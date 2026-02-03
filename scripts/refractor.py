"""Automated refractor pipeline using Claude CLI.

Runs multiple Claude CLI sessions sequentially, each performing a specific
code review or refractor task. Each session runs non-interactively with
--dangerously-skip-permissions.

Before running, creates a local git checkpoint commit for easy rollback.

Pipeline operates in multiple passes (max 3), each pass containing two phases:

Phase 1 - Iterative Roast Loop (max 10 iterations per pass):
    - Run roast analysis (step 0) with severity classification (SEVERE/MEDIUM/MINOR)
    - Fix ALL issues automatically, sorted by severity (SEVERE → MEDIUM → MINOR)
    - Commit fixes and repeat until no issues remain

Phase 2 - Project-Wide Steps:
    1. Data Architecture Enforcement
    2. Architecture Review (per python_clean_architecture.md)
    3. LRU Cache Opportunities
    4. Proper Usage of Libraries
    5. Edge Cases, Race Conditions & Security
    6. Test Refractor
    7. Code Simplification
    8. Documentation Review

After project-wide steps, a final roast checks for new issues. If found,
the pipeline starts the next pass (up to 3 total passes).
"""

from __future__ import annotations

import re
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import click
import orjson


@dataclass
class OutputContext:
    """Context for structured output formatting."""

    step_name: str
    phase: str
    pass_number: int | None = None


def _format_output_prefix(ctx: OutputContext | None) -> str:
    """Generate structured output prefix like [hh:mm:ss][Step][Phase][Pass].

    Args:
        ctx: Output context with step name, phase, and optional pass number.
             If None, returns only timestamp.

    Returns:
        Formatted prefix string like "[14:32:15][Data Architecture][Phase1.1]".
    """
    timestamp = datetime.now().strftime("%H:%M:%S")

    if ctx is None:
        return f"[{timestamp}]"

    parts = [timestamp, ctx.step_name, ctx.phase]
    if ctx.pass_number is not None:
        parts.append(f"Pass{ctx.pass_number}")

    return "".join(f"[{part}]" for part in parts)


def _get_phase_name(step_idx: int) -> str:
    """Map step index to phase name.

    Args:
        step_idx: Step index (0-8).

    Returns:
        Phase name like "Phase1.1", "Phase2", etc.
    """
    if 1 <= step_idx <= 7:
        return f"Phase1.{step_idx}"
    elif step_idx == 0:
        return "Phase2"
    elif step_idx == 8:
        return "Phase3"
    return f"Step{step_idx}"


# Maximum test fix attempts to prevent infinite loops
_MAX_TEST_FIX_ATTEMPTS = 5


def _run_tests(output_ctx: OutputContext | None = None) -> tuple[int, str]:
    """Run unit tests using make test.

    Args:
        output_ctx: Output context for structured prefix formatting.

    Returns:
        Tuple of (return_code, output_text).
    """
    prefix = _format_output_prefix(output_ctx)
    click.echo(f"{prefix} : Running unit tests (make test)...")

    result = subprocess.run(
        ["make", "test"],
        capture_output=True,
        text=True,
        check=False,
    )

    output = result.stdout + result.stderr
    if result.returncode == 0:
        click.echo(f"{prefix} : ✓ All unit tests passed")
    else:
        click.echo(f"{prefix} : ✗ Unit tests failed (exit code {result.returncode})")

    return result.returncode, output


def _run_integration_tests(output_ctx: OutputContext | None = None) -> tuple[int, str]:
    """Run integration tests using make test-slow.

    Args:
        output_ctx: Output context for structured prefix formatting.

    Returns:
        Tuple of (return_code, output_text).
    """
    prefix = _format_output_prefix(output_ctx)
    click.echo(f"{prefix} : Running integration tests (make test-slow)...")

    result = subprocess.run(
        ["make", "test-slow"],
        capture_output=True,
        text=True,
        check=False,
    )

    output = result.stdout + result.stderr
    if result.returncode == 0:
        click.echo(f"{prefix} : ✓ All integration tests passed")
    else:
        click.echo(f"{prefix} : ✗ Integration tests failed (exit code {result.returncode})")

    return result.returncode, output


def _fix_test_errors(
    test_output: str,
    test_type: str,
    output_ctx: OutputContext | None = None,
) -> int:
    """Use Claude to fix test errors.

    Args:
        test_output: The failing test output.
        test_type: Type of tests ("unit" or "integration").
        output_ctx: Output context for structured prefix formatting.

    Returns:
        Exit code (0 for success).
    """
    prefix = _format_output_prefix(output_ctx)
    click.echo(f"{prefix} : Attempting to fix {test_type} test errors...")

    # Truncate output if too long (keep last 8000 chars which has the errors)
    if len(test_output) > 10000:
        test_output = "...[truncated]...\n" + test_output[-8000:]

    fix_prompt = f"""The {test_type} tests are failing. Please analyze the error output and fix the issues.

TEST OUTPUT:
```
{test_output}
```

Fix the failing tests by:
1. Analyzing the error messages to understand what's broken
2. Making the necessary code changes to fix the issues
3. Do NOT just delete or skip tests - fix the actual problems
4. If a test is testing removed functionality, update the test appropriately

After fixing, verify your changes are correct."""

    # Create a fix-specific context
    fix_ctx = OutputContext(
        step_name=f"Fix {test_type.title()} Tests",
        phase=output_ctx.phase if output_ctx else "TestFix",
        pass_number=output_ctx.pass_number if output_ctx else None,
    )

    return_code, _ = _run_claude_session(fix_prompt, output_ctx=fix_ctx)
    return return_code


