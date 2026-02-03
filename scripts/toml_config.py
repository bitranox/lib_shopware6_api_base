"""Dataclass-based TOML configuration parsing.

Provides type-safe dataclasses for pyproject.toml sections, eliminating
dict-based access patterns and their associated type issues.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import rtoml

__all__ = [
    "CleanConfig",
    "CoverageReportConfig",
    "BanditConfig",
    "PipAuditConfig",
    "ScriptsTestConfig",
    "ToolConfig",
    "ProjectSection",
    "BuildSystemSection",
    "PyprojectConfig",
    "load_pyproject_config",
]


# ---------------------------------------------------------------------------
# Helper Functions for Safe Value Extraction
# ---------------------------------------------------------------------------


def _get_str(data: dict[str, Any], key: str, default: str = "") -> str:
    """Extract a string value from dict, with default fallback."""
    value = data.get(key)
    if isinstance(value, str):
        return value
    if value is not None:
        return str(value)
    return default


def _get_int(data: dict[str, Any], key: str, default: int = 0) -> int:
    """Extract an integer value from dict, with default fallback."""
    value = data.get(key)
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, (float, str)):
        try:
            return int(value)
        except (ValueError, TypeError):
            pass
    return default


def _get_str_list(data: dict[str, Any], key: str) -> list[str]:
    """Extract a list of strings from dict, filtering non-strings."""
    value = data.get(key)
    if not isinstance(value, list):
        return []
    typed_list = cast(list[object], value)
    return [str(item) for item in typed_list if item is not None]


def _get_dict(data: dict[str, Any], key: str) -> dict[str, Any]:
    """Extract a nested dict from dict, returning empty dict if not found."""
    value = data.get(key)
    if isinstance(value, dict):
        return cast(dict[str, Any], value)
    return {}


# ---------------------------------------------------------------------------
# Tool Configuration Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CleanConfig:
    """Configuration for [tool.clean] section."""

    patterns: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CleanConfig:
        """Create from dict parsed from TOML."""
        patterns = _get_str_list(data, "patterns")
        return cls(patterns=tuple(patterns))


@dataclass(frozen=True)
class CoverageReportConfig:
    """Configuration for [tool.coverage.report] section."""

    fail_under: int = 80

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CoverageReportConfig:
        """Create from dict parsed from TOML."""
        report_data = _get_dict(data, "report")
        fail_under = _get_int(report_data, "fail_under", 80)
        return cls(fail_under=fail_under)


@dataclass(frozen=True)
class BanditConfig:
    """Configuration for [tool.bandit] section."""

    skips: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BanditConfig:
        """Create from dict parsed from TOML."""
        skips = _get_str_list(data, "skips")
        return cls(skips=tuple(skips))


@dataclass(frozen=True)
class PipAuditConfig:
    """Configuration for [tool.pip-audit] section."""

    ignore_vulns: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PipAuditConfig:
        """Create from dict parsed from TOML."""
        ignore_vulns = _get_str_list(data, "ignore-vulns")
        return cls(ignore_vulns=tuple(ignore_vulns))


@dataclass(frozen=True)
class ScriptsTestConfig:
    """Configuration for [tool.scripts.test] section."""

    pytest_verbosity: str = "-vv"
    coverage_report_file: str = "coverage.xml"
    src_path: str = "src"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScriptsTestConfig:
        """Create from dict parsed from TOML."""
        test_data = _get_dict(data, "test")
        return cls(
            pytest_verbosity=_get_str(test_data, "pytest-verbosity", "-vv"),
            coverage_report_file=_get_str(test_data, "coverage-report-file", "coverage.xml"),
            src_path=_get_str(test_data, "src-path", "src"),
        )


@dataclass(frozen=True)
class PoetryDepSpec:
    """A single Poetry dependency specification."""

    name: str
    version: str = ""
    extras: tuple[str, ...] = ()

    def to_requirement_string(self) -> str:
        """Convert to PEP 508 requirement string."""
        if not self.version or self.version == "*":
            return self.name
        if self.version.startswith("^"):
            return f"{self.name}>={self.version[1:]}"
        if self.version.startswith("~"):
            return f"{self.name}>={self.version[1:]}"
        return f"{self.name}{self.version}"


def _empty_poetry_groups() -> dict[str, tuple[PoetryDepSpec, ...]]:
    """Return an empty dict for Poetry group dependencies."""
    return {}


@dataclass(frozen=True)
class PoetryConfig:
    """Configuration for [tool.poetry] section."""

    dependencies: tuple[PoetryDepSpec, ...] = ()
    dev_dependencies: tuple[PoetryDepSpec, ...] = ()
    group_dependencies: dict[str, tuple[PoetryDepSpec, ...]] = field(default_factory=_empty_poetry_groups)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PoetryConfig:
        """Create from dict parsed from TOML."""
        dependencies = cls._parse_poetry_deps(_get_dict(data, "dependencies"))
        dev_dependencies = cls._parse_poetry_deps(_get_dict(data, "dev-dependencies"))

        group_dependencies = cls._parse_poetry_groups(_get_dict(data, "group"))

        return cls(
            dependencies=dependencies,
            dev_dependencies=dev_dependencies,
            group_dependencies=group_dependencies,
        )

    @classmethod
    def _parse_poetry_groups(cls, group_data: dict[str, Any]) -> dict[str, tuple[PoetryDepSpec, ...]]:
        """Parse Poetry group dependencies."""
        result: dict[str, tuple[PoetryDepSpec, ...]] = {}
        for group_name_raw, group_content in group_data.items():
            group_name = str(group_name_raw)
            if isinstance(group_content, dict):
                typed_content = cast(dict[str, Any], group_content)
                deps_dict = _get_dict(typed_content, "dependencies")
                result[group_name] = cls._parse_poetry_deps(deps_dict)
        return result

    @staticmethod
    def _parse_poetry_deps(deps: dict[str, Any]) -> tuple[PoetryDepSpec, ...]:
        """Parse Poetry-style dependency dict into PoetryDepSpec objects."""
        result: list[PoetryDepSpec] = []
        for name_raw, spec in deps.items():
            name = str(name_raw)
            if name.lower() == "python":
                continue
            if isinstance(spec, str):
                result.append(PoetryDepSpec(name=name, version=spec))
            elif isinstance(spec, dict):
                typed_spec = cast(dict[str, Any], spec)
                version = _get_str(typed_spec, "version", "")
                extras = tuple(_get_str_list(typed_spec, "extras"))
                result.append(PoetryDepSpec(name=name, version=version, extras=extras))
            else:
                result.append(PoetryDepSpec(name=name))
        return tuple(result)


def _empty_str_tuple_dict() -> dict[str, tuple[str, ...]]:
    """Return an empty dict for string tuple mappings."""
    return {}


@dataclass(frozen=True)
class PdmConfig:
    """Configuration for [tool.pdm] section."""

    dev_dependencies: dict[str, tuple[str, ...]] = field(default_factory=_empty_str_tuple_dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PdmConfig:
        """Create from dict parsed from TOML."""
        dev_deps_raw = _get_dict(data, "dev-dependencies")
        dev_dependencies = cls._parse_dev_deps(dev_deps_raw)
        return cls(dev_dependencies=dev_dependencies)

    @staticmethod
    def _parse_dev_deps(dev_deps_raw: dict[str, Any]) -> dict[str, tuple[str, ...]]:
        """Parse PDM dev dependencies."""
        result: dict[str, tuple[str, ...]] = {}
        for group_name_raw, group_deps in dev_deps_raw.items():
            group_name = str(group_name_raw)
            if isinstance(group_deps, list):
                typed_deps = cast(list[object], group_deps)
                result[group_name] = tuple(str(item) for item in typed_deps if item is not None)
        return result


@dataclass(frozen=True)
class UvConfig:
    """Configuration for [tool.uv] section."""

    dev_dependencies: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UvConfig:
        """Create from dict parsed from TOML."""
        dev_deps = _get_str_list(data, "dev-dependencies")
        return cls(dev_dependencies=tuple(dev_deps))


@dataclass(frozen=True)
class ToolConfig:
    """Configuration for the [tool] section of pyproject.toml."""

    clean: CleanConfig = field(default_factory=CleanConfig)
    coverage: CoverageReportConfig = field(default_factory=CoverageReportConfig)
    bandit: BanditConfig = field(default_factory=BanditConfig)
    pip_audit: PipAuditConfig = field(default_factory=PipAuditConfig)
    scripts: ScriptsTestConfig = field(default_factory=ScriptsTestConfig)
    poetry: PoetryConfig = field(default_factory=PoetryConfig)
    pdm: PdmConfig = field(default_factory=PdmConfig)
    uv: UvConfig = field(default_factory=UvConfig)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ToolConfig:
        """Create from dict parsed from TOML."""
        return cls(
            clean=CleanConfig.from_dict(_get_dict(data, "clean")),
            coverage=CoverageReportConfig.from_dict(_get_dict(data, "coverage")),
            bandit=BanditConfig.from_dict(_get_dict(data, "bandit")),
            pip_audit=PipAuditConfig.from_dict(_get_dict(data, "pip-audit")),
            scripts=ScriptsTestConfig.from_dict(_get_dict(data, "scripts")),
            poetry=PoetryConfig.from_dict(_get_dict(data, "poetry")),
            pdm=PdmConfig.from_dict(_get_dict(data, "pdm")),
            uv=UvConfig.from_dict(_get_dict(data, "uv")),
        )


# ---------------------------------------------------------------------------
# Top-Level Section Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProjectSection:
    """Configuration for the [project] section of pyproject.toml."""

    name: str = ""
    version: str = ""
    description: str = ""
    dependencies: tuple[str, ...] = ()
    optional_dependencies: dict[str, tuple[str, ...]] = field(default_factory=_empty_str_tuple_dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProjectSection:
        """Create from dict parsed from TOML."""
        dependencies = _get_str_list(data, "dependencies")
        optional_deps_raw = _get_dict(data, "optional-dependencies")
        optional_dependencies = cls._parse_optional_deps(optional_deps_raw)

        return cls(
            name=_get_str(data, "name"),
            version=_get_str(data, "version"),
            description=_get_str(data, "description"),
            dependencies=tuple(dependencies),
            optional_dependencies=optional_dependencies,
        )

    @staticmethod
    def _parse_optional_deps(optional_deps_raw: dict[str, Any]) -> dict[str, tuple[str, ...]]:
        """Parse optional dependencies."""
        result: dict[str, tuple[str, ...]] = {}
        for group_name_raw, group_deps in optional_deps_raw.items():
            group_name = str(group_name_raw)
            if isinstance(group_deps, list):
                typed_deps = cast(list[object], group_deps)
                result[group_name] = tuple(str(item) for item in typed_deps if item is not None)
        return result


@dataclass(frozen=True)
class BuildSystemSection:
    """Configuration for the [build-system] section of pyproject.toml."""

    requires: tuple[str, ...] = ()
    build_backend: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BuildSystemSection:
        """Create from dict parsed from TOML."""
        requires = _get_str_list(data, "requires")
        return cls(
            requires=tuple(requires),
            build_backend=_get_str(data, "build-backend"),
        )


@dataclass(frozen=True)
class DependencyGroupsSection:
    """Configuration for the [dependency-groups] section (PEP 735)."""

    groups: dict[str, tuple[str, ...]] = field(default_factory=_empty_str_tuple_dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DependencyGroupsSection:
        """Create from dict parsed from TOML."""
        groups = cls._parse_groups(data)
        return cls(groups=groups)

    @staticmethod
    def _parse_groups(data: dict[str, Any]) -> dict[str, tuple[str, ...]]:
        """Parse dependency groups."""
        result: dict[str, tuple[str, ...]] = {}
        for group_name_raw, group_deps in data.items():
            group_name = str(group_name_raw)
            if isinstance(group_deps, list):
                typed_deps = cast(list[object], group_deps)
                result[group_name] = tuple(str(item) for item in typed_deps if item is not None)
        return result


# ---------------------------------------------------------------------------
# Main Configuration Dataclass
# ---------------------------------------------------------------------------


def _empty_any_dict() -> dict[str, Any]:
    """Return an empty dict with proper typing for dataclass default."""
    return {}


@dataclass(frozen=True)
class PyprojectConfig:
    """Complete pyproject.toml configuration."""

    project: ProjectSection = field(default_factory=ProjectSection)
    build_system: BuildSystemSection = field(default_factory=BuildSystemSection)
    dependency_groups: DependencyGroupsSection = field(default_factory=DependencyGroupsSection)
    tool: ToolConfig = field(default_factory=ToolConfig)
    raw_data: dict[str, Any] = field(default_factory=_empty_any_dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PyprojectConfig:
        """Create from dict parsed from TOML."""
        return cls(
            project=ProjectSection.from_dict(_get_dict(data, "project")),
            build_system=BuildSystemSection.from_dict(_get_dict(data, "build-system")),
            dependency_groups=DependencyGroupsSection.from_dict(_get_dict(data, "dependency-groups")),
            tool=ToolConfig.from_dict(_get_dict(data, "tool")),
            raw_data=data,
        )

    @classmethod
    def from_path(cls, path: Path) -> PyprojectConfig:
        """Load configuration from a pyproject.toml file."""
        try:
            data: dict[str, Any] = rtoml.loads(path.read_text(encoding="utf-8"))
            return cls.from_dict(data)
        except (rtoml.TomlParsingError, OSError, ValueError):
            return cls()


def load_pyproject_config(path: Path = Path("pyproject.toml")) -> PyprojectConfig:
    """Load and parse pyproject.toml into a typed configuration object.

    Args:
        path: Path to the pyproject.toml file

    Returns:
        PyprojectConfig with all sections parsed, using defaults for missing values
    """
    return PyprojectConfig.from_path(path)
