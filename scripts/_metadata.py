"""Project metadata extraction from ``pyproject.toml``.

Purpose
-------
Parse ``pyproject.toml`` once, cache the result, and expose a
``ProjectMetadata`` dataclass that downstream scripts use for build, test,
release and documentation automation.

Contents
--------
* ``ProjectMetadata`` -- dataclass holding all derived project attributes.
* ``get_project_metadata`` -- cached factory that reads ``pyproject.toml``.
* ``sync_metadata_module`` -- write/update ``__init__conf__.py``.
* ``read_version_from_pyproject`` -- quick version-only accessor.
* Numerous private helpers for slug normalisation, author extraction,
  entry-point resolution, and module rendering.

System Role
-----------
Pure data-extraction layer.  Has no dependency on git, pip or subprocesses --
only reads ``pyproject.toml`` via *rtoml* and produces structured metadata.
"""

from __future__ import annotations

import re
import textwrap
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlparse

import orjson
import rtoml

__all__ = [
    "ProjectMetadata",
    "get_project_metadata",
    "sync_metadata_module",
    "read_version_from_pyproject",
    "load_pyproject",
    "as_str_mapping",
    "get_dependencies",
]

_RE_NON_ALNUM = re.compile(r"[^A-Za-z0-9]+")
_RE_PYPROJECT_VERSION = re.compile(r'(?m)^version\s*=\s*"([0-9]+(?:\.[0-9]+){2})"')


# ---------------------------------------------------------------------------
# Caches
# ---------------------------------------------------------------------------

_PYPROJECT_DATA_CACHE: dict[Path, dict[str, object]] = {}
_METADATA_CACHE: dict[Path, ProjectMetadata] = {}


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------


@dataclass
class ProjectMetadata:
    """Project metadata extracted from pyproject.toml.

    Contains all relevant information about a Python project including
    repository details, package names, and build configuration.
    """

    name: str
    description: str
    slug: str
    repo_url: str
    repo_host: str
    repo_owner: str
    repo_name: str
    homepage: str
    import_package: str
    coverage_source: str
    scripts: dict[str, str]
    metadata_module: Path
    version: str
    summary: str
    author_name: str
    author_email: str
    shell_command: str

    def github_tarball_url(self, version: str) -> str:
        if self.repo_host == "github.com" and self.repo_owner and self.repo_name:
            return f"https://github.com/{self.repo_owner}/{self.repo_name}/archive/refs/tags/v{version}.tar.gz"
        return ""

    def resolve_cli_entry(self) -> tuple[str, str, str | None] | None:
        """Return ``(script_name, module, attr)`` for the preferred CLI entry point.

        Resolution strategy keeps ``pyproject.toml`` as the single source of truth:
        prefer scripts whose name matches the project slug/name/import package and
        fall back to the first declared script.
        """

        if not self.scripts:
            return None
        candidates = (
            self.slug,
            self.name,
            self.import_package,
            self.import_package.replace("_", "-"),
        )
        return _select_cli_entry(self.scripts, candidates)

    def diagnostic_lines(self) -> tuple[str, ...]:
        """Return human-friendly lines that summarise project metadata."""

        summary = [
            f"name={self.name}",
            f"slug={self.slug}",
            f"package={self.import_package}",
        ]
        if self.repo_url:
            summary.append(f"repository={self.repo_url}")
        if self.homepage:
            summary.append(f"homepage={self.homepage}")
        summary.append(f"version={self.version}")
        return tuple(summary)


# ---------------------------------------------------------------------------
# Private helpers -- slug / mapping / sequence
# ---------------------------------------------------------------------------


def _normalize_slug(value: str) -> str:
    slug = _RE_NON_ALNUM.sub("-", value).strip("-").lower()
    return slug or value.replace("_", "-").lower()


def _package_name_to_display(value: str) -> str:
    """Convert package name to display-friendly app name.

    Examples:
        "bitranox_template_py_cli" -> "Bitranox Template Py Cli"
        "my-cool-app" -> "My Cool App"
    """
    # Replace underscores and hyphens with spaces
    normalized = value.replace("_", " ").replace("-", " ")
    # Title case each word
    return " ".join(word.capitalize() for word in normalized.split())


def as_str_mapping(value: object) -> dict[str, object]:
    """Return a shallow copy of mapping entries with string keys."""
    if isinstance(value, dict):
        mapping = cast(dict[object, object], value)
        return {key: item for key, item in mapping.items() if isinstance(key, str)}
    return {}


def _as_str_dict(value: object) -> dict[str, str]:
    """Return a mapping containing only string keys and string values."""
    if isinstance(value, dict):
        mapping = cast(dict[object, object], value)
        return {key: item for key, item in mapping.items() if isinstance(key, str) and isinstance(item, str)}
    return {}


