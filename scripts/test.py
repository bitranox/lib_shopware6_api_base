"""Test runner with linting, type-checking, and coverage support.

This module provides a unified test runner that:
- Runs ruff format/lint checks
- Validates import contracts with import-linter
- Type-checks with pyright
- Scans for security issues with bandit
- Audits dependencies with pip-audit
- Executes pytest with optional coverage
- Uploads coverage to Codecov

Parallel execution is supported for independent checks (ruff, pyright, bandit,
import-linter) to reduce total execution time.
"""

from __future__ import annotations

import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import click

from ._test_audit import (
    AuditDependency,
    AuditResult,
    AuditVulnerability,
)
from ._test_coverage import (
    ensure_codecov_token,
    prune_coverage_data_files,
    remove_report_artifacts,
    upload_coverage_report,
)
from ._test_steps import (
    ParallelStep,
    StepResult,
    TestSteps,
    build_test_steps,
    display_parallel_results,
    make_run_command,
    make_run_fn,
    run_parallel_steps_subprocess,
)
from ._utils import (
    bootstrap_dev,
    get_project_metadata,
    run,
    sync_metadata_module,
)
from .toml_config import load_pyproject_config

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROJECT = get_project_metadata()
PROJECT_ROOT = Path(__file__).resolve().parents[1]
COVERAGE_TARGET = PROJECT.coverage_source

__all__ = ["run_tests", "run_coverage", "COVERAGE_TARGET"]

_TRUTHY = {"1", "true", "yes", "on"}
_FALSY = {"0", "false", "no", "off"}

# Re-export dataclasses so existing imports from scripts.test keep working
__all__ += [
    "AuditVulnerability",
    "AuditDependency",
    "AuditResult",
    "StepResult",
    "TestSteps",
    "ParallelStep",
]


# ---------------------------------------------------------------------------
# Project Configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TestConfig:
    """Consolidated test configuration from pyproject.toml."""

    fail_under: int
    bandit_skips: tuple[str, ...]
    pip_audit_ignores: tuple[str, ...]
    pytest_verbosity: str
    coverage_report_file: str
    src_path: str

    @classmethod
    def from_pyproject(cls, pyproject_path: Path) -> TestConfig:
        """Load test configuration from pyproject.toml."""
        config = load_pyproject_config(pyproject_path)
        return cls(
            fail_under=config.tool.coverage.fail_under,
            bandit_skips=config.tool.bandit.skips,
            pip_audit_ignores=config.tool.pip_audit.ignore_vulns,
            pytest_verbosity=config.tool.scripts.pytest_verbosity,
            coverage_report_file=config.tool.scripts.coverage_report_file,
            src_path=config.tool.scripts.src_path,
        )


# ---------------------------------------------------------------------------
# Test Environment (replaces global mutable state)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TestEnvironment:
    """Immutable snapshot of the environment used for subprocess execution."""

    default_env: dict[str, str]
    src_path: str


# ---------------------------------------------------------------------------
# Environment Management
# ---------------------------------------------------------------------------


def _build_default_env(src_path: str = "src") -> dict[str, str]:
    """Return the base environment for subprocess execution."""
    pythonpath = os.pathsep.join(filter(None, [str(PROJECT_ROOT / src_path), os.environ.get("PYTHONPATH")]))
    return os.environ | {"PYTHONPATH": pythonpath}


# ---------------------------------------------------------------------------
# Format Resolution
# ---------------------------------------------------------------------------


def _resolve_strict_format(strict_format: bool | None) -> bool:
    """Resolve the strict format setting from parameter or environment."""
    if strict_format is not None:
        return strict_format

    env_value = os.getenv("STRICT_RUFF_FORMAT")
    if env_value is None:
        return True

    token = env_value.strip().lower()
    if token in _TRUTHY:
        return True
    if token in _FALSY or token == "":
        return False
    raise SystemExit("STRICT_RUFF_FORMAT must be one of {0,1,true,false,yes,no,on,off}.")


# ---------------------------------------------------------------------------
# Pytest Step
# ---------------------------------------------------------------------------