# Test mode options: "unit" (make test), "integration" (make test-slow), "both"
TestMode = str  # Literal["unit", "integration", "both"]


def _run_and_fix_tests(
    output_ctx: OutputContext | None = None,
    *,
    test_mode: TestMode = "integration",
) -> int:
    """Run tests and fix any errors, with retry loop.

    Args:
        output_ctx: Output context for structured prefix formatting.
        test_mode: Which tests to run - "unit", "integration", or "both".
                   Default is "integration" since steps typically run unit tests themselves.

    Returns:
        Exit code (0 for success, non-zero if tests still fail after max attempts).
    """
    prefix = _format_output_prefix(output_ctx)
    run_unit = test_mode in ("unit", "both")
    run_integration = test_mode in ("integration", "both")

    # Run and fix unit tests if requested
    if run_unit:
        for attempt in range(1, _MAX_TEST_FIX_ATTEMPTS + 1):
            return_code, test_output = _run_tests(output_ctx)
            if return_code == 0:
                break

            click.echo(f"{prefix} : Test fix attempt {attempt}/{_MAX_TEST_FIX_ATTEMPTS}")
            fix_result = _fix_test_errors(test_output, "unit", output_ctx)
            if fix_result != 0:
                click.echo(f"{prefix} : ✗ Failed to fix unit tests")
                return fix_result
        else:
            click.echo(f"{prefix} : ✗ Unit tests still failing after {_MAX_TEST_FIX_ATTEMPTS} attempts")
            return 1

    # Run and fix integration tests if requested
    if run_integration:
        for attempt in range(1, _MAX_TEST_FIX_ATTEMPTS + 1):
            return_code, test_output = _run_integration_tests(output_ctx)
            if return_code == 0:
                break

            click.echo(f"{prefix} : Integration test fix attempt {attempt}/{_MAX_TEST_FIX_ATTEMPTS}")
            fix_result = _fix_test_errors(test_output, "integration", output_ctx)
            if fix_result != 0:
                click.echo(f"{prefix} : ✗ Failed to fix integration tests")
                return fix_result
        else:
            click.echo(f"{prefix} : ✗ Integration tests still failing after {_MAX_TEST_FIX_ATTEMPTS} attempts")
            return 1

    return 0


# Pre-compiled regex for parsing issue headers and severity
_ISSUE_HEADER_PATTERN = re.compile(r"^## Issue \d+:\s*(.+)$", re.MULTILINE)
_SEVERITY_PATTERN = re.compile(r"\*\*Severity\*\*:\s*(SEVERE|MEDIUM|MINOR)", re.IGNORECASE)

# Standard suffix for fix prompts
_FIX_SUFFIX = (
    "Do not create compatibility shims, we don't care for backward compatibility. "
    "Write tests for any new code you create - aim for good test coverage. "
    "Make sure that all tests are still passing. "
    "After that, update all documentation, claude.md and module_reference.md, "
    "only document the current state, no old or outdated, transitive, refractured or legacy issues or code. "
    "update the changelog (important points only) in section [unreleased] "
    "(create that section if not present), in the appropriate category "
    "(like Fixed, Changed, Added, etc.)."
)

# Directory for saving roast output files
ROAST_OUTPUT_DIR = Path(tempfile.gettempdir()) / "RISscraper_refractor"

# Maximum roast iterations per pipeline pass to prevent infinite loops
_MAX_ROAST_ITERATIONS = 10

# Maximum full pipeline passes (roast loop + project-wide steps)
_MAX_PIPELINE_PASSES = 3

__all__ = ["run_refractor_pipeline"]


def _get_version() -> str:
    """Get current version from __init__conf__.py."""
    conf_path = Path(__file__).parent.parent / "src" / "RISscraper" / "__init__conf__.py"
    content = conf_path.read_text()
    for line in content.splitlines():
        if line.startswith("version = "):
            return line.split('"')[1]
    return "unknown"