def _as_sequence(value: object) -> tuple[object, ...]:
    """Return a tuple for list/tuple values, otherwise an empty tuple."""

    if isinstance(value, (list, tuple)):
        sequence = cast(Sequence[object], value)
        return tuple(sequence)
    return ()


# ---------------------------------------------------------------------------
# Private helpers -- pyproject loading
# ---------------------------------------------------------------------------


def load_pyproject(pyproject: Path) -> dict[str, object]:
    path = pyproject.resolve()
    cached = _PYPROJECT_DATA_CACHE.get(path)
    if cached is not None:
        return cached
    raw_text = path.read_text(encoding="utf-8")
    try:
        parsed_obj = rtoml.loads(raw_text)
    except rtoml.TomlParsingError as exc:  # pragma: no cover - invalid pyproject fails fast
        msg = f"Unable to parse {path}: {exc}"
        raise ValueError(msg) from exc
    data = {str(key): value for key, value in parsed_obj.items()}
    _PYPROJECT_DATA_CACHE[path] = data
    return data


# ---------------------------------------------------------------------------
# Private helpers -- derive package / coverage / scripts
# ---------------------------------------------------------------------------


def _derive_import_package(data: dict[str, Any], fallback: str) -> str:
    tool_table = as_str_mapping(data.get("tool"))
    hatch_table = as_str_mapping(tool_table.get("hatch"))
    build_table = as_str_mapping(hatch_table.get("build"))
    targets_table = as_str_mapping(build_table.get("targets"))
    wheel_table = as_str_mapping(targets_table.get("wheel"))
    packages_value = wheel_table.get("packages")
    for entry in _as_sequence(packages_value):
        if isinstance(entry, str) and entry:
            return Path(entry).name
    project_table = as_str_mapping(data.get("project"))
    scripts_table = as_str_mapping(project_table.get("scripts"))
    for script_value in scripts_table.values():
        if isinstance(script_value, str) and ":" in script_value:
            module = script_value.split(":", 1)[0]
            return module.split(".", 1)[0]
    return fallback.replace("-", "_")


def _derive_coverage_source(data: dict[str, Any], fallback: str) -> str:
    tool_table = as_str_mapping(data.get("tool"))
    coverage_table = as_str_mapping(tool_table.get("coverage"))
    run_table = as_str_mapping(coverage_table.get("run"))
    sources_value = run_table.get("source")
    for entry in _as_sequence(sources_value):
        if isinstance(entry, str) and entry:
            return entry
    return fallback


def _derive_scripts(data: dict[str, Any]) -> dict[str, str]:
    project_table = as_str_mapping(data.get("project"))
    scripts_table = as_str_mapping(project_table.get("scripts"))
    scripts: dict[str, str] = {}
    for name, raw in scripts_table.items():
        if isinstance(raw, str):
            value = raw.strip()
            if value:
                scripts[name] = value
    return scripts


# ---------------------------------------------------------------------------
# Private helpers -- entry-point resolution
# ---------------------------------------------------------------------------


def _normalize_script_key(name: str) -> str:
    return name.replace("_", "-").lower()


def _parse_entrypoint(spec: str) -> tuple[str, str | None]:
    module, _, attr = spec.partition(":")
    module = module.strip()
    attr = attr.strip()
    return module, attr or None


def _select_cli_entry(
    scripts: Mapping[str, str],
    candidates: Sequence[str],
) -> tuple[str, str, str | None] | None:
    normalised: dict[str, tuple[str, str]] = {}
    for script_name, spec in scripts.items():
        if not spec:
            continue
        normalised[_normalize_script_key(script_name)] = (script_name, spec)

    for candidate in candidates:
        normalised_candidate = _normalize_script_key(candidate)
        match = normalised.get(normalised_candidate)
        if match is not None:
            script_name, spec = match
            module, attr = _parse_entrypoint(spec)
            return script_name, module, attr

    if normalised:
        script_name, spec = next(iter(normalised.values()))
        module, attr = _parse_entrypoint(spec)
        return script_name, module, attr

    return None


# ---------------------------------------------------------------------------
# Private helpers -- repo / author / summary extraction
# ---------------------------------------------------------------------------


def _parse_repo_url(repo_url: str) -> tuple[str, str, str]:
    """Parse repository URL into host, owner, and name.

    Args:
        repo_url: Repository URL (e.g., "https://github.com/owner/repo")

    Returns:
        Tuple of (host, owner, name). Empty strings if parsing fails.
    """
    if not repo_url:
        return "", "", ""
    parsed = urlparse(repo_url)
    repo_host = parsed.netloc.lower()
    repo_path = parsed.path.strip("/")
    if repo_path.endswith(".git"):
        repo_path = repo_path[:-4]
    parts = [p for p in repo_path.split("/") if p]
    if len(parts) >= 2:
        return repo_host, parts[0], parts[1]
    return repo_host, "", ""