def _run_pytest_step(
    config: TestConfig,
    coverage_mode: str,
    verbose: bool,
    test_env: TestEnvironment,
) -> None:
    """Execute pytest with optional coverage collection."""
    for path in (Path(".coverage"), Path(config.coverage_report_file)):
        path.unlink(missing_ok=True)

    run_command_fn = make_run_command(test_env.default_env)
    run_fn = make_run_fn(run_command_fn, verbose)
    enable_coverage = coverage_mode == "on" or (
        coverage_mode == "auto" and (os.getenv("CI") or os.getenv("CODECOV_TOKEN"))
    )

    if enable_coverage:
        click.echo("[coverage] enabled")
        with tempfile.TemporaryDirectory() as tmp:
            cov_file = Path(tmp) / ".coverage"
            click.echo(f"[coverage] file={cov_file}")
            env = os.environ | {"COVERAGE_FILE": str(cov_file)}
            pytest_result = run_fn(
                [
                    "python",
                    "-m",
                    "pytest",
                    "-m",
                    "not local_only",
                    f"--cov={COVERAGE_TARGET}",
                    f"--cov-report=xml:{config.coverage_report_file}",
                    "--cov-report=term-missing",
                    f"--cov-fail-under={config.fail_under}",
                    config.pytest_verbosity,
                ],
                env=env,
                capture=False,
                label="pytest",
            )
            if pytest_result.code != 0:
                click.echo("[pytest] failed; skipping Codecov upload", err=True)
                raise SystemExit(pytest_result.code)
    else:
        click.echo("[coverage] disabled (set --coverage=on to force)")
        pytest_result = run_fn(
            ["python", "-m", "pytest", "-m", "not local_only", config.pytest_verbosity],
            capture=False,
            label="pytest-no-cov",
        )
        if pytest_result.code != 0:
            click.echo("[pytest] failed; skipping Codecov upload", err=True)
            raise SystemExit(pytest_result.code)


# ---------------------------------------------------------------------------
# Parallel Command Extraction
# ---------------------------------------------------------------------------


def _extract_parallel_commands(config: TestConfig, *, strict_format: bool) -> list[ParallelStep]:
    """Build the list of ``ParallelStep`` objects for parallel execution.

    This replaces the old ``_build_parallel_commands`` which duplicated the
    same command-building logic found in ``build_test_steps``.  The commands
    are reconstructed from ``config`` to guarantee they match the callables
    stored in the ``TestSteps.parallel`` list.
    """
    commands: list[ParallelStep] = []

    if strict_format:
        commands.append(ParallelStep("Ruff format check", ["ruff", "format", "--check", "."]))

    commands.append(ParallelStep("Ruff lint", ["ruff", "check", "."]))

    commands.append(
        ParallelStep(
            "Import-linter contracts",
            ["lint-imports"],
        )
    )

    commands.append(ParallelStep("Pyright type-check", ["pyright"]))

    bandit_src = str(Path(config.src_path) / PROJECT.import_package)
    bandit_cmd = ["bandit", "-q", "-r"]
    if config.bandit_skips:
        bandit_cmd.extend(["-s", ",".join(config.bandit_skips)])
    bandit_cmd.append(bandit_src)
    commands.append(ParallelStep("Bandit security scan", bandit_cmd))

    return commands


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_coverage(*, verbose: bool = False) -> None:
    """Run pytest under coverage using python modules to avoid PATH shim issues."""
    sync_metadata_module(PROJECT)
    bootstrap_dev()

    config = TestConfig.from_pyproject(PROJECT_ROOT / "pyproject.toml")
    prune_coverage_data_files()
    remove_report_artifacts(config.coverage_report_file)
    base_env = _build_default_env(config.src_path)

    with tempfile.TemporaryDirectory() as tmpdir:
        coverage_file = Path(tmpdir) / ".coverage"
        env = base_env | {"COVERAGE_FILE": str(coverage_file)}

        coverage_cmd = [
            sys.executable,
            "-m",
            "coverage",
            "run",
            "-m",
            "pytest",
            "-m",
            "not local_only",
            config.pytest_verbosity,
        ]
        click.echo(f"[coverage] python -m coverage run -m pytest -m 'not local_only' {config.pytest_verbosity}")
        result = run(coverage_cmd, env=env, capture=not verbose, check=False)
        if result.code != 0:
            if result.out:
                click.echo(result.out, nl=False)
            if result.err:
                click.echo(result.err, err=True, nl=False)
            raise SystemExit(result.code)

        report_cmd = [sys.executable, "-m", "coverage", "report", "-m"]
        click.echo("[coverage] python -m coverage report -m")
        report = run(report_cmd, env=env, capture=not verbose, check=False)
        if report.code != 0:
            if report.out:
                click.echo(report.out, nl=False)
            if report.err:
                click.echo(report.err, err=True, nl=False)
            raise SystemExit(report.code)
        if report.out and not verbose:
            click.echo(report.out, nl=False)


def run_local_tests(*, verbose: bool = False) -> None:
    """Run only tests marked as local_only (skipped in CI).

    These tests require external resources (SMTP server, etc.) or the local
    dev environment. Use this target to run them when the required environment
    is configured.

    Args:
        verbose: Enable verbose pytest output
    """
    config = TestConfig.from_pyproject(PROJECT_ROOT / "pyproject.toml")
    click.echo("[test-local] Running local-only tests...")
    click.echo("[test-local] These tests require external resources (see .env.example)")

    verbosity = config.pytest_verbosity if verbose else "-v"
    result = run(
        [sys.executable, "-m", "pytest", "-m", "local_only", verbosity, "tests/"],
        capture=False,
        check=False,
    )

    if result.code != 0:
        click.echo("[test-local] Some tests failed", err=True)
        raise SystemExit(result.code)

    click.echo("[test-local] Local-only tests completed successfully")