def _create_pre_refractor_commit() -> bool:
    """Create a local git checkpoint commit before refractor.

    Returns:
        True if commit was created, False if nothing to commit or error.
    """
    version = _get_version()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"pre-refractor {version} {timestamp}"

    click.echo()
    click.echo("=" * 60)
    click.echo("=== Creating pre-refractor checkpoint ===")
    click.echo("=" * 60)
    click.echo()

    # Stage all changes
    result = subprocess.run(["git", "add", "-A"], check=False, capture_output=True, text=True)
    if result.returncode != 0:
        click.echo(f"Warning: git add failed: {result.stderr}", err=True)
        return False

    # Check if there are changes to commit
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], check=False)
    if result.returncode == 0:
        click.echo("No changes to commit, skipping checkpoint")
        return False

    # Create commit
    result = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        click.echo(f"Warning: git commit failed: {result.stderr}", err=True)
        return False

    click.echo(f"✓ Created checkpoint: {commit_msg}")
    return True


def _run_claude_session(
    prompt: str,
    *,
    capture_output: bool = False,
    output_ctx: OutputContext | None = None,
) -> tuple[int, str]:
    """Run Claude CLI session with real-time output display.

    Args:
        prompt: The prompt to send to Claude.
        capture_output: If True, also capture text output for later use.
        output_ctx: Output context for structured prefix formatting.

    Returns:
        Tuple of (return_code, captured_text). captured_text is empty if
        capture_output is False.
    """
    cmd = [
        "claude",
        "--dangerously-skip-permissions",
        "--verbose",
        "--output-format",
        "stream-json",
        "-p",
        prompt,
    ]

    captured_lines: list[str] = []

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    if process.stdout:
        for raw_line in process.stdout:
            stripped = raw_line.strip()
            if not stripped:
                continue

            # Skip or strip "stdout > " and "stdout: " prefixes from Claude CLI
            if stripped.startswith("stdout > "):
                stripped = stripped[9:]  # Strip "stdout > " prefix
                if not stripped:
                    continue
            elif stripped.startswith("stdout: "):
                stripped = stripped[8:]  # Strip "stdout: " prefix
                if not stripped:
                    continue

            try:
                data = orjson.loads(stripped)
                if data.get("type") == "assistant":
                    msg = data.get("message", {})
                    content = msg.get("content", [])
                    for item in content:
                        if item.get("type") == "text":
                            text = item.get("text", "")
                            if text:
                                prefix = _format_output_prefix(output_ctx)
                                click.echo(f"{prefix} : {text}")
                                if capture_output:
                                    captured_lines.append(text)
                elif data.get("type") == "content_block_start":
                    block = data.get("content_block", {})
                    if block.get("type") == "tool_use":
                        prefix = _format_output_prefix(output_ctx)
                        tool_msg = f"[Tool: {block.get('name', 'unknown')}]"
                        click.echo(f"{prefix} : {tool_msg}")
                        if capture_output:
                            captured_lines.append(tool_msg)
                elif data.get("type") == "result":
                    result_text = data.get("result", "")
                    if result_text:
                        prefix = _format_output_prefix(output_ctx)
                        click.echo(f"{prefix} : {result_text}")
                        if capture_output:
                            captured_lines.append(result_text)
            except orjson.JSONDecodeError:
                # Skip lines that are just "stdout" markers without content
                if stripped.lower() in ("stdout", "stderr"):
                    continue
                prefix = _format_output_prefix(output_ctx)
                click.echo(f"{prefix} : {stripped}")
                if capture_output:
                    captured_lines.append(stripped)

    process.wait()

    captured_text = "\n".join(captured_lines) if capture_output else ""
    return process.returncode, captured_text


def _save_roast_output(roast_text: str) -> Path:
    """Save roast output to a timestamped markdown file.

    Args:
        roast_text: The captured roast analysis text.

    Returns:
        Path to the saved roast file.
    """
    ROAST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"roast_{timestamp}.md"
    filepath = ROAST_OUTPUT_DIR / filename

    filepath.write_text(roast_text, encoding="utf-8")
    return filepath


def _parse_roast_into_chunks(roast_text: str) -> list[tuple[str, str, str]]:
    """Parse roast output into (title, content, severity) chunks.

    Args:
        roast_text: Full roast output from step 0.

    Returns:
        List of (title, chunk_content, severity) tuples.
        Severity is one of: "SEVERE", "MEDIUM", "MINOR", or "UNKNOWN".
    """
    chunks: list[tuple[str, str, str]] = []
    # Split by ## Issue N: headers
    parts = re.split(r"(## Issue \d+:\s*.+)", roast_text)

    # parts alternates: [preamble, header1, content1, header2, content2, ...]
    for i in range(1, len(parts), 2):
        header = parts[i].strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        # Extract title from "## Issue N: Title"
        match = _ISSUE_HEADER_PATTERN.match(header)
        title = match.group(1) if match else header
        full_chunk = f"{header}\n\n{content}"

        # Extract severity from content
        severity_match = _SEVERITY_PATTERN.search(content)
        severity = severity_match.group(1).upper() if severity_match else "UNKNOWN"

        chunks.append((title, full_chunk, severity))

    return chunks