def _extract_author_info(
    project_table: dict[str, object],
    fallback_name: str,
) -> tuple[str, str]:
    """Extract author name and email from project table.

    Args:
        project_table: Project section of pyproject.toml
        fallback_name: Fallback name if no author found

    Returns:
        Tuple of (author_name, author_email)
    """
    authors_list = _get_authors_list(project_table)
    author_name, author_email = _find_first_author(authors_list)
    return author_name or fallback_name, author_email


def _get_authors_list(project_table: dict[str, object]) -> list[dict[str, object]]:
    """Extract the authors list from project table."""
    authors_value = project_table.get("authors")
    if not isinstance(authors_value, list):
        return []
    return [cast(dict[str, object], entry) for entry in cast(list[object], authors_value) if isinstance(entry, dict)]


def _find_first_author(authors_list: list[dict[str, object]]) -> tuple[str, str]:
    """Find the first valid author name and email from authors list."""
    author_name = ""
    author_email = ""
    for author_dict in authors_list:
        if not author_name:
            author_name = _extract_str_field(author_dict, "name")
        if not author_email:
            author_email = _extract_str_field(author_dict, "email")
        if author_name and author_email:
            break
    return author_name, author_email


def _extract_str_field(data: dict[str, object], key: str) -> str:
    """Extract a string field from a dict, returning empty string if not found."""
    value = data.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return ""


def _extract_summary(
    project_table: dict[str, object],
    description: str,
    name: str,
) -> str:
    """Extract summary from project table with fallbacks.

    Args:
        project_table: Project section of pyproject.toml
        description: Project description
        name: Project name

    Returns:
        Summary string
    """
    summary = description.strip() if description else ""
    if not summary:
        summary_candidate = project_table.get("summary")
        summary = summary_candidate.strip() if isinstance(summary_candidate, str) else ""
    if not summary:
        summary = name
    return summary


def _extract_name(project_table: dict[str, object], pyproject: Path) -> str:
    """Extract project name from project table."""
    name = str(pyproject.stem)
    name_value = project_table.get("name")
    if isinstance(name_value, str) and name_value.strip():
        name = name_value.strip()
    return name if name else "project"


def _extract_homepage(
    urls_table: dict[str, str],
    project_table: dict[str, object],
) -> str:
    """Extract homepage URL from urls table or project table."""
    homepage_value = urls_table.get("Homepage")
    homepage_project = project_table.get("homepage")
    return homepage_value or (homepage_project if isinstance(homepage_project, str) else "")


def _determine_shell_command(
    slug: str,
    scripts: dict[str, str],
    name: str,
    import_package: str,
) -> str:
    """Determine the shell command for the project."""
    shell_command = slug.replace("_", "-")
    preferred_entry = _select_cli_entry(
        scripts,
        (slug, name, import_package, import_package.replace("_", "-")),
    )
    if preferred_entry is not None:
        shell_command = preferred_entry[0]
    return shell_command


# ---------------------------------------------------------------------------
# Private helpers -- rendering
# ---------------------------------------------------------------------------


def _quote(value: str) -> str:
    return orjson.dumps(value).decode()


