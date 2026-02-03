"""Test step execution, parallel orchestration, and display helpers.

Purpose
-------
Provide the building blocks for running linting / type-checking / security
steps both sequentially and in parallel. All command execution flows through
``make_run_command`` which binds a shared ``default_env`` dict, eliminating
the global mutable state that previously lived in ``test.py``.

Contents
--------
* ``StepResult`` / ``TestSteps`` / ``ParallelStep`` -- step metadata.
* ``make_run_command`` -- factory returning a ``_run_command`` closure bound
  to a specific environment dict.
* ``_make_step`` / ``_make_run_fn`` -- convenience wrappers.
* ``run_step_subprocess`` / ``run_parallel_steps_subprocess`` -- thread-pool
  parallel execution.
* Display helpers for command echoing, result reporting, and output capture.

System Role
-----------
Called from the test orchestrator (``test.py``) to execute individual build
steps and render their results.
"""

from __future__ import annotations

import os
import threading
import time
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

import click

from ._utils import RunResult, run

__all__ = [
    "StepResult",
    "TestSteps",
    "ParallelStep",
    "make_run_command",
    "make_step",
    "make_run_fn",
    "run_step_subprocess",
    "run_parallel_steps_subprocess",
    "display_parallel_results",
    "build_test_steps",
]

# Thread-safe lock for console output
_output_lock = threading.Lock()

_StepList = list[tuple[str, Callable[[], None]]]


def _empty_step_list() -> _StepList:
    """Return an empty step list with proper typing."""
    return []


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StepResult:
    """Result of a test step execution."""

    name: str
    success: bool
    output: str = ""
    error: str = ""
    duration: float = 0.0
    command: str = ""


@dataclass
class TestSteps:
    """Categorized test steps for sequential and parallel execution."""

    sequential_pre: _StepList = field(default_factory=_empty_step_list)
    parallel: _StepList = field(default_factory=_empty_step_list)
    sequential_post: _StepList = field(default_factory=_empty_step_list)


@dataclass
class ParallelStep:
    """A step configured for parallel execution with its command."""

    name: str
    command: list[str]


# ---------------------------------------------------------------------------
# Display Helpers
# ---------------------------------------------------------------------------

_SENSITIVE_ENV_PATTERNS = frozenset({"TOKEN", "PASSWORD", "SECRET", "API_KEY", "CREDENTIAL"})


def _echo_output(output: str, *, to_stderr: bool = False) -> None:
    """Echo output ensuring proper newline handling."""
    click.echo(output, err=to_stderr, nl=False)
    if not output.endswith("\n"):
        click.echo(err=to_stderr)


def _is_sensitive_env(key: str) -> bool:
    """Return True if the environment variable name suggests a sensitive value."""
    upper = key.upper()
    return any(s in upper for s in _SENSITIVE_ENV_PATTERNS)


def _display_command(cmd: Sequence[str] | str, label: str | None, env: dict[str, str] | None, verbose: bool) -> None:
    """Display command being executed with optional label and environment."""
    display = cmd if isinstance(cmd, str) else " ".join(cmd)
    if label and not verbose:
        click.echo(f"[{label}] $ {display}")
    if verbose:
        click.echo(f"  $ {display}")
        if env:
            overrides = {k: v for k, v in env.items() if os.environ.get(k) != v}
            if overrides:
                env_view = " ".join(f"{k}=***" if _is_sensitive_env(k) else f"{k}={v}" for k, v in overrides.items())
                click.echo(f"    env {env_view}")


def _display_result(result: RunResult, label: str | None, verbose: bool) -> None:
    """Display verbose result information."""
    if verbose and label:
        click.echo(f"    -> {label}: exit={result.code} out={bool(result.out)} err={bool(result.err)}")


def _display_captured_output(result: RunResult, capture: bool, verbose: bool) -> None:
    """Display captured stdout/stderr if verbose or on error."""
    if capture and (verbose or result.code != 0):
        if result.out:
            _echo_output(result.out)
        if result.err:
            _echo_output(result.err, to_stderr=True)


# ---------------------------------------------------------------------------
# Command Execution
# ---------------------------------------------------------------------------


def make_run_command(default_env: dict[str, str]) -> Callable[..., RunResult]:
    """Create a ``_run_command`` function bound to *default_env*.

    The returned callable has the same signature as the previous module-level
    ``_run_command`` but captures the environment dict via closure instead of
    reading a global.
    """

    def _run_command(
        cmd: Sequence[str] | str,
        *,
        env: dict[str, str] | None = None,
        check: bool = True,
        capture: bool = True,
        label: str | None = None,
        verbose: bool = False,
    ) -> RunResult:
        """Execute command with optional display, capture, and error handling."""
        _display_command(cmd, label, env, verbose)
        merged_env = default_env if env is None else default_env | env
        result = run(cmd, env=merged_env, check=False, capture=capture)
        _display_result(result, label, verbose)
        _display_captured_output(result, capture, verbose)
        if check and result.code != 0:
            raise SystemExit(result.code)
        return result

    return _run_command


def make_step(
    run_command_fn: Callable[..., RunResult],
    cmd: list[str] | str,
    label: str,
    *,
    capture: bool = True,
    verbose: bool = False,
) -> Callable[[], None]:
    """Create a step function that executes a command via *run_command_fn*."""

    def runner() -> None:
        run_command_fn(cmd, label=label, capture=capture, verbose=verbose)

    return runner