def _display_chunks_by_severity(
    chunks: list[tuple[str, str, str]],
) -> tuple[list[int], list[int], list[int]]:
    """Display chunks grouped by severity and return indices.

    Returns:
        Tuple of (severe_indices, medium_indices, minor_indices).
    """
    severe_indices: list[int] = []
    medium_indices: list[int] = []
    minor_indices: list[int] = []

    for i, (_title, _, severity) in enumerate(chunks):
        if severity == "SEVERE":
            severe_indices.append(i)
        elif severity == "MEDIUM":
            medium_indices.append(i)
        else:  # MINOR or UNKNOWN
            minor_indices.append(i)

    click.echo("\nDetected issues by severity:")

    if severe_indices:
        click.echo("\n  SEVERE:")
        for idx in severe_indices:
            click.echo(f"    {idx + 1}. {chunks[idx][0]}")

    if medium_indices:
        click.echo("\n  MEDIUM:")
        for idx in medium_indices:
            click.echo(f"    {idx + 1}. {chunks[idx][0]}")

    if minor_indices:
        click.echo("\n  MINOR:")
        for idx in minor_indices:
            click.echo(f"    {idx + 1}. {chunks[idx][0]}")

    return severe_indices, medium_indices, minor_indices


def _create_chunk_checkpoint(chunk_idx: int, chunk_title: str) -> bool:
    """Create git checkpoint before processing a chunk.

    Commit message: "pre-chunk-{idx}: {title}"

    Args:
        chunk_idx: 0-based index of the chunk.
        chunk_title: Short title for the chunk.

    Returns:
        True if commit was created, False if nothing to commit.
    """
    # Sanitize title for commit message
    safe_title = chunk_title[:50].replace('"', "'")
    commit_msg = f"pre-chunk-{chunk_idx + 1}: {safe_title}"

    # Stage and commit
    subprocess.run(["git", "add", "-A"], check=False, capture_output=True)
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], check=False)
    if result.returncode == 0:
        return False  # Nothing to commit

    subprocess.run(
        ["git", "commit", "-m", commit_msg],
        check=False,
        capture_output=True,
    )
    click.echo(f"✓ Checkpoint: {commit_msg}")
    return True


def _create_iteration_checkpoint(label: int | str) -> bool:
    """Create git checkpoint after completing all fixes in an iteration.

    Commit message: "refractor-{label}-complete"

    Args:
        label: Iteration number or descriptive label for the checkpoint.

    Returns:
        True if commit was created, False if nothing to commit.
    """
    commit_msg = f"refractor-{label}-complete"

    # Stage and commit all changes
    subprocess.run(["git", "add", "-A"], check=False, capture_output=True)
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], check=False)
    if result.returncode == 0:
        click.echo("No changes to commit after fixes.")
        return False

    subprocess.run(
        ["git", "commit", "-m", commit_msg],
        check=False,
        capture_output=True,
    )
    click.echo(f"✓ Committed: {commit_msg}")
    return True


def _run_chunk_fix_session(
    chunk_content: str,
    chunk_title: str,
    output_ctx: OutputContext | None = None,
) -> int:
    """Run a single fix session for an issue chunk.

    Applies the suggested fix from the roast output with standard suffix.

    Args:
        chunk_content: The full chunk text (header + description + suggested fix).
        chunk_title: Short title for display.
        output_ctx: Output context for structured prefix formatting.

    Returns:
        Exit code (0 for success).
    """
    click.echo(f"\n{'=' * 60}")
    click.echo(f"=== Fixing: {chunk_title} ===")
    click.echo(f"{'=' * 60}")

    # Create fix prompt from the chunk's suggested fix
    fix_prompt = f"Apply the suggested fix for this issue:\n\n{chunk_content}\n\n---\n\n{_FIX_SUFFIX}"

    return_code, _ = _run_claude_session(fix_prompt, output_ctx=output_ctx)
    if return_code != 0:
        click.echo(f"✗ Fix failed for: {chunk_title}")
        return return_code

    click.echo(f"\n✓ Fixed: {chunk_title}")
    return 0