def run_tests(
    *,
    coverage: str = "on",
    verbose: bool = False,
    strict_format: bool | None = None,
    parallel: bool = True,
) -> None:
    """Run the complete test suite with all quality checks.

    Args:
        coverage: Coverage mode - "on", "off", or "auto"
        verbose: Enable verbose output
        strict_format: Enforce strict ruff format checking
        parallel: Run independent checks in parallel (default: True)
    """
    env_verbose = os.getenv("TEST_VERBOSE", "").lower()
    if not verbose and env_verbose in _TRUTHY:
        verbose = True

    # Check for PARALLEL env override
    env_parallel = os.getenv("TEST_PARALLEL", "").lower()
    if env_parallel in _FALSY:
        parallel = False
    elif env_parallel in _TRUTHY:
        parallel = True

    sync_metadata_module(PROJECT)
    bootstrap_dev()

    config = TestConfig.from_pyproject(PROJECT_ROOT / "pyproject.toml")

    # Build immutable test environment (no globals)
    default_env = _build_default_env(config.src_path)
    test_env = TestEnvironment(default_env=default_env, src_path=config.src_path)

    resolved_strict_format = _resolve_strict_format(strict_format)

    run_command_fn = make_run_command(test_env.default_env)
    steps = build_test_steps(
        config,
        strict_format=resolved_strict_format,
        verbose=verbose,
        run_command_fn=run_command_fn,
        import_package=PROJECT.import_package,
    )

    # Calculate total steps
    total_steps = (
        len(steps.sequential_pre) + len(steps.parallel) + len(steps.sequential_post) + 1  # pytest
    )
    current_step = 0

    # Phase 1: Sequential pre-steps (ruff format)
    for description, action in steps.sequential_pre:
        current_step += 1
        click.echo(f"[{current_step}/{total_steps}] {description}")
        action()

    # Phase 2: Parallel checks (or sequential if parallel=False)
    if parallel and len(steps.parallel) > 1:
        parallel_commands = _extract_parallel_commands(config, strict_format=resolved_strict_format)
        n_parallel = len(parallel_commands)
        step_range = f"{current_step + 1}-{current_step + n_parallel}"
        click.echo(f"[{step_range}/{total_steps}] Running {n_parallel} checks in parallel...")
        results = run_parallel_steps_subprocess(parallel_commands, test_env.default_env)
        all_passed = display_parallel_results(results, current_step + 1, total_steps, verbose=verbose)
        current_step += len(parallel_commands)

        if not all_passed:
            # Show which checks failed
            failed = [r.name for r in results if not r.success]
            click.echo(f"Failed checks: {', '.join(failed)}", err=True)
            raise SystemExit(1)
    else:
        # Run sequentially
        for description, action in steps.parallel:
            current_step += 1
            click.echo(f"[{current_step}/{total_steps}] {description}")
            action()

    # Phase 3: Sequential post-steps (pip-audit)
    for description, action in steps.sequential_post:
        current_step += 1
        click.echo(f"[{current_step}/{total_steps}] {description}")
        action()

    # Phase 4: Pytest (always sequential)
    current_step += 1
    pytest_label = "Pytest with coverage" if coverage != "off" else "Pytest"
    click.echo(f"[{current_step}/{total_steps}] {pytest_label}")
    _run_pytest_step(config, coverage, verbose, test_env)

    # Phase 5: Codecov upload
    token_loaded = ensure_codecov_token()
    if token_loaded:
        # Rebuild env to pick up the newly-loaded CODECOV_TOKEN
        refreshed_env = _build_default_env(config.src_path)
        refreshed_test_env = TestEnvironment(default_env=refreshed_env, src_path=config.src_path)
    else:
        refreshed_test_env = test_env

    if Path(config.coverage_report_file).exists():
        prune_coverage_data_files()
        upload_run_command_fn = make_run_command(refreshed_test_env.default_env)
        upload_run_fn = make_run_fn(upload_run_command_fn, verbose)
        uploaded = upload_coverage_report(
            project=PROJECT,
            run_fn=upload_run_fn,
            coverage_report_file=config.coverage_report_file,
        )
        if uploaded:
            click.echo("All checks passed (coverage uploaded)")
        else:
            click.echo("Checks finished (coverage upload skipped or failed)")
    else:
        click.echo(f"Checks finished ({config.coverage_report_file} missing, upload skipped)")


def main() -> None:
    """Entry point for direct script execution."""
    run_tests()


if __name__ == "__main__":
    main()