def _render_metadata_module(project: ProjectMetadata) -> str:
    homepage = project.homepage or project.repo_url or ""
    body = f'''"""Static package metadata surfaced to CLI commands and documentation.

Purpose
-------
Expose the current project metadata as simple constants. These values are kept
in sync with ``pyproject.toml`` by development automation (tests, push
pipelines), so runtime code does not query packaging metadata.

Contents
--------
* Module-level constants describing the published package.
* :func:`print_info` rendering the constants for the CLI ``info`` command.

System Role
-----------
Lives in the adapters/platform layer; CLI transports import these constants to
present authoritative project information without invoking packaging APIs.
"""

from __future__ import annotations

import sys

#: Distribution name declared in ``pyproject.toml``.
name = {_quote(project.name)}
#: Human-readable summary shown in CLI help output.
title = {_quote(project.summary)}
#: Current release version pulled from ``pyproject.toml`` by automation.
version = {_quote(project.version)}
#: Repository homepage presented to users.
homepage = {_quote(homepage)}
#: Author attribution surfaced in CLI output.
author = {_quote(project.author_name)}
#: Contact email surfaced in CLI output.
author_email = {_quote(project.author_email)}
#: Console-script name published by the package.
shell_command = {_quote(project.shell_command)}

#: Vendor identifier for lib_layered_config paths (macOS/Windows)
LAYEREDCONF_VENDOR: str = {_quote(project.author_name)}
#: Application display name for lib_layered_config paths (macOS/Windows)
LAYEREDCONF_APP: str = {_quote(_package_name_to_display(project.name))}
#: Configuration slug for lib_layered_config Linux paths and environment variables
LAYEREDCONF_SLUG: str = {_quote(project.shell_command)}


def print_info() -> None:
    """Print the summarised metadata block used by the CLI ``info`` command.

    Why
        Provides a single, auditable rendering function so documentation and
        CLI output always match the system design reference.

    Side Effects
        Writes to ``stdout``.

    Examples
    --------
    >>> print_info()  # doctest: +ELLIPSIS
    Info for {project.name}:
    ...
    """

    fields = [
        ("name", name),
        ("title", title),
        ("version", version),
        ("homepage", homepage),
        ("author", author),
        ("author_email", author_email),
        ("shell_command", shell_command),
    ]
    pad = max(len(label) for label, _ in fields)
    lines = [f"Info for {{name}}:", ""]
    lines.extend(f"    {{label.ljust(pad)}} = {{value}}" for label, value in fields)
    sys.stdout.write("\\n".join(lines) + "\\n")
'''
    return textwrap.dedent(body)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_project_metadata(pyproject: Path = Path("pyproject.toml")) -> ProjectMetadata:
    """Load project metadata from pyproject.toml with caching."""
    path = pyproject.resolve()
    cached = _METADATA_CACHE.get(path)
    if cached is not None:
        return cached

    data = load_pyproject(pyproject)
    project_table = as_str_mapping(data.get("project"))

    # Extract name and slug
    name = _extract_name(project_table, pyproject)
    slug = _normalize_slug(name)

    # Extract description
    description_value = project_table.get("description")
    description = description_value.strip() if isinstance(description_value, str) else ""

    # Extract URLs
    urls_table = _as_str_dict(project_table.get("urls"))
    repo_url = urls_table.get("Repository", "")
    homepage = _extract_homepage(urls_table, project_table)
    repo_host, repo_owner, repo_name = _parse_repo_url(repo_url)

    # Derive package info
    import_package = _derive_import_package(data, name)
    coverage_source = _derive_coverage_source(data, import_package)
    scripts = _derive_scripts(data)

    # Extract other metadata
    version = read_version_from_pyproject(pyproject)
    summary = _extract_summary(project_table, description, name)
    author_name, author_email = _extract_author_info(project_table, repo_owner or name)

    # Determine shell command
    shell_command = _determine_shell_command(slug, scripts, name, import_package)
    metadata_module = (Path("src") / import_package / "__init__conf__.py").resolve()

    meta = ProjectMetadata(
        name=name,
        description=description,
        slug=slug,
        repo_url=repo_url,
        repo_host=repo_host,
        repo_owner=repo_owner,
        repo_name=repo_name,
        homepage=homepage,
        import_package=import_package,
        coverage_source=coverage_source,
        scripts=scripts,
        metadata_module=metadata_module,
        version=version,
        summary=summary,
        author_name=author_name,
        author_email=author_email,
        shell_command=shell_command,
    )
    _METADATA_CACHE[path] = meta
    return meta


def sync_metadata_module(project: ProjectMetadata) -> None:
    """Write ``__init__conf__.py`` so the constants mirror ``pyproject.toml``."""

    content = _render_metadata_module(project)
    module_path = project.metadata_module
    module_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        existing = module_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        existing = ""
    if existing == content:
        return
    module_path.write_text(content, encoding="utf-8")


def read_version_from_pyproject(pyproject: Path = Path("pyproject.toml")) -> str:
    """Read the version string from pyproject.toml."""
    data = load_pyproject(pyproject)
    project_table = as_str_mapping(data.get("project"))
    version_value = project_table.get("version")
    if isinstance(version_value, str) and version_value.strip():
        return version_value.strip()
    text = pyproject.read_text(encoding="utf-8")
    match = _RE_PYPROJECT_VERSION.search(text)
    return match.group(1) if match else ""


_RE_DEPENDENCY_NAME = re.compile(r"^([a-zA-Z0-9][-a-zA-Z0-9._]*)")


def get_dependencies(pyproject: Path = Path("pyproject.toml")) -> list[str]:
    """Extract dependency package names from pyproject.toml.

    Returns a list of normalized package names (without version specifiers).
    Names are normalized by replacing hyphens with underscores for filesystem matching.
    """
    data = load_pyproject(pyproject)
    project_table = as_str_mapping(data.get("project"))
    dependencies_value = project_table.get("dependencies")

    if not isinstance(dependencies_value, list):
        return []

    names: list[str] = []
    for dep in cast(list[object], dependencies_value):
        if isinstance(dep, str):
            match = _RE_DEPENDENCY_NAME.match(dep.strip())
            if match:
                # Normalize: replace hyphens with underscores for filesystem matching
                name = match.group(1).replace("-", "_")
                names.append(name)
    return names