# Define the refractor steps as (title, prompt) tuples
# Step 0 is interactive (requires confirmation), steps 1-8 are automated
REFRACTOR_STEPS: list[tuple[str, str]] = [
    (
        "Project Analysis (Roast)",
        """analyze the whole project. is it any good? roast me!

IMPORTANT: Format your findings as separate issues with clear headers and severity:

## Issue 1: [Short Title]
**Severity**: SEVERE | MEDIUM | MINOR
**Affected files**: [list of files]
**Description**: [what's wrong]
**Suggested fix**: [specific actionable fix instructions]

## Issue 2: [Short Title]
**Severity**: SEVERE | MEDIUM | MINOR
**Affected files**: [list of files]
**Description**: [what's wrong]
**Suggested fix**: [specific actionable fix instructions]

Severity guidelines:
- SEVERE: Security issues, data loss risks, critical bugs, architectural violations
- MEDIUM: Performance issues, code quality problems, missing tests, unclear code, documentation gaps, nice-to-haves
- MINOR: Pure style issues (formatting, naming conventions that don't affect readability)

Continue numbering for all issues found. Each issue MUST have a specific, actionable suggested fix.""",
    ),
    (
        "Data Architecture Enforcement",
        "run the slash command /bx_data_architecture_enforcement. "
        "do not create compatibility shims, we dont care for backward compatibility. "
        "write tests for any new code you create - aim for good test coverage. "
        "dont ask back - decide yourself given all the systemprompts in claude.md. "
        "make sure that all tests are still passing. "
        "after that, update all documentation, claude.md and module_reference.md, "
        "and update the changelog in section [unreleased]",
    ),
    (
        "Architecture Review",
        "review architecture like described in python_clean_architecture.md. "
        "do not create compatibility shims, we dont care for backward compatibility. "
        "write tests for any new code you create - aim for good test coverage. "
        "dont ask back - decide yourself given all the systemprompts in claude.md. "
        "make sure that all tests are still passing. "
        "after that, update all documentation, claude.md and module_reference.md, "
        "and update the changelog in section [unreleased]",
    ),
    (
        "LRU Cache Opportunities",
        "look for lru_cache opportunities - profile with both unit tests and integration tests "
        "(make test-slow) if the caches are really helpful. "
        "make sure that all regex expressions are precompiled. "
        "do not create compatibility shims, we dont care for backward compatibility. "
        "write tests for any new code you create - aim for good test coverage. "
        "dont ask back - decide yourself given all the systemprompts in claude.md. "
        "make sure that all tests are still passing. "
        "after that update all documentation, claude.md and module_reference.md, "
        "and update the changelog in section [unreleased]",
    ),
    (
        "Proper Usage of Libraries",
        "make sure that we use orjson, rtoml instead of stdlib. "
        "make sure that we use httpx if applicable. "
        "do not create compatibility shims, we dont care for backward compatibility. "
        "write tests for any new code you create - aim for good test coverage. "
        "dont ask back - decide yourself given all the systemprompts in claude.md. "
        "make sure that all tests are still passing. "
        "after that update all documentation, claude.md and module_reference.md, "
        "and update the changelog in section [unreleased]",
    ),
    (
        "Edge Cases, Race Conditions & Security",
        "review the whole code and look for edge cases, race conditions and security issues. "
        "do not create compatibility shims, we dont care for backward compatibility. "
        "write tests for any new code you create - aim for good test coverage. "
        "dont ask back - decide yourself given all the systemprompts in claude.md. "
        "make sure that all tests are still passing. "
        "after that, update all documentation, claude.md and module_reference.md, "
        "and update the changelog in section [unreleased]",
    ),
    (
        "Test Refractor",
        "run the slash command /bx_refactor_tests_python. "
        "do not create compatibility shims, we dont care for backward compatibility. "
        "write tests for any new code you create - aim for good test coverage. "
        "dont ask back - decide yourself given all the systemprompts in claude.md. "
        "make sure that all tests are still passing. "
        "after that, update all documentation, claude.md and module_reference.md, "
        "and update the changelog in section [unreleased]",
    ),
    (
        "Code Simplification",
        "review and simplify code without breaking architecture. "
        "remove compatibility shims, legacy code, dead code, "
        "but keep compatibility to the oldest python version specified in pyproject.toml. "
        "modernize the code, according to the oldest python version specified in pyproject.toml. "
        "write tests for any new code you create - aim for good test coverage. "
        "dont ask back - decide yourself given all the systemprompts in claude.md. "
        "make sure that all tests are still passing. "
        "after that, update all documentation, claude.md and module_reference.md, "
        "and update the changelog in section [unreleased]",
    ),
    (
        "Documentation Review",
        "review and check all documentation, claude.md and module_reference.md for correctness and completeness. "
        "make sure the complete API and cli is explained. "
        "all options, flags, default values are accurate and explained. "
        "all cli commands including options are accurate and explained. "
        "only document the current state, no old or outdated, transitive, refractured or legacy issues or code. "
        "dont ask back - decide yourself given all the systemprompts in claude.md.",
    ),
]


def _run_roast_step(output_ctx: OutputContext | None = None) -> tuple[int, str]:
    """Run the roast step (step 0) and capture output.

    Args:
        output_ctx: Output context for structured prefix formatting.

    Returns:
        Tuple of (return_code, captured_text).
    """
    title, prompt = REFRACTOR_STEPS[0]

    click.echo()
    click.echo(f"{'=' * 60}")
    click.echo(f"=== Step 0: {title} ===")
    click.echo(f"{'=' * 60}")
    click.echo()
    click.echo("Running Claude CLI...")
    click.echo("-" * 60)

    return_code, captured_text = _run_claude_session(
        prompt,
        capture_output=True,
        output_ctx=output_ctx,
    )

    click.echo()
    click.echo("-" * 60)

    if return_code != 0:
        click.echo(f"\n✗ Roast step failed with exit code {return_code}", err=True)
    else:
        click.echo("\n✓ Roast step completed successfully")

    return return_code, captured_text