def make_run_fn(run_command_fn: Callable[..., RunResult], verbose: bool) -> Callable[..., RunResult]:
    """Create a run function with the specified verbosity.

    This factory function creates a run_fn that can be passed to other
    functions, avoiding the need for nested function definitions.
    """

    def run_fn(
        cmd: Sequence[str] | str,
        *,
        env: dict[str, str] | None = None,
        check: bool = True,
        capture: bool = True,
        label: str | None = None,
    ) -> RunResult:
        return run_command_fn(cmd, env=env, check=check, capture=capture, label=label, verbose=verbose)

    return run_fn


# ---------------------------------------------------------------------------
# Parallel Execution
# ---------------------------------------------------------------------------


def run_step_subprocess(step: ParallelStep, default_env: dict[str, str]) -> StepResult:
    """Run a step as a subprocess and capture its output."""
    start_time = time.perf_counter()
    cmd_str = " ".join(step.command)

    result = run(step.command, env=default_env, check=False, capture=True)

    duration = time.perf_counter() - start_time
    success = result.code == 0

    return StepResult(
        name=step.name,
        success=success,
        output=result.out,
        error=result.err,
        duration=duration,
        command=cmd_str,
    )


def run_parallel_steps_subprocess(
    steps: list[ParallelStep],
    default_env: dict[str, str],
    *,
    max_workers: int | None = None,
) -> list[StepResult]:
    """Run multiple steps in parallel using subprocesses and collect results."""
    if not steps:
        return []

    # Default to number of steps or 4, whichever is smaller
    if max_workers is None:
        max_workers = min(len(steps), 4)

    results: list[StepResult] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_step = {executor.submit(run_step_subprocess, step, default_env): step.name for step in steps}

        for future in as_completed(future_to_step):
            result = future.result()
            results.append(result)

    # Sort results by original order
    step_order = {step.name: i for i, step in enumerate(steps)}
    results.sort(key=lambda r: step_order.get(r.name, 999))

    return results


def display_parallel_results(
    results: list[StepResult],
    start_index: int,
    total: int,
    *,
    verbose: bool = False,
) -> bool:
    """Display results from parallel execution. Returns True if all passed."""
    all_passed = True

    for i, result in enumerate(results):
        status = "PASS" if result.success else "FAIL"
        step_num = start_index + i
        duration_str = f" ({result.duration:.1f}s)" if result.duration >= 0.1 else ""

        # Show command and status
        click.echo(f"[{step_num}/{total}] {result.name} [{status}]{duration_str}")

        # Show output based on success and verbosity
        show_output = not result.success or verbose

        if show_output and result.command:
            click.echo(f"  $ {result.command}")

        if not result.success:
            all_passed = False

        # Always show output for failures, optionally for success in verbose mode
        if show_output:
            if result.output:
                # Indent output for readability
                for line in result.output.rstrip().split("\n"):
                    click.echo(f"    {line}")
            if result.error:
                for line in result.error.rstrip().split("\n"):
                    click.echo(f"    {line}", err=True)

    return all_passed


# ---------------------------------------------------------------------------
# Test Step Builder
# ---------------------------------------------------------------------------


def build_test_steps(
    config: object,
    *,
    strict_format: bool,
    verbose: bool,
    run_command_fn: Callable[..., RunResult],
    import_package: str,
) -> TestSteps:
    """Build categorized test steps for sequential and parallel execution.

    Parameters
    ----------
    config:
        A ``TestConfig`` instance (imported as ``object`` to avoid circular
        imports; accessed via attribute protocol).
    strict_format:
        Whether to add a ``ruff format --check`` step.
    verbose:
        Passed through to step factories.
    run_command_fn:
        A ``_run_command`` callable produced by ``make_run_command``.
    import_package:
        The project's importable package name (e.g. ``bitranox_template_py_cli``).
    """
    from pathlib import Path

    from ._test_audit import run_pip_audit_guarded

    run_fn = make_run_fn(run_command_fn, verbose)

    def _make(cmd: list[str], label: str, capture: bool = True) -> Callable[[], None]:
        return make_step(run_command_fn, cmd, label, capture=capture, verbose=verbose)

    steps = TestSteps()

    # Sequential pre-steps: must run before parallel checks
    # Ruff format modifies files, so it must run first and alone
    steps.sequential_pre.append(("Ruff format (apply)", _make(["ruff", "format", "."], "ruff-format-apply")))

    # Parallel steps: can run concurrently after formatting
    if strict_format:
        steps.parallel.append(("Ruff format check", _make(["ruff", "format", "--check", "."], "ruff-format-check")))

    steps.parallel.append(("Ruff lint", _make(["ruff", "check", "."], "ruff-check")))

    steps.parallel.append(
        (
            "Import-linter contracts",
            _make(["lint-imports"], "import-linter"),
        )
    )

    steps.parallel.append(("Pyright type-check", _make(["pyright"], "pyright")))

    # Access config attributes via protocol
    src_path: str = getattr(config, "src_path", "src")
    bandit_skips: tuple[str, ...] = getattr(config, "bandit_skips", ())
    pip_audit_ignores: tuple[str, ...] = getattr(config, "pip_audit_ignores", ())

    bandit_src = str(Path(src_path) / import_package)
    bandit_cmd = ["bandit", "-q", "-r"]
    if bandit_skips:
        bandit_cmd.extend(["-s", ",".join(bandit_skips)])
    bandit_cmd.append(bandit_src)
    steps.parallel.append(("Bandit security scan", _make(bandit_cmd, "bandit")))

    # Sequential post-steps: must run after parallel checks
    # pip-audit has network calls and complex output, better sequential
    steps.sequential_post.append(("pip-audit (guarded)", lambda: run_pip_audit_guarded(pip_audit_ignores, run_fn)))

    return steps