def _create_step_checkpoint(step_idx: int, step_title: str) -> bool:
    """Create git checkpoint after completing a project-wide step.

    Commit message: "refractor-step-{idx}: {title}"

    Args:
        step_idx: Step number (1-8).
        step_title: Short title for the step.

    Returns:
        True if commit was created, False if nothing to commit.
    """
    # Sanitize title for commit message
    safe_title = step_title[:40].replace('"', "'")
    commit_msg = f"refractor-step-{step_idx}: {safe_title}"

    # Stage and commit all changes
    subprocess.run(["git", "add", "-A"], check=False, capture_output=True)
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], check=False)
    if result.returncode == 0:
        click.echo("No changes to commit after this step.")
        return False

    subprocess.run(
        ["git", "commit", "-m", commit_msg],
        check=False,
        capture_output=True,
    )
    click.echo(f"✓ Committed: {commit_msg}")
    return True


def _run_project_wide_steps(
    step_indices: list[int] | None = None,
    *,
    test_mode: TestMode = "integration",
) -> int:
    """Run project-wide steps.

    Creates a git commit after each step so Claude can see incremental changes.
    Runs tests after each step and fixes any errors.

    Args:
        step_indices: List of step indices to run (1-8). If None, runs all (1-8).
        test_mode: Which tests to run after each step - "unit", "integration", or "both".

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    if step_indices is None:
        step_indices = list(range(1, 9))  # Steps 1-8

    total_steps = len(REFRACTOR_STEPS) - 1  # Exclude step 0 (roast)

    click.echo()
    click.echo("=" * 60)
    click.echo(f"=== Running Project-Wide Steps: {step_indices} ===")
    click.echo("=" * 60)

    for step_idx in step_indices:
        if step_idx < 1 or step_idx >= len(REFRACTOR_STEPS):
            click.echo(f"Warning: Skipping invalid step index {step_idx}", err=True)
            continue

        step_title, step_prompt = REFRACTOR_STEPS[step_idx]

        # Create output context for this step
        phase = _get_phase_name(step_idx)
        ctx = OutputContext(
            step_name=step_title,
            phase=phase,
            pass_number=None,
        )

        click.echo()
        click.echo(f"{'=' * 60}")
        click.echo(f"=== Step {step_idx}/{total_steps}: {step_title} ===")
        click.echo(f"{'=' * 60}")
        click.echo()
        click.echo("Running Claude CLI...")
        click.echo("-" * 60)

        return_code, _ = _run_claude_session(step_prompt, output_ctx=ctx)

        click.echo()
        click.echo("-" * 60)

        if return_code != 0:
            click.echo(f"\n✗ Step {step_idx} ({step_title}) failed", err=True)
            return return_code

        click.echo(f"\n✓ Step {step_idx} ({step_title}) completed")

        # Run tests and fix any errors
        test_result = _run_and_fix_tests(ctx, test_mode=test_mode)
        if test_result != 0:
            click.echo(f"\n✗ Tests failed after step {step_idx} ({step_title})", err=True)
            return test_result

        # Commit after each step so Claude sees incremental changes
        _create_step_checkpoint(step_idx, step_title)

    return 0


def _run_selected_steps(  # noqa: PLR0911
    steps: list[int],
    auto_fix: bool,
    *,
    test_mode: TestMode = "integration",
) -> int:
    """Run only the selected steps.

    Args:
        steps: List of step numbers to run (0-8).
        auto_fix: Whether to auto-fix issues in step 0.
        test_mode: Which tests to run after each step - "unit", "integration", or "both".

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    total_steps = len(REFRACTOR_STEPS)
    max_step = total_steps - 1

    # Validate and sort steps
    valid_steps = sorted({s for s in steps if 0 <= s <= max_step})
    if not valid_steps:
        click.echo(f"Error: No valid steps provided. Steps must be between 0 and {max_step}", err=True)
        return 1

    invalid_steps = [s for s in steps if s < 0 or s > max_step]
    if invalid_steps:
        click.echo(f"Warning: Ignoring invalid steps: {invalid_steps}", err=True)

    click.echo(f"\nRunning selected steps: {valid_steps}")

    for step in valid_steps:
        title, prompt = REFRACTOR_STEPS[step]

        # Create output context for this step
        phase = _get_phase_name(step)
        ctx = OutputContext(
            step_name=title,
            phase=phase,
            pass_number=None,
        )

        click.echo()
        click.echo(f"{'=' * 60}")
        click.echo(f"=== Step {step}/{max_step}: {title} ===")
        click.echo(f"{'=' * 60}")
        click.echo()
        click.echo("Running Claude CLI...")
        click.echo("-" * 60)

        # Step 0 (roast) needs special handling if auto_fix is enabled
        if step == 0 and auto_fix:
            # Run roast and auto-fix loop
            roast_ctx = OutputContext(
                step_name="Roast Analysis",
                phase="Phase2",
                pass_number=1,
            )
            return_code, roast_text = _run_roast_step(output_ctx=roast_ctx)
            if return_code != 0:
                return return_code

            chunks = _parse_roast_into_chunks(roast_text)
            if chunks:
                severe_indices, medium_indices, minor_indices = _display_chunks_by_severity(chunks)
                unknown_indices = [i for i, (_, _, severity) in enumerate(chunks) if severity == "UNKNOWN"]
                all_indices = severe_indices + medium_indices + unknown_indices + minor_indices

                click.echo(f"\n[Auto-fix mode] Fixing {len(all_indices)} issue(s)...")
                for chunk_idx in all_indices:
                    chunk_title, chunk_content, severity = chunks[chunk_idx]
                    _create_chunk_checkpoint(chunk_idx, f"[{severity}] {chunk_title}")

                    fix_ctx = OutputContext(
                        step_name=f"Fix: {chunk_title[:30]}",
                        phase="Phase2",
                        pass_number=1,
                    )
                    result = _run_chunk_fix_session(
                        chunk_content,
                        f"[{severity}] {chunk_title}",
                        output_ctx=fix_ctx,
                    )
                    if result != 0:
                        return result

                    # Run tests after each chunk fix
                    test_result = _run_and_fix_tests(fix_ctx, test_mode=test_mode)
                    if test_result != 0:
                        click.echo(f"\n✗ Tests failed after fixing: {chunk_title}", err=True)
                        return test_result

                _create_iteration_checkpoint("roast-fixes")
        else:
            return_code, _ = _run_claude_session(
                prompt,
                capture_output=(step == 0),
                output_ctx=ctx,
            )

            click.echo()
            click.echo("-" * 60)

            if return_code != 0:
                click.echo(f"\n✗ Step {step} ({title}) failed", err=True)
                return return_code

            click.echo(f"\n✓ Step {step} ({title}) completed")

            # Run tests after step
            test_result = _run_and_fix_tests(ctx, test_mode=test_mode)
            if test_result != 0:
                click.echo(f"\n✗ Tests failed after step {step} ({title})", err=True)
                return test_result

        # Commit after each step
        _create_step_checkpoint(step, title)

    click.echo()
    click.echo("=" * 60)
    click.echo("=== Selected steps completed ===")
    click.echo("=" * 60)
    return 0


def run_refractor_pipeline(  # noqa: PLR0911
    *,
    steps: list[int] | None = None,
    auto_fix: bool = False,
    max_roast_iterations: int | None = None,
    max_pipeline_passes: int | None = None,  # Kept for CLI compatibility, ignored
    test_mode: TestMode = "integration",
) -> int:
    """Run the automated refractor pipeline.

    The pipeline operates in three phases:

    Phase 1 - Project-Wide Steps 1-7 (once):
        1. Data Architecture Enforcement
        2. Architecture Review
        3. LRU Cache Opportunities
        4. Proper Usage of Libraries
        5. Edge Cases, Race Conditions & Security
        6. Test Refractor
        7. Code Simplification

    Phase 2 - Roast Loop (iterative):
        1. Run roast analysis (step 0) with severity classification
        2. Fix ALL issues sorted by severity (SEVERE → MEDIUM → MINOR)
        3. Repeat until no issues remain or max iterations reached

    Phase 3 - Documentation Review (once):
        8. Documentation Review

    Args:
        steps: List of specific steps to run (0-8). If None or empty, run full pipeline.
               Step 0 is the roast/analysis step.
               Steps 1-7 are project-wide refactoring steps.
               Step 8 is documentation review.
        auto_fix: If True, automatically fix all issues without
              prompting. Useful for unattended/CI runs.
        max_roast_iterations: Maximum roast iterations. Default: 10.
        max_pipeline_passes: Deprecated, kept for CLI compatibility.
        test_mode: Which tests to run after each step - "unit", "integration", or "both".
              Default is "integration" since steps typically run unit tests themselves.

    Returns:
        Exit code (0 for success, non-zero on failure).
    """
    # Use defaults if not specified
    roast_limit = max_roast_iterations if max_roast_iterations is not None else _MAX_ROAST_ITERATIONS

    # Clamp to reasonable range
    roast_limit = max(1, min(20, roast_limit))

    # Create checkpoint commit before refractor
    _create_pre_refractor_commit()

    # Handle selected steps mode (run only specific steps)
    if steps:
        return _run_selected_steps(steps, auto_fix, test_mode=test_mode)

    # --- Full Pipeline: Steps 1-7 → Roast Loop → Step 8 (Docs) ---

    click.echo("\nPipeline flow: Steps 1-7 → Roast Loop → Step 8 (Docs)")
    click.echo(f"Roast config: max {roast_limit} iterations")

    # === Phase 1: Run Steps 1-7 (once) ===
    click.echo()
    click.echo("@" * 60)
    click.echo("@@@ PHASE 1: PROJECT-WIDE STEPS 1-7 @@@")
    click.echo("@" * 60)

    result = _run_project_wide_steps([1, 2, 3, 4, 5, 6, 7], test_mode=test_mode)
    if result != 0:
        return result

    _create_iteration_checkpoint("phase1-steps-1-7")

    # === Phase 2: Roast Loop ===
    click.echo()
    click.echo("@" * 60)
    click.echo("@@@ PHASE 2: ROAST LOOP @@@")
    click.echo("@" * 60)

    iteration = 0

    while iteration < roast_limit:
        iteration += 1
        click.echo()
        click.echo("#" * 60)
        click.echo(f"### ROAST ITERATION {iteration}/{roast_limit} ###")
        click.echo("#" * 60)

        # Create output context for this roast iteration
        roast_ctx = OutputContext(
            step_name="Roast Analysis",
            phase="Phase2",
            pass_number=iteration,
        )

        # Run a fresh roast analysis
        click.echo("\nRunning fresh roast analysis on current codebase...")
        return_code, roast_text = _run_roast_step(output_ctx=roast_ctx)
        if return_code != 0:
            return return_code

        # Save roast output
        roast_file = _save_roast_output(roast_text)
        click.echo(f"\nRoast analysis saved to: {roast_file}")

        # Parse into chunks with severity
        chunks = _parse_roast_into_chunks(roast_text)

        if not chunks:
            click.echo("No structured issues found in roast output.")
            click.echo("✓ Codebase is clean! Proceeding to documentation step...")
            break

        # Display issues by severity
        severe_indices, medium_indices, minor_indices = _display_chunks_by_severity(chunks)

        # Process ALL issues, sorted by severity (SEVERE → MEDIUM → MINOR)
        # UNKNOWN severity is treated as MEDIUM (inserted between MEDIUM and MINOR)
        unknown_indices = [i for i, (_, _, severity) in enumerate(chunks) if severity == "UNKNOWN"]
        all_indices = severe_indices + medium_indices + unknown_indices + minor_indices

        click.echo(f"\nSummary: {len(severe_indices)} SEVERE, {len(medium_indices)} MEDIUM, {len(minor_indices)} MINOR")

        click.echo(f"\n{len(all_indices)} issue(s) to fix.")

        # Auto-fix mode: skip prompt and fix automatically
        if auto_fix:
            click.echo("\n[Auto-fix mode] Fixing all issues...")
            choice = "fix"
        else:
            # Ask user to confirm fixing issues
            click.echo("\nOptions:")
            click.echo("  fix      - Fix all issues (SEVERE → MEDIUM → MINOR), then re-roast")
            click.echo("  continue - Skip to documentation step")
            click.echo("  abort    - Cancel the pipeline")

            choice = click.prompt(
                "What would you like to do?",
                type=click.Choice(["fix", "continue", "abort"], case_sensitive=False),
                default="fix",
                show_choices=True,
            )

            if choice == "abort":
                click.echo("Refactoring cancelled by user.")
                return 0
            elif choice == "continue":
                click.echo("Skipping to documentation step...")
                break

        # Fix all issues (sorted by severity)
        click.echo(f"\n=== Fixing {len(all_indices)} issue(s) ===")

        for chunk_idx in all_indices:
            chunk_title, chunk_content, severity = chunks[chunk_idx]

            # Git checkpoint before this chunk
            _create_chunk_checkpoint(chunk_idx, f"[{severity}] {chunk_title}")

            # Create output context for this fix
            fix_ctx = OutputContext(
                step_name=f"Fix: {chunk_title[:30]}",
                phase="Phase2",
                pass_number=iteration,
            )

            # Fix this chunk
            result = _run_chunk_fix_session(
                chunk_content,
                f"[{severity}] {chunk_title}",
                output_ctx=fix_ctx,
            )
            if result != 0:
                return result

            # Run tests after each chunk fix
            test_result = _run_and_fix_tests(fix_ctx, test_mode=test_mode)
            if test_result != 0:
                click.echo(f"\n✗ Tests failed after fixing: {chunk_title}", err=True)
                return test_result

        click.echo("\n✓ All issues fixed.")

        # Commit all fixes before re-roasting so Claude sees the changes
        _create_iteration_checkpoint(f"roast-{iteration}")
        click.echo("\nRe-running roast to check for remaining issues...")
    else:
        # Max iterations reached
        click.echo()
        click.echo("=" * 60)
        click.echo(f"⚠ Maximum roast iterations ({roast_limit}) reached.")
        click.echo("Some issues may remain. Proceeding to documentation step...")
        click.echo("=" * 60)

    # === Phase 3: Documentation Step (Step 8) ===
    click.echo()
    click.echo("@" * 60)
    click.echo("@@@ PHASE 3: DOCUMENTATION REVIEW (Step 8) @@@")
    click.echo("@" * 60)

    result = _run_project_wide_steps([8], test_mode=test_mode)
    if result != 0:
        return result

    _create_iteration_checkpoint("phase3-docs")

    click.echo()
    click.echo("=" * 60)
    click.echo("=== Refractor pipeline complete ===")
    click.echo("=" * 60)

    return 0


def main() -> None:
    """Entry point for direct script execution."""
    raise SystemExit(run_refractor_pipeline())


if __name__ == "__main__":
    main()
