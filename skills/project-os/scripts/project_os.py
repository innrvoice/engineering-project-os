#!/usr/bin/env python3
"""Bootstrap, adopt, validate, upgrade, and maintain repository-local Project OS state."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable, Sequence


VERSION = "2.0.0"
SCHEMA_VERSION = 3
PROGRAM_RELATIVE_PATH = ".agents/PROGRAM.md"
PACK_NAMES = ("service", "web", "mobile", "data", "delivery")
OVERLAY_NAMES = ("react-native-expo",)
OVERLAY_REQUIREMENTS = {"react-native-expo": {"mobile"}}
PLAN_STATUSES = {"planned", "active", "blocked", "done", "superseded"}
FINDING_STATUSES = {
    "candidate",
    "confirmed",
    "fixed_unverified",
    "verified",
    "accepted_risk",
    "deferred",
    "rejected",
    "merged",
}
FAILURE_STATUSES = {"active", "retired", "replaced"}
COVERAGE_DISPOSITIONS = {"promoted", "merged", "retained_private", "retired"}
RESERVED_TEMPLATE_TOKENS = {
    "__UPDATED_DATE__",
    "__PROJECT_NAME__",
    "__DETECTION_LINES__",
    "__PACK_NAMES__",
    "__OVERLAY_NAMES__",
    "__PROGRAM_INITIATIVE__",
    "__PROGRAM_ID__",
    "__PROGRAM_STARTED_ON__",
    "__PROGRAM_OUTCOME__",
    "__PROGRAM_AUTHORITY__",
    "__PROGRAM_PHASES__",
    "__PROGRAM_EXIT_CONDITIONS__",
    "__PROGRAM_EVIDENCE__",
    "__PROGRAM_COST_BOUNDARY__",
    "__PROGRAM_EXCLUSIONS__",
}
LESSON_HEADING_PATTERN = re.compile(r"^## ([A-Z][A-Z0-9-]*-\d+):\s*(.+?)\s*$")
PRIVATE_KNOWLEDGE_PATTERNS = (
    (re.compile(r"(?:/Users/|/home/|/private/var/|/var/folders/|[A-Za-z]:\\Users\\)"), "private path"),
    (re.compile(r"\b(?:sk-(?:proj-)?|gh[pousr]_|github_pat_|xox[baprs]-|AKIA)[A-Za-z0-9_-]+"), "credential-like token"),
    (re.compile(r"\bAIza[A-Za-z0-9_-]{20,}"), "credential-like token"),
    (re.compile(r"Authorization\s*:\s*Bearer\s+eyJ[A-Za-z0-9_.-]+", re.IGNORECASE), "authorization token"),
    (re.compile(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----"), "private key"),
    (re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE), "email address"),
    (re.compile(r"https?://(?:localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+)(?::\d+)?", re.IGNORECASE), "private URL"),
    (re.compile(r"https?://[^/\s?#]+\.internal(?::\d+)?(?:[/\s?#]|$)", re.IGNORECASE), "private URL"),
    (re.compile(r"[?&](?:token|access_token|signature|x-amz-signature|x-goog-signature)=[^&\s]+", re.IGNORECASE), "signed URL"),
)
SENSITIVE_FIELD_NAMES = {
    "api_key",
    "apikey",
    "access_token",
    "authorization",
    "client_secret",
    "password",
    "passwd",
    "private_key",
    "refresh_token",
    "secret",
}

SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSETS = SKILL_ROOT / "assets"
CORE_TEMPLATE = ASSETS / "templates" / "core"
PROGRAM_TEMPLATE = ASSETS / "templates" / "program" / "PROGRAM.md"
HISTORY_README_TEMPLATE = ASSETS / "templates" / "program" / "history" / "README.md"
PACK_TEMPLATE = ASSETS / "packs"
OVERLAY_TEMPLATE = ASSETS / "overlays"
KNOWLEDGE_TEMPLATE = ASSETS / "knowledge"

DEFAULT_PATHS: dict[str, Any] = {
    "context": ".agents/CONTEXT.md",
    "state": ".agents/STATE.md",
    "plans": ".agents/plans/index.json",
    "findings": ".agents/findings/findings.json",
    "evidence": ".agents/evidence",
    "program": None,
    "history": None,
    "history_index": None,
    "shared_knowledge": ".agents/knowledge/shared/failures.json",
    "project_knowledge": [".agents/knowledge/project/failures.json"],
    "legacy_knowledge": [],
    "knowledge_coverage": None,
}


class ProjectOSError(RuntimeError):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ProjectOSError(f"Missing JSON file: {path}") from error
    except UnicodeDecodeError as error:
        raise ProjectOSError(f"JSON file is not valid UTF-8: {path}") from error
    except json.JSONDecodeError as error:
        raise ProjectOSError(
            f"Invalid JSON in {path}: line {error.lineno}, column {error.colno}: {error.msg}"
        ) from error
    except OSError as error:
        raise ProjectOSError(f"Could not read JSON file {path}: {error}") from error


def atomic_write_text(path: Path, content: str, expected_sha256: str | None = None) -> None:
    """Atomically replace an existing regular file after an optional concurrency check."""
    if path.is_symlink():
        raise ProjectOSError(f"Refusing to replace a symlink: {path}")
    if expected_sha256 is not None:
        if not path.is_file():
            raise ProjectOSError(f"File changed during operation: {path}")
        current_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
        if current_sha256 != expected_sha256:
            raise ProjectOSError(f"File changed during operation: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    original_mode = path.stat().st_mode & 0o7777 if path.exists() else None
    descriptor, raw_temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(raw_temporary)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content.encode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
        if original_mode is not None:
            os.chmod(temporary, original_mode)
        if expected_sha256 is not None:
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected_sha256:
                raise ProjectOSError(f"File changed during operation: {path}")
        os.replace(temporary, path)
    except OSError as error:
        raise ProjectOSError(f"Atomic write failed for {path}: {error}") from error
    finally:
        if temporary.exists():
            temporary.unlink()


def package_metadata(root: Path) -> tuple[dict[str, Any], list[str]]:
    path = root / "package.json"
    if not path.is_file():
        return {}, []
    try:
        value = load_json(path)
    except ProjectOSError:
        return {}, ["package.json exists but is not valid JSON"]

    dependency_names: set[str] = set()
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        dependencies = value.get(key, {})
        if isinstance(dependencies, dict):
            dependency_names.update(str(name).lower() for name in dependencies)
    scripts = value.get("scripts", {})
    script_names = sorted(str(name) for name in scripts) if isinstance(scripts, dict) else []
    return {"dependencies": sorted(dependency_names), "scripts": script_names}, []


def read_small_text(path: Path, limit: int = 250_000) -> str:
    if not path.is_file() or path.stat().st_size > limit:
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def iter_string_values(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from iter_string_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_string_values(item)


def private_material_labels(value: Any) -> list[str]:
    labels: set[str] = set()
    for text in iter_string_values(value):
        for pattern, label in PRIVATE_KNOWLEDGE_PATTERNS:
            if pattern.search(text):
                labels.add(label)
    if any(
        isinstance(key, str) and key.strip().lower().replace("-", "_") in SENSITIVE_FIELD_NAMES
        for key in iter_mapping_keys(value)
    ):
        labels.add("sensitive field name")
    return sorted(labels)


def iter_mapping_keys(value: Any) -> Iterable[Any]:
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from iter_mapping_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_mapping_keys(item)


def any_exists(root: Path, names: Iterable[str]) -> bool:
    return any((root / name).exists() for name in names)


def any_top_level_match(root: Path, patterns: Iterable[str]) -> bool:
    return any(any(root.glob(pattern)) for pattern in patterns)


def detect_repository(root: Path) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        raise ProjectOSError(f"Target is not a directory: {root}")

    signal_candidates = (
        "package.json",
        "tsconfig.json",
        "pnpm-lock.yaml",
        "yarn.lock",
        "package-lock.json",
        "pyproject.toml",
        "requirements.txt",
        "setup.py",
        "Pipfile",
        "uv.lock",
        "poetry.lock",
        "deps.edn",
        "project.clj",
        "bb.edn",
        "shadow-cljs.edn",
        "go.mod",
        "Cargo.toml",
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
        "Package.swift",
        "pubspec.yaml",
        "Gemfile",
        "composer.json",
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        "compose.yml",
        "compose.yaml",
        "eas.json",
        "app.json",
        "app.config.js",
        "app.config.ts",
        "Makefile",
        "justfile",
    )
    signals = [name for name in signal_candidates if (root / name).exists()]
    for directory in (
        ".github/workflows",
        "api",
        "server",
        "services",
        "workers",
        "migrations",
        "ios",
        "android",
        "supabase/functions",
        "supabase/migrations",
    ):
        if (root / directory).exists():
            signals.append(f"{directory}/")

    package, package_warnings = package_metadata(root)
    dependencies = set(package.get("dependencies", []))
    python_text = "\n".join(
        read_small_text(root / name).lower()
        for name in ("pyproject.toml", "requirements.txt", "setup.py")
    )
    clojure_text = "\n".join(
        read_small_text(root / name).lower() for name in ("deps.edn", "project.clj")
    )

    toolchains: list[str] = []
    toolchain_checks = (
        ("javascript-typescript", any_exists(root, ("package.json", "tsconfig.json"))),
        (
            "python",
            any_exists(
                root,
                ("pyproject.toml", "requirements.txt", "setup.py", "Pipfile", "uv.lock"),
            )
            or any_top_level_match(root, ("*.py",)),
        ),
        (
            "clojure",
            any_exists(root, ("deps.edn", "project.clj", "bb.edn", "shadow-cljs.edn")),
        ),
        ("go", (root / "go.mod").exists()),
        ("rust", (root / "Cargo.toml").exists()),
        (
            "java-kotlin",
            any_exists(root, ("pom.xml", "build.gradle", "build.gradle.kts"))
            or any_top_level_match(root, ("*.gradle", "*.gradle.kts")),
        ),
        (
            "swift-objective-c",
            (root / "Package.swift").exists()
            or any_top_level_match(root, ("*.xcodeproj", "*.xcworkspace"))
            or (root / "ios").is_dir(),
        ),
        ("dart", (root / "pubspec.yaml").exists()),
        ("ruby", (root / "Gemfile").exists()),
        ("php", (root / "composer.json").exists()),
        ("dotnet", any_top_level_match(root, ("*.sln", "*.csproj", "*.fsproj"))),
    )
    toolchains.extend(name for name, present in toolchain_checks if present)

    has_react_native = "react-native" in dependencies
    has_expo = "expo" in dependencies
    has_mobile = (
        has_react_native
        or (root / "pubspec.yaml").exists()
        or (root / "ios").is_dir()
        or (root / "android").is_dir()
        or any_top_level_match(root, ("*.xcodeproj", "*.xcworkspace"))
    )

    web_framework_dependencies = {
        "next",
        "vue",
        "nuxt",
        "svelte",
        "@sveltejs/kit",
        "@angular/core",
        "solid-js",
        "astro",
    }
    explicit_web_files = any_exists(
        root,
        ("index.html", "vite.config.js", "vite.config.ts", "next.config.js", "next.config.mjs"),
    )
    has_web = (
        bool(web_framework_dependencies.intersection(dependencies))
        or explicit_web_files
        or ("react-dom" in dependencies and not has_mobile)
    )

    service_dependencies = {
        "express",
        "fastify",
        "koa",
        "hapi",
        "@nestjs/core",
        "django",
        "fastapi",
        "flask",
        "starlette",
        "celery",
    }
    service_markers = ("django", "fastapi", "flask", "starlette", "celery", "gunicorn")
    clojure_service_markers = (
        "metosin/reitit",
        "http-kit/http-kit",
        "ring/ring-core",
        "compojure/compojure",
        "io.pedestal/pedestal.service",
    )
    has_service = (
        bool(service_dependencies.intersection(dependencies))
        or any(marker in python_text for marker in service_markers)
        or any(marker in clojure_text for marker in clojure_service_markers)
        or (root / "supabase" / "functions").is_dir()
        or any(
            (root / name).is_dir()
            for name in ("api", "backend", "server", "services", "workers")
        )
    )

    data_dependencies = {
        "pg",
        "prisma",
        "@prisma/client",
        "typeorm",
        "sequelize",
        "mongoose",
        "sqlalchemy",
        "alembic",
        "diesel",
    }
    clojure_data_markers = (
        "com.github.seancorfield/next.jdbc",
        "org.clojure/java.jdbc",
        "hikari-cp/hikari-cp",
        "com.github.seancorfield/honeysql",
        "com.datomic/",
        "com.xtdb/",
    )
    has_data = (
        bool(data_dependencies.intersection(dependencies))
        or any(marker in python_text for marker in ("sqlalchemy", "alembic", "django"))
        or any(marker in clojure_text for marker in clojure_data_markers)
        or (root / "supabase" / "migrations").is_dir()
        or any((root / name).is_dir() for name in ("migrations", "db", "database", "schema"))
        or any_top_level_match(root, ("*.sql",))
    )

    has_delivery = (
        any_exists(
            root,
            (
                "Dockerfile",
                "docker-compose.yml",
                "docker-compose.yaml",
                "compose.yml",
                "compose.yaml",
                "eas.json",
                "fly.toml",
                "railway.json",
                "railway.toml",
                "vercel.json",
                "netlify.toml",
            ),
        )
        or (root / ".github" / "workflows").is_dir()
        or any((root / name).is_dir() for name in ("terraform", "k8s", "helm"))
    )

    recommended_packs = [
        name
        for name, present in (
            ("service", has_service),
            ("web", has_web),
            ("mobile", has_mobile),
            ("data", has_data),
            ("delivery", has_delivery),
        )
        if present
    ]
    recommended_overlays = ["react-native-expo"] if has_react_native and has_expo else []

    package_manager = None
    for lockfile, manager in (
        ("pnpm-lock.yaml", "pnpm"),
        ("yarn.lock", "yarn"),
        ("package-lock.json", "npm"),
    ):
        if (root / lockfile).exists():
            package_manager = manager
            break

    return {
        "target": str(root),
        "repository": root.name,
        "toolchain_signals": toolchains,
        "recommended_packs": recommended_packs,
        "recommended_overlays": recommended_overlays,
        "signals": sorted(set(signals)),
        "package_manager_signal": package_manager,
        "package_scripts": package.get("scripts", []),
        "warnings": package_warnings,
        "note": (
            "Signals recommend capability packs only. Verify commands, architecture, and product "
            "authority from the repository before recording them."
        ),
    }


def parse_selection(
    value: str,
    detected: Iterable[str],
    allowed: Sequence[str],
    label: str,
) -> list[str]:
    normalized = value.strip().lower()
    if normalized in {"auto", "selected"}:
        detected_set = set(detected)
        return [name for name in allowed if name in detected_set]
    if normalized in {"", "none"}:
        return []
    requested = [part.strip().lower() for part in value.split(",") if part.strip()]
    unknown = sorted(set(requested).difference(allowed))
    if unknown:
        raise ProjectOSError(
            f"Unknown {label}: {', '.join(unknown)}. Allowed: {', '.join(allowed)}"
        )
    requested_set = set(requested)
    return [name for name in allowed if name in requested_set]


def validate_overlay_dependencies(packs: Sequence[str], overlays: Sequence[str]) -> None:
    pack_set = set(packs)
    for overlay in overlays:
        missing = OVERLAY_REQUIREMENTS.get(overlay, set()).difference(pack_set)
        if missing:
            raise ProjectOSError(
                f"Overlay {overlay} requires packs: {', '.join(sorted(missing))}"
            )


def detection_lines(detection: dict[str, Any]) -> str:
    toolchains = detection.get("toolchain_signals", [])
    signals = detection.get("signals", [])
    return "\n".join(
        (
            "- Toolchains: " + (", ".join(toolchains) if toolchains else "none detected"),
            "- Repository signals: "
            + (
                ", ".join(f"`{signal}`" for signal in signals)
                if signals
                else "none detected"
            ),
        )
    )


def render_template(content: str, replacements: dict[str, str]) -> str:
    rendered = content
    for token, value in replacements.items():
        rendered = rendered.replace(token, value)
    return rendered


def iter_template_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if path.is_file():
            yield path


def require_destination_within_root(root: Path, destination: Path) -> None:
    root = root.resolve()
    try:
        destination.resolve().relative_to(root)
        destination.relative_to(root)
    except ValueError as error:
        raise ProjectOSError(f"Refusing to access a path outside the target: {destination}") from error


def reject_symlink_path(root: Path, destination: Path) -> None:
    """Reject a mutation when any destination component is a symlink."""
    root = root.resolve()
    require_destination_within_root(root, destination)
    relative = destination.relative_to(root)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ProjectOSError(f"Refusing to mutate through a symlink: {current}")


def check_no_symlink_path(
    root: Path, path: Path, label: str, errors: list[str]
) -> None:
    try:
        reject_symlink_path(root, path)
    except ProjectOSError as error:
        message = f"{label} must not use symlink components: {error}"
        if message not in errors:
            errors.append(message)


def repo_relative_path(root: Path, raw_path: Any) -> Path | None:
    """Parse a repository-relative POSIX path without accepting traversal syntax."""
    if not isinstance(raw_path, str) or raw_path in {"", ".", ".."} or "\\" in raw_path:
        return None
    pure = PurePosixPath(raw_path)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        return None
    candidate = root.joinpath(*pure.parts)
    try:
        candidate.resolve().relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def safe_relative(root: Path, raw_path: Any) -> Path | None:
    return repo_relative_path(root, raw_path)


def relative_string(root: Path, path: Path | None) -> str | None:
    if path is None:
        return None
    if path.is_symlink():
        return None
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return None


def create_parent_directories(root: Path, parent: Path, created: list[Path]) -> None:
    root = root.resolve()
    require_destination_within_root(root, parent)
    relative = parent.relative_to(root)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ProjectOSError(f"Refusing to create through a symlink: {current}")
        if current.exists():
            if not current.is_dir():
                raise ProjectOSError(f"Expected a directory but found a file: {current}")
            continue
        try:
            current.mkdir()
        except FileExistsError:
            if current.is_symlink() or not current.is_dir():
                raise ProjectOSError(f"Unsafe path appeared during operation: {current}")
        else:
            created.append(current)


def unique_existing(
    root: Path,
    candidates: Sequence[str],
    kind: str,
    label: str,
    errors: list[str],
    prefer_nonempty: bool = False,
) -> Path | None:
    matches: list[Path] = []
    for relative in candidates:
        path = root / relative
        if path.is_symlink():
            errors.append(f"unsafe symlink for {label}: {relative}")
            continue
        if kind == "file" and path.is_file():
            matches.append(path)
        if kind == "dir" and path.is_dir():
            matches.append(path)
    if prefer_nonempty and len(matches) > 1:
        nonempty = [
            path
            for path in matches
            if any(item.is_file() and not item.is_symlink() for item in path.rglob("*"))
        ]
        if len(nonempty) == 1:
            return nonempty[0]
        if nonempty:
            matches = nonempty
    if len(matches) > 1:
        errors.append(
            f"ambiguous {label} owners: "
            + ", ".join(path.relative_to(root).as_posix() for path in matches)
        )
        return None
    return matches[0] if matches else None


def default_system(
    root: Path,
    mode: str,
    installation: str,
    packs: Sequence[str],
    overlays: Sequence[str],
    paths: dict[str, Any],
    active_program: dict[str, Any] | None = None,
) -> dict[str, Any]:
    managed_guidance: dict[str, str] = {
        ".agents/packs/README.md": "sha256:"
        + hashlib.sha256((PACK_TEMPLATE / "README.md").read_bytes()).hexdigest()
    }
    for name in packs:
        relative = f".agents/packs/{name}.md"
        managed_guidance[relative] = (
            "sha256:" + hashlib.sha256((PACK_TEMPLATE / f"{name}.md").read_bytes()).hexdigest()
        )
    for name in overlays:
        relative = f".agents/packs/overlays/{name}.md"
        managed_guidance[relative] = (
            "sha256:" + hashlib.sha256((OVERLAY_TEMPLATE / f"{name}.md").read_bytes()).hexdigest()
        )
    managed_knowledge = {
        entry["id"]: entry_content_hash(entry)
        for entry in seed_documents(packs, overlays)
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "project_os_version": VERSION,
        "mode": mode,
        "active_program": active_program,
        "installation": installation,
        "generated_on": date.today().isoformat(),
        "packs": list(packs),
        "pack_paths": [f".agents/packs/{name}.md" for name in packs],
        "overlays": list(overlays),
        "overlay_paths": [f".agents/packs/overlays/{name}.md" for name in overlays],
        "managed_guidance": managed_guidance,
        "managed_knowledge": dict(sorted(managed_knowledge.items())),
        "toolchain_signals": detect_repository(root)["toolchain_signals"],
        "paths": paths,
    }


def seed_documents(packs: Sequence[str], overlays: Sequence[str]) -> list[dict[str, Any]]:
    selected_packs = set(packs)
    paths = [KNOWLEDGE_TEMPLATE / "core.json"]
    paths.extend(KNOWLEDGE_TEMPLATE / "packs" / f"{name}.json" for name in PACK_NAMES)
    paths.extend(KNOWLEDGE_TEMPLATE / "overlays" / f"{name}.json" for name in overlays)
    missing = [path for path in paths if not path.is_file()]
    if missing:
        raise ProjectOSError(
            "Missing bundled knowledge asset: "
            + ", ".join(path.relative_to(SKILL_ROOT).as_posix() for path in missing)
        )
    entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in paths:
        value = load_json(path)
        source_entries = value.get("entries", []) if isinstance(value, dict) else None
        if not isinstance(source_entries, list):
            raise ProjectOSError(f"Knowledge seed must contain an entries array: {path}")
        for entry in source_entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
                raise ProjectOSError(f"Knowledge seed has an invalid entry: {path}")
            source = entry.get("source", {})
            source_pack = source.get("pack") if isinstance(source, dict) else None
            applies_to = entry.get("applies_to", [])
            selected = (
                path.name == "core.json" and path.parent == KNOWLEDGE_TEMPLATE
            ) or (
                isinstance(source_pack, str)
                and source_pack in {f"overlay/{name}" for name in overlays}
            )
            if path.parent.name == "packs":
                selected = source_pack in selected_packs or bool(
                    isinstance(applies_to, list) and selected_packs.intersection(applies_to)
                )
            if not selected:
                continue
            if entry["id"] in seen:
                raise ProjectOSError(f"Duplicate knowledge seed id {entry['id']}: {path}")
            seen.add(entry["id"])
            entries.append(entry)
    return entries


def composed_knowledge(packs: Sequence[str], overlays: Sequence[str]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "knowledge_version": VERSION,
        "packs": ["core", *packs],
        "overlays": list(overlays),
        "entries": sorted(seed_documents(packs, overlays), key=lambda entry: entry["id"]),
    }


def validate_composed_knowledge(
    value: dict[str, Any], packs: Sequence[str], overlays: Sequence[str]
) -> None:
    """Fail closed before bundled knowledge can be written into a target repository."""
    errors: list[str] = []
    if value.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if value.get("knowledge_version") != VERSION:
        errors.append(f"knowledge_version must be {VERSION}")
    if value.get("packs") != ["core", *packs]:
        errors.append("packs do not match the selected capability packs")
    if value.get("overlays") != list(overlays):
        errors.append("overlays do not match the selected ecosystem overlays")

    required = (
        "id",
        "title",
        "status",
        "applies_to",
        "trigger",
        "mechanism",
        "prevention",
        "verification",
        "boundaries",
        "source",
    )
    entries = value.get("entries")
    check_unique_ids(entries, "bundled knowledge", errors, required, FAILURE_STATUSES)
    allowed_source_packs = {
        "core",
        *PACK_NAMES,
        *(f"overlay/{name}" for name in OVERLAY_NAMES),
    }
    if isinstance(entries, list):
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            entry_id = entry.get("id", f"index {index}")
            for key in ("id", "title", "trigger", "mechanism", "prevention"):
                if not isinstance(entry.get(key), str) or not entry.get(key):
                    errors.append(f"bundled knowledge {entry_id!r} has invalid {key}")
            for key in ("applies_to", "verification", "boundaries"):
                values = entry.get(key)
                if (
                    not isinstance(values, list)
                    or not values
                    or any(not isinstance(item, str) or not item for item in values)
                ):
                    errors.append(f"bundled knowledge {entry_id!r} has invalid {key}")
            source = entry.get("source")
            if not isinstance(source, dict):
                errors.append(f"bundled knowledge {entry_id!r} has invalid source")
                continue
            source_kind = source.get("kind")
            if not isinstance(source_kind, str) or source_kind not in {
                "project-os-pack",
                "incident-derived",
            }:
                errors.append(f"bundled knowledge {entry_id!r} has invalid source kind")
            source_pack = source.get("pack")
            if not isinstance(source_pack, str) or source_pack not in allowed_source_packs:
                errors.append(f"bundled knowledge {entry_id!r} has invalid source pack")
            references = source.get("references")
            if not isinstance(references, list) or any(
                not isinstance(reference, str) or not reference.startswith("https://")
                for reference in references
            ):
                errors.append(f"bundled knowledge {entry_id!r} has invalid source references")
            if source_kind == "project-os-pack" and not references:
                errors.append(f"bundled knowledge {entry_id!r} needs a public source reference")
            if source.get("content_hash") != entry_content_hash(entry):
                errors.append(f"bundled knowledge {entry_id!r} content_hash is stale")

    for label in private_material_labels(value):
        errors.append(f"bundled knowledge contains a {label}")
    if errors:
        raise ProjectOSError("Invalid bundled knowledge: " + "; ".join(errors))


def guidance_operations(
    root: Path,
    packs: Sequence[str],
    overlays: Sequence[str],
) -> list[tuple[str, Path, str | None]]:
    operations: list[tuple[str, Path, str | None]] = []
    readme_source = PACK_TEMPLATE / "README.md"
    readme_destination = root / ".agents" / "packs" / "README.md"
    operations.append(
        ("skip", readme_destination, None)
        if readme_destination.exists()
        else ("create", readme_destination, readme_source.read_text(encoding="utf-8"))
    )
    for name in packs:
        source = PACK_TEMPLATE / f"{name}.md"
        destination = root / ".agents" / "packs" / f"{name}.md"
        operations.append(
            ("skip", destination, None)
            if destination.exists()
            else ("create", destination, source.read_text(encoding="utf-8"))
        )
    for name in overlays:
        source = OVERLAY_TEMPLATE / f"{name}.md"
        destination = root / ".agents" / "packs" / "overlays" / f"{name}.md"
        operations.append(
            ("skip", destination, None)
            if destination.exists()
            else ("create", destination, source.read_text(encoding="utf-8"))
        )
    return operations


def guidance_content_map(packs: Sequence[str], overlays: Sequence[str]) -> dict[str, str]:
    contents = {
        ".agents/packs/README.md": (PACK_TEMPLATE / "README.md").read_text(encoding="utf-8")
    }
    for name in packs:
        contents[f".agents/packs/{name}.md"] = (PACK_TEMPLATE / f"{name}.md").read_text(
            encoding="utf-8"
        )
    for name in overlays:
        contents[f".agents/packs/overlays/{name}.md"] = (
            OVERLAY_TEMPLATE / f"{name}.md"
        ).read_text(encoding="utf-8")
    return contents


def execute_operations(
    root: Path,
    operations: Sequence[tuple[str, Path, str | None]],
    dry_run: bool,
    before_write: Callable[[], None] | None = None,
) -> None:
    seen: set[Path] = set()
    for action, destination, content in operations:
        if action not in {"create", "skip"}:
            raise ProjectOSError(f"Unsupported file operation: {action}")
        require_destination_within_root(root, destination)
        reject_symlink_path(root, destination)
        if destination in seen:
            raise ProjectOSError(f"Duplicate file operation: {destination}")
        seen.add(destination)
        if action == "create" and destination.exists():
            raise ProjectOSError(f"Refusing to overwrite an existing file: {destination}")
        if action == "skip" and not destination.is_file():
            raise ProjectOSError(f"Preserved destination is not a regular file: {destination}")
        if action == "create" and content is None:
            raise ProjectOSError(f"Create operation has no content: {destination}")

    for action, destination, _ in operations:
        print(f"{action}: {destination.relative_to(root)}")
    if dry_run:
        return
    if before_write is not None:
        before_write()

    created_files: list[dict[str, Any]] = []
    created_directories: list[Path] = []
    try:
        for action, destination, content in operations:
            if action == "skip":
                continue
            create_parent_directories(root, destination.parent, created_directories)
            reject_symlink_path(root, destination)
            handle = destination.open("xb")
            record: dict[str, Any] = {
                "path": destination,
                "identity": (os.fstat(handle.fileno()).st_dev, os.fstat(handle.fileno()).st_ino),
                "sha256": None,
            }
            created_files.append(record)
            with handle:
                intended = (content or "").encode("utf-8")
                handle.write(intended)
                handle.flush()
                os.fsync(handle.fileno())
            record["sha256"] = hashlib.sha256(intended).hexdigest()
    except (OSError, ProjectOSError) as error:
        rollback_failures: list[str] = []
        for record in reversed(created_files):
            path = record["path"]
            try:
                if path.is_symlink():
                    raise ProjectOSError("destination became a symlink")
                details = path.stat()
                if (details.st_dev, details.st_ino) != record["identity"]:
                    raise ProjectOSError("destination was concurrently replaced")
                expected = record["sha256"]
                if (
                    isinstance(expected, str)
                    and hashlib.sha256(path.read_bytes()).hexdigest() != expected
                ):
                    raise ProjectOSError("created file was concurrently changed")
                path.unlink()
            except (OSError, ProjectOSError) as rollback_error:
                rollback_failures.append(f"{path}: {rollback_error}")
        for path in reversed(created_directories):
            try:
                path.rmdir()
            except OSError as rollback_error:
                rollback_failures.append(f"{path}: {rollback_error}")
        rollback_note = (
            " rollback incomplete: " + "; ".join(rollback_failures)
            if rollback_failures
            else " created files were rolled back"
        )
        raise ProjectOSError(f"Project OS write failed;{rollback_note}: {error}") from error


def execute_sync_transaction(
    root: Path,
    creates: Sequence[tuple[Path, str | bytes]],
    replacements: Sequence[tuple[Path, str, str]],
    deletions: Sequence[tuple[Path, str]] = (),
    after_write: Callable[[], None] | None = None,
) -> None:
    """Apply a small file transaction with hash-guarded rollback for caught failures."""
    root = root.resolve()
    destinations = (
        [path for path, _ in creates]
        + [path for path, _, _ in replacements]
        + [path for path, _ in deletions]
    )
    if len(destinations) != len(set(destinations)):
        raise ProjectOSError("Sync transaction contains duplicate destinations")
    for path, _ in creates:
        require_destination_within_root(root, path)
        reject_symlink_path(root, path)
        if path.exists():
            raise ProjectOSError(f"File changed during sync: {path}")
    for path, _, expected_sha256 in replacements:
        require_destination_within_root(root, path)
        reject_symlink_path(root, path)
        if not path.is_file():
            raise ProjectOSError(f"File changed during sync: {path}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected_sha256:
            raise ProjectOSError(f"File changed during sync: {path}")
    for path, expected_sha256 in deletions:
        require_destination_within_root(root, path)
        reject_symlink_path(root, path)
        if not path.is_file():
            raise ProjectOSError(f"File changed during sync: {path}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected_sha256:
            raise ProjectOSError(f"File changed during sync: {path}")

    created_files: list[dict[str, Any]] = []
    created_directories: list[Path] = []
    replaced: list[tuple[Path, bytes, str, int, tuple[int, int]]] = []
    deleted: list[tuple[Path, Path]] = []
    try:
        for path, content in creates:
            create_parent_directories(root, path.parent, created_directories)
            intended = content if isinstance(content, bytes) else content.encode("utf-8")
            if isinstance(content, bytes):
                handle = path.open("xb")
                record = {
                    "path": path,
                    "identity": (os.fstat(handle.fileno()).st_dev, os.fstat(handle.fileno()).st_ino),
                    "sha256": None,
                }
                created_files.append(record)
                with handle:
                    handle.write(content)
                    handle.flush()
                    os.fsync(handle.fileno())
            else:
                handle = path.open("xb")
                record = {
                    "path": path,
                    "identity": (os.fstat(handle.fileno()).st_dev, os.fstat(handle.fileno()).st_ino),
                    "sha256": None,
                }
                created_files.append(record)
                with handle:
                    handle.write(intended)
                    handle.flush()
                    os.fsync(handle.fileno())
            record["sha256"] = hashlib.sha256(intended).hexdigest()
        for path, content, expected_sha256 in replacements:
            original = path.read_bytes()
            original_mode = path.stat().st_mode & 0o7777
            replacement_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
            atomic_write_text(path, content, expected_sha256=expected_sha256)
            replacement_details = path.stat()
            replaced.append(
                (
                    path,
                    original,
                    replacement_sha256,
                    original_mode,
                    (replacement_details.st_dev, replacement_details.st_ino),
                )
            )
        for path, expected_sha256 in deletions:
            if hashlib.sha256(path.read_bytes()).hexdigest() != expected_sha256:
                raise ProjectOSError(f"File changed during sync: {path}")
            descriptor, raw_tombstone = tempfile.mkstemp(
                prefix=f".{path.name}.project-os-delete.", dir=path.parent
            )
            os.close(descriptor)
            tombstone = Path(raw_tombstone)
            try:
                os.replace(path, tombstone)
            except OSError:
                tombstone.unlink(missing_ok=True)
                raise
            deleted.append((path, tombstone))
        if after_write is not None:
            after_write()
    except (OSError, ProjectOSError) as error:
        rollback_failures: list[str] = []
        for path, tombstone in reversed(deleted):
            if path.exists() or path.is_symlink():
                rollback_failures.append(
                    f"{path}: destination reappeared; original preserved at {tombstone}"
                )
                continue
            try:
                os.replace(tombstone, path)
            except OSError as rollback_error:
                rollback_failures.append(f"{path}: {rollback_error}")
        for path, original, replacement_sha256, original_mode, replacement_identity in reversed(
            replaced
        ):
            try:
                if path.is_symlink() or not path.is_file():
                    raise ProjectOSError(f"File changed during rollback: {path}")
                details = path.stat()
                if (details.st_dev, details.st_ino) != replacement_identity:
                    raise ProjectOSError(f"File changed during rollback: {path}")
                if hashlib.sha256(path.read_bytes()).hexdigest() != replacement_sha256:
                    raise ProjectOSError(f"File changed during rollback: {path}")
                descriptor, raw_temporary = tempfile.mkstemp(
                    prefix=f".{path.name}.project-os-rollback.", dir=path.parent
                )
                temporary = Path(raw_temporary)
                try:
                    with os.fdopen(descriptor, "wb") as handle:
                        handle.write(original)
                        handle.flush()
                        os.fsync(handle.fileno())
                    os.chmod(temporary, original_mode)
                    os.replace(temporary, path)
                except BaseException:
                    temporary.unlink(missing_ok=True)
                    raise
            except (OSError, ProjectOSError) as rollback_error:
                rollback_failures.append(f"{path}: {rollback_error}")
        for record in reversed(created_files):
            path = record["path"]
            try:
                if path.is_symlink():
                    raise ProjectOSError("destination became a symlink")
                details = path.stat()
                if (details.st_dev, details.st_ino) != record["identity"]:
                    raise ProjectOSError("destination was concurrently replaced")
                expected = record["sha256"]
                if (
                    isinstance(expected, str)
                    and hashlib.sha256(path.read_bytes()).hexdigest() != expected
                ):
                    raise ProjectOSError("created file was concurrently changed")
                path.unlink()
            except (OSError, ProjectOSError) as rollback_error:
                rollback_failures.append(f"{path}: {rollback_error}")
        for path in reversed(created_directories):
            try:
                path.rmdir()
            except OSError:
                pass
        note = (
            " rollback incomplete: " + "; ".join(rollback_failures)
            if rollback_failures
            else " changes were rolled back"
        )
        raise ProjectOSError(f"Project OS transaction failed;{note}: {error}") from error
    for _, tombstone in deleted:
        try:
            tombstone.unlink()
        except OSError as error:
            raise ProjectOSError(f"Project OS transaction committed but cleanup failed: {error}")


def init_project(
    root: Path,
    packs_value: str,
    overlays_value: str,
    dry_run: bool,
    allow_existing_agents: bool = False,
) -> int:
    root = root.resolve()
    detection = detect_repository(root)
    packs = parse_selection(packs_value, detection["recommended_packs"], PACK_NAMES, "packs")
    overlays = parse_selection(
        overlays_value, detection["recommended_overlays"], OVERLAY_NAMES, "overlays"
    )
    validate_overlay_dependencies(packs, overlays)
    system_path = root / ".agents" / "SYSTEM.json"
    if system_path.exists():
        raise ProjectOSError("Project OS is already configured; use check instead of reinitializing")
    agents_path = root / "AGENTS.md"
    agents_exists = agents_path.exists()
    agents_root = root / ".agents"
    if agents_root.is_symlink() or (agents_root.exists() and not agents_root.is_dir()):
        raise ProjectOSError("Existing .agents must be a real directory")
    owned_names = {
        "SYSTEM.json",
        "README.md",
        "CONTEXT.md",
        "STATE.md",
        "PROGRAM.md",
        "plans",
        "findings",
        "evidence",
        "knowledge",
        "packs",
        "history",
    }
    existing_owned = (
        sorted(name for name in owned_names if (agents_root / name).exists())
        if agents_root.is_dir()
        else []
    )
    if existing_owned or (agents_exists and not allow_existing_agents):
        raise ProjectOSError(
            "Existing repository instructions or Project OS-owned .agents state detected; "
            "use adopt instead of init"
        )
    if agents_exists and allow_existing_agents:
        if not agents_path.is_file() or agents_path.is_symlink():
            raise ProjectOSError("Existing AGENTS.md must be a regular file")
        agents_text = agents_path.read_text(encoding="utf-8", errors="ignore")
        required_routes = (".agents/CONTEXT.md", ".agents/STATE.md")
        missing_routes = [route for route in required_routes if route not in agents_text]
        if missing_routes:
            raise ProjectOSError(
                "Existing AGENTS.md must route to "
                + ", ".join(missing_routes)
                + " before --allow-existing-agents can preserve it"
            )

    replacements = {
        "__UPDATED_DATE__": date.today().isoformat(),
        "__PROJECT_NAME__": root.name,
        "__DETECTION_LINES__": detection_lines(detection),
        "__PACK_NAMES__": ", ".join(packs) if packs else "none",
        "__OVERLAY_NAMES__": ", ".join(overlays) if overlays else "none",
    }
    knowledge = composed_knowledge(packs, overlays)
    validate_composed_knowledge(knowledge, packs, overlays)
    operations: list[tuple[str, Path, str | None]] = []
    template_roots = [CORE_TEMPLATE]
    shared_relative = Path(".agents/knowledge/shared/failures.json")
    for template_root in template_roots:
        for source in iter_template_files(template_root):
            relative = source.relative_to(template_root)
            if relative == shared_relative:
                continue
            if relative == Path("AGENTS.md") and agents_exists:
                continue
            destination = root / relative
            operations.append(
                ("skip", destination, None)
                if destination.exists()
                else (
                    "create",
                    destination,
                    render_template(source.read_text(encoding="utf-8"), replacements),
                )
            )

    paths = dict(DEFAULT_PATHS)
    system = default_system(root, "standard", "initialized", packs, overlays, paths)
    operations.extend(guidance_operations(root, packs, overlays))
    shared_destination = root / str(paths["shared_knowledge"])
    operations.append(
        ("skip", shared_destination, None)
        if shared_destination.exists()
        else (
            "create",
            shared_destination,
            json.dumps(knowledge, indent=2, ensure_ascii=False) + "\n",
        )
    )
    operations.append(("create", system_path, json.dumps(system, indent=2) + "\n"))
    execute_operations(root, operations, dry_run)

    if agents_exists:
        print("existing AGENTS.md preserved")
    if dry_run:
        print("dry-run: no files written")
    return 0


def scan_markdown_lessons(root: Path, roots: Sequence[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    occurrences: dict[tuple[str, str, str], int] = {}
    for raw_root in roots:
        lesson_root = safe_relative(root, raw_root)
        if lesson_root is None or not lesson_root.exists() or lesson_root.is_symlink():
            continue
        files = [lesson_root] if lesson_root.is_file() else sorted(lesson_root.rglob("*.md"))
        for path in files:
            if path.is_symlink():
                continue
            try:
                path.resolve().relative_to(root.resolve())
            except ValueError:
                continue
            relative = path.relative_to(root).as_posix()
            for line_number, line in enumerate(
                path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1
            ):
                match = LESSON_HEADING_PATTERN.match(line)
                if not match:
                    continue
                title = match.group(2)
                identity = (relative, match.group(1), title)
                occurrences[identity] = occurrences.get(identity, 0) + 1
                occurrence = occurrences[identity]
                fingerprint = hashlib.sha256(
                    f"{relative}\n{match.group(1)}\n{title}\n{occurrence}".encode("utf-8")
                ).hexdigest()[:16]
                records.append(
                    {
                        "source": relative,
                        "line": line_number,
                        "legacy_id": match.group(1),
                        "title": title,
                        "occurrence": occurrence,
                        "fingerprint": fingerprint,
                    }
                )
    return records


def file_sha256(path: Path) -> str:
    try:
        return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as error:
        raise ProjectOSError(f"Could not hash adoption source: {path}: {error}") from error


def adoption_precondition_snapshot(
    root: Path,
    system: dict[str, Any],
    inventory: Sequence[dict[str, Any]],
    detection: dict[str, Any],
) -> dict[str, Any]:
    """Capture preserved adoption inputs so validation cannot go stale before mutation."""
    root = root.resolve()
    paths = system.get("paths")
    if not isinstance(paths, dict):
        raise ProjectOSError("Adoption SYSTEM paths must contain an object")

    tracked_files = {"AGENTS.md"}
    for key in (
        "context",
        "state",
        "plans",
        "findings",
        "program",
        "history_index",
        "knowledge_coverage",
    ):
        raw_path = paths.get(key)
        if isinstance(raw_path, str):
            tracked_files.add(raw_path)
    project_knowledge = paths.get("project_knowledge", [])
    if not isinstance(project_knowledge, list):
        raise ProjectOSError("Adoption project knowledge paths must be an array")
    tracked_files.update(path for path in project_knowledge if isinstance(path, str))

    file_hashes: dict[str, str] = {}
    for raw_path in sorted(tracked_files):
        path = safe_relative(root, raw_path)
        if path is None:
            raise ProjectOSError(f"Unsafe adoption source path: {raw_path!r}")
        reject_symlink_path(root, path)
        if not path.is_file():
            raise ProjectOSError(f"Missing adoption source file: {raw_path}")
        file_hashes[raw_path] = file_sha256(path)

    history_archives: dict[str, str] = {}
    raw_history = paths.get("history")
    raw_history_index = paths.get("history_index")
    if isinstance(raw_history, str) and isinstance(raw_history_index, str):
        history_path = safe_relative(root, raw_history)
        index_path = safe_relative(root, raw_history_index)
        if history_path is None or index_path is None:
            raise ProjectOSError("Unsafe adoption history paths")
        reject_symlink_path(root, history_path)
        reject_symlink_path(root, index_path)
        try:
            index_bytes = index_path.read_bytes()
        except OSError as error:
            raise ProjectOSError(f"Could not read adoption history index: {error}") from error
        index_digest = "sha256:" + hashlib.sha256(index_bytes).hexdigest()
        if file_hashes.get(raw_history_index) != index_digest:
            raise ProjectOSError("Adoption history index changed during discovery")
        try:
            history_index = json.loads(index_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ProjectOSError("Adoption history index is not valid UTF-8 JSON") from error
        entries = history_index.get("entries") if isinstance(history_index, dict) else None
        if not isinstance(entries, list):
            raise ProjectOSError("Adoption history index must contain an entries array")
        for position, entry in enumerate(entries):
            raw_archive = entry.get("path") if isinstance(entry, dict) else None
            archive_path = safe_relative(root, raw_archive)
            if archive_path is None:
                raise ProjectOSError(
                    f"Adoption history entry {position} has an unsafe path"
                )
            try:
                archive_path.resolve().relative_to(history_path.resolve())
            except ValueError as error:
                raise ProjectOSError(
                    f"Adoption history entry {position} is outside SYSTEM history"
                ) from error
            reject_symlink_path(root, archive_path)
            if not archive_path.is_file():
                raise ProjectOSError(
                    f"Adoption history entry {position} is not a regular file"
                )
            archive_digest = file_sha256(archive_path)
            if not isinstance(entry, dict) or entry.get("sha256") != archive_digest:
                raise ProjectOSError(
                    f"Adoption history entry {position} hash does not match its index"
                )
            if not isinstance(raw_archive, str):
                raise ProjectOSError(
                    f"Adoption history entry {position} has no valid path"
                )
            history_archives[raw_archive] = archive_digest

    directory_paths: list[str] = []
    for key in ("evidence", "history"):
        raw_path = paths.get(key)
        if not isinstance(raw_path, str):
            continue
        path = safe_relative(root, raw_path)
        if path is None:
            raise ProjectOSError(f"Unsafe adoption directory path: {raw_path!r}")
        reject_symlink_path(root, path)
        if not path.is_dir():
            raise ProjectOSError(f"Missing adoption directory: {raw_path}")
        directory_paths.append(raw_path)

    legacy_roots = paths.get("legacy_knowledge", [])
    if not isinstance(legacy_roots, list):
        raise ProjectOSError("Adoption legacy knowledge paths must be an array")
    legacy_hashes: dict[str, str] = {}
    for raw_root in legacy_roots:
        lesson_root = safe_relative(root, raw_root)
        if lesson_root is None:
            raise ProjectOSError(f"Unsafe legacy knowledge path: {raw_root!r}")
        reject_symlink_path(root, lesson_root)
        if not lesson_root.is_dir():
            raise ProjectOSError(f"Missing legacy knowledge directory: {raw_root}")
        directory_paths.append(raw_root)
        for path in sorted(lesson_root.rglob("*.md")):
            reject_symlink_path(root, path)
            if not path.is_file():
                raise ProjectOSError(f"Legacy knowledge path is not a regular file: {path}")
            relative = path.relative_to(root).as_posix()
            legacy_hashes[relative] = file_sha256(path)

    inventory_raw = json.dumps(
        list(inventory), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    detection_snapshot = {
        key: detection.get(key)
        for key in (
            "toolchain_signals",
            "recommended_packs",
            "recommended_overlays",
            "signals",
            "package_manager_signal",
            "package_scripts",
            "warnings",
        )
    }
    return {
        "files": file_hashes,
        "directories": sorted(set(directory_paths)),
        "history_archives": history_archives,
        "legacy_markdown": legacy_hashes,
        "legacy_inventory_sha256": "sha256:" + hashlib.sha256(inventory_raw).hexdigest(),
        "detection": detection_snapshot,
    }


def verify_adoption_preconditions(root: Path, report: dict[str, Any]) -> None:
    expected = report.get("preconditions")
    system = report.get("proposed_system")
    if not isinstance(expected, dict) or not isinstance(system, dict):
        raise ProjectOSError("Adoption report has no valid mutation preconditions")
    paths = system.get("paths")
    if not isinstance(paths, dict):
        raise ProjectOSError("Adoption report has no valid SYSTEM paths")
    refreshed = discover_adoption(root, include_inventory=False)
    current = refreshed.get("preconditions")
    if (
        not refreshed.get("safe_to_adopt")
        or refreshed.get("proposed_system") != system
        or current != expected
    ):
        changed = sorted(
            key
            for key in set(expected).union(current if isinstance(current, dict) else {})
            if expected.get(key)
            != (current.get(key) if isinstance(current, dict) else None)
        )
        if not refreshed.get("safe_to_adopt"):
            changed.append("validation")
        raise ProjectOSError(
            "Adoption sources changed after discovery"
            + (f" ({', '.join(sorted(set(changed)))})" if changed else "")
            + "; rerun the adoption dry run"
        )


def discover_adoption(root: Path, include_inventory: bool = False) -> dict[str, Any]:
    root = root.resolve()
    detection = detect_repository(root)
    errors: list[str] = []
    warnings: list[str] = []
    context = unique_existing(root, (".agents/CONTEXT.md",), "file", "context", errors)
    state = unique_existing(root, (".agents/STATE.md",), "file", "state", errors)
    plans = unique_existing(
        root,
        (".agents/plans/index.json", "docs/plans/index.json"),
        "file",
        "plans",
        errors,
    )
    findings = unique_existing(
        root,
        (
            ".agents/findings/findings.json",
            ".agents/audit/findings.json",
            "docs/audit/findings.json",
        ),
        "file",
        "findings",
        errors,
    )
    evidence = unique_existing(
        root,
        (".agents/evidence", ".agents/audit/evidence", "docs/audit/evidence"),
        "dir",
        "evidence",
        errors,
        prefer_nonempty=True,
    )
    program = unique_existing(root, (".agents/PROGRAM.md",), "file", "program", errors)
    history = unique_existing(root, (".agents/history",), "dir", "history", errors)
    history_index = unique_existing(
        root, (".agents/history/index.json",), "file", "history index", errors
    )
    coverage = unique_existing(
        root,
        (
            ".agents/adoption/knowledge-map.json",
            ".agents/knowledge/coverage.json",
        ),
        "file",
        "knowledge coverage",
        errors,
    )

    knowledge_root = root / ".agents" / "knowledge"
    if knowledge_root.is_symlink():
        errors.append(f"unsafe knowledge root symlink: {knowledge_root}")
    project_knowledge: list[str] = []
    canonical_project = knowledge_root / "project" / "failures.json"
    if canonical_project.is_file():
        project_knowledge.append(relative_string(root, canonical_project) or "")
    if knowledge_root.is_dir():
        for path in sorted(knowledge_root.glob("*.md")):
            if path.name.lower() != "readme.md":
                relative = relative_string(root, path)
                if relative is None:
                    errors.append(f"unsafe project knowledge path: {path}")
                else:
                    project_knowledge.append(relative)
    project_knowledge = [path for path in project_knowledge if path]

    legacy_knowledge: list[str] = []
    if knowledge_root.is_dir():
        for directory in sorted(path for path in knowledge_root.iterdir() if path.is_dir()):
            if directory.name in {"project", "shared"}:
                continue
            if directory.is_symlink():
                errors.append(f"unsafe legacy knowledge symlink: {directory}")
                continue
            if any(directory.rglob("*.md")):
                relative = relative_string(root, directory)
                if relative:
                    legacy_knowledge.append(relative)

    paths = {
        "context": relative_string(root, context),
        "state": relative_string(root, state),
        "plans": relative_string(root, plans),
        "findings": relative_string(root, findings),
        "evidence": relative_string(root, evidence),
        "program": None,
        "history": relative_string(root, history) if history_index is not None else None,
        "history_index": relative_string(root, history_index),
        "shared_knowledge": ".agents/knowledge/shared/failures.json",
        "project_knowledge": project_knowledge,
        "legacy_knowledge": legacy_knowledge,
        "knowledge_coverage": relative_string(root, coverage),
    }
    if program is not None:
        errors.append(
            "existing PROGRAM.md is ambiguous; adoption creates Standard state only"
        )
    if history is not None and history_index is None:
        warnings.append(
            "existing history is preserved but remains unmanaged without history/index.json"
        )
    packs = list(detection["recommended_packs"])
    overlays = list(detection["recommended_overlays"])
    validate_overlay_dependencies(packs, overlays)
    system = default_system(root, "standard", "adopted", packs, overlays, paths)
    validate_system_owner_paths(root, paths, "standard", system.get("managed_guidance"), errors)

    if history is not None and history_index is not None:
        validate_history_index(root, history, history_index, errors)

    if not (root / "AGENTS.md").is_file():
        errors.append("missing root AGENTS.md")
    for owner in ("context", "state", "plans", "findings"):
        if paths[owner] is None:
            errors.append(f"could not discover required {owner} owner")
    if evidence is None:
        warnings.append("no evidence directory was discovered")
    agents_text = read_small_text(root / "AGENTS.md")
    for owner in (context, state):
        if owner is not None:
            relative = relative_string(root, owner)
            if relative and relative not in agents_text:
                errors.append(f"AGENTS.md does not route to {relative}")

    validate_adoption_records(root, paths, errors)
    for raw_path in project_knowledge:
        path = safe_relative(root, raw_path)
        if path is None or not path.is_file():
            errors.append(f"invalid project knowledge path: {raw_path}")
        elif path.suffix == ".json":
            validate_failure_registry(path, f"project knowledge {raw_path}", errors)

    inventory = scan_markdown_lessons(root, legacy_knowledge)
    counts: dict[str, int] = {}
    for record in inventory:
        counts[record["legacy_id"]] = counts.get(record["legacy_id"], 0) + 1
    duplicates = sorted(identifier for identifier, count in counts.items() if count > 1)
    if inventory and coverage is None:
        errors.append("legacy knowledge requires an explicit complete coverage map")
    elif coverage is not None:
        coverage_errors: list[str] = []
        shared_targets = {
            entry["id"]: entry["source"]["pack"]
            for entry in composed_knowledge(packs, overlays)["entries"]
        }
        validate_knowledge_coverage(root, inventory, coverage, shared_targets, coverage_errors)
        errors.extend(coverage_errors)
    if duplicates:
        warnings.append("legacy knowledge duplicate ids are resolved only by source fingerprint")

    managed_destinations = [
        ".agents/packs/README.md",
        ".agents/knowledge/shared/failures.json",
        *(f".agents/packs/{name}.md" for name in packs),
        *(f".agents/packs/overlays/{name}.md" for name in overlays),
    ]
    for relative in managed_destinations:
        if (root / relative).exists():
            errors.append(f"Project OS-managed adoption destination already exists: {relative}")
    for relative in [*managed_destinations, ".agents/SYSTEM.json"]:
        try:
            reject_symlink_path(root, root / relative)
        except ProjectOSError as error:
            errors.append(str(error))

    planned_creates = [".agents/SYSTEM.json"]
    planned_creates.extend(f".agents/packs/{name}.md" for name in packs)
    planned_creates.extend(f".agents/packs/overlays/{name}.md" for name in overlays)
    planned_creates.extend((".agents/packs/README.md", ".agents/knowledge/shared/failures.json"))
    planned_creates = [relative for relative in planned_creates if not (root / relative).exists()]

    preconditions: dict[str, Any] | None = None
    if not errors:
        try:
            preconditions = adoption_precondition_snapshot(root, system, inventory, detection)
        except ProjectOSError as error:
            errors.append(str(error))

    report: dict[str, Any] = {
        "target": str(root),
        "safe_to_adopt": not errors,
        "errors": errors,
        "warnings": warnings,
        "planned_creates": sorted(set(planned_creates)),
        "existing_files_modified": [],
        "legacy_knowledge_count": len(inventory),
        "legacy_duplicate_ids": duplicates,
        "proposed_system": system,
        "preconditions": preconditions,
    }
    if include_inventory:
        report["legacy_knowledge_inventory"] = inventory
    return report


def adopt_project(root: Path, dry_run: bool, include_inventory: bool) -> int:
    root = root.resolve()
    system_path = root / ".agents" / "SYSTEM.json"
    if system_path.exists():
        raise ProjectOSError("Project OS is already configured; use check instead of adopt")
    report = discover_adoption(root, include_inventory=include_inventory)
    proposed = report["proposed_system"]
    knowledge = composed_knowledge(proposed["packs"], proposed["overlays"])
    validate_composed_knowledge(knowledge, proposed["packs"], proposed["overlays"])
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not report["safe_to_adopt"]:
        return 1
    if dry_run:
        print("dry-run: no files written")
        return 0

    system = report["proposed_system"]
    operations = [
        ("create", root / raw_path, content)
        for raw_path, content in guidance_content_map(
            system["packs"], system["overlays"]
        ).items()
    ]
    shared_destination = root / system["paths"]["shared_knowledge"]
    operations.append(
        (
            "create",
            shared_destination,
            json.dumps(knowledge, indent=2, ensure_ascii=False) + "\n",
        )
    )
    operations.append(("create", system_path, json.dumps(system, indent=2) + "\n"))
    execute_operations(
        root,
        operations,
        dry_run=False,
        before_write=lambda: verify_adoption_preconditions(root, report),
    )
    print("adopted: existing files were preserved")
    return 0


def check_unique_ids(
    entries: Any,
    label: str,
    errors: list[str],
    required: Iterable[str],
    allowed_statuses: set[str] | None = None,
) -> set[str]:
    identifiers: set[str] = set()
    if not isinstance(entries, list):
        errors.append(f"{label} must be an array")
        return identifiers
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"{label}[{index}] must be an object")
            continue
        missing = [key for key in required if key not in entry]
        if missing:
            errors.append(f"{label}[{index}] is missing: {', '.join(missing)}")
        entry_id = entry.get("id")
        if not isinstance(entry_id, str) or not entry_id:
            errors.append(f"{label}[{index}] has no valid id")
        elif entry_id in identifiers:
            errors.append(f"{label} contains duplicate id {entry_id}")
        else:
            identifiers.add(entry_id)
        status = entry.get("status")
        if allowed_statuses is not None and (
            not isinstance(status, str) or status not in allowed_statuses
        ):
            errors.append(f"{label}[{index}] has invalid status {entry.get('status')!r}")
    return identifiers


def entry_content_hash(entry: dict[str, Any]) -> str:
    value = copy.deepcopy(entry)
    source = value.get("source")
    if isinstance(source, dict):
        source.pop("content_hash", None)
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def validate_registry_schema(value: dict[str, Any], label: str, errors: list[str]) -> None:
    versions = [value[key] for key in ("schema_version", "version") if key in value]
    if not versions:
        errors.append(f"{label} must declare schema_version or version")
    elif any(version != 1 for version in versions):
        errors.append(f"{label} schema version must be 1")


def system_path_value(
    root: Path,
    paths: dict[str, Any],
    key: str,
    errors: list[str],
    required: bool = False,
) -> Path | None:
    raw = paths.get(key)
    if raw is None:
        if required:
            errors.append(f"SYSTEM paths.{key} is required")
        return None
    path = safe_relative(root, raw)
    if path is None:
        errors.append(f"SYSTEM paths.{key} is not a safe repository-relative path: {raw!r}")
    return path


def validate_system_owner_paths(
    root: Path,
    paths: dict[str, Any],
    mode: Any,
    managed_guidance: Any,
    errors: list[str],
) -> None:
    """Require distinct file owners and reject unsafe directory ownership overlap."""
    raw_program = paths.get("program")
    if mode == "program" and raw_program != PROGRAM_RELATIVE_PATH:
        errors.append(
            f"Program mode requires SYSTEM paths.program to be {PROGRAM_RELATIVE_PATH}"
        )
    if mode == "standard" and raw_program is not None:
        errors.append("Standard mode requires SYSTEM paths.program to be null")

    def normalized(raw_path: str) -> str:
        return PurePosixPath(raw_path).as_posix().casefold()

    physical_file_owners: list[tuple[str, str]] = [
        ("AGENTS.md", "AGENTS.md"),
        ("SYSTEM manifest", ".agents/SYSTEM.json"),
    ]
    file_owners: list[tuple[str, str]] = [
        ("AGENTS.md", normalized("AGENTS.md")),
        ("SYSTEM manifest", normalized(".agents/SYSTEM.json")),
    ]
    for key in (
        "context",
        "state",
        "plans",
        "findings",
        "program",
        "history_index",
        "shared_knowledge",
        "knowledge_coverage",
    ):
        raw_path = paths.get(key)
        if isinstance(raw_path, str):
            physical_file_owners.append((f"paths.{key}", raw_path))
            file_owners.append((f"paths.{key}", normalized(raw_path)))
    project_knowledge = paths.get("project_knowledge")
    if isinstance(project_knowledge, list):
        physical_file_owners.extend(
            (f"paths.project_knowledge[{index}]", raw_path)
            for index, raw_path in enumerate(project_knowledge)
            if isinstance(raw_path, str)
        )
        file_owners.extend(
            (f"paths.project_knowledge[{index}]", normalized(raw_path))
            for index, raw_path in enumerate(project_knowledge)
            if isinstance(raw_path, str)
        )
    if isinstance(managed_guidance, dict):
        physical_file_owners.extend(
            (f"managed_guidance[{raw_path}]", raw_path)
            for raw_path in managed_guidance
            if isinstance(raw_path, str)
        )
        file_owners.extend(
            (f"managed_guidance[{raw_path}]", normalized(raw_path))
            for raw_path in managed_guidance
            if isinstance(raw_path, str)
        )

    owners_by_path: dict[str, list[str]] = {}
    for label, raw_path in file_owners:
        owners_by_path.setdefault(raw_path, []).append(label)
    for raw_path, labels in owners_by_path.items():
        if len(labels) > 1:
            errors.append(
                f"Project OS file owner collision at {raw_path}: {', '.join(labels)}"
            )

    owners_by_identity: dict[tuple[int, int], list[str]] = {}
    for label, raw_path in physical_file_owners:
        candidate = safe_relative(root, raw_path)
        if candidate is None:
            continue
        try:
            details = candidate.stat()
        except OSError:
            continue
        owners_by_identity.setdefault((details.st_dev, details.st_ino), []).append(label)
    for labels in owners_by_identity.values():
        if len(labels) > 1:
            errors.append(
                "Project OS file owners reference the same existing file: "
                + ", ".join(labels)
            )

    directory_owners: list[tuple[str, str]] = []
    for key in ("evidence", "history"):
        raw_path = paths.get(key)
        if isinstance(raw_path, str):
            directory_owners.append((f"paths.{key}", normalized(raw_path)))
    legacy_knowledge = paths.get("legacy_knowledge")
    if isinstance(legacy_knowledge, list):
        directory_owners.extend(
            (f"paths.legacy_knowledge[{index}]", normalized(raw_path))
            for index, raw_path in enumerate(legacy_knowledge)
            if isinstance(raw_path, str)
        )

    def contains(parent: str, child: str) -> bool:
        parent_parts = PurePosixPath(parent).parts
        child_parts = PurePosixPath(child).parts
        return (
            len(child_parts) > len(parent_parts)
            and child_parts[: len(parent_parts)] == parent_parts
        )

    for left_index, (left_label, left_path) in enumerate(directory_owners):
        for right_label, right_path in directory_owners[left_index + 1 :]:
            if left_path == right_path or contains(left_path, right_path) or contains(
                right_path, left_path
            ):
                errors.append(
                    "Project OS directory owner overlap: "
                    f"{left_label} ({left_path}) and {right_label} ({right_path})"
                )

    raw_history = paths.get("history")
    raw_history_index = paths.get("history_index")
    if (
        isinstance(raw_history, str)
        and isinstance(raw_history_index, str)
        and not contains(raw_history, raw_history_index)
    ):
        errors.append("SYSTEM paths.history_index must be inside paths.history")

    for file_label, file_path in file_owners:
        for directory_label, directory_path in directory_owners:
            if file_path != directory_path and not contains(directory_path, file_path):
                continue
            if file_label == "paths.history_index" and directory_label == "paths.history":
                continue
            errors.append(
                f"Project OS owner overlap: {file_label} ({file_path}) is owned by "
                f"{directory_label} ({directory_path})"
            )


def require_safe_system_owners(root: Path, system: dict[str, Any]) -> None:
    paths = system.get("paths")
    if not isinstance(paths, dict):
        raise ProjectOSError("SYSTEM paths must contain an object")
    errors: list[str] = []
    validate_system_owner_paths(
        root, paths, system.get("mode"), system.get("managed_guidance"), errors
    )
    if errors:
        raise ProjectOSError("Unsafe Project OS owners: " + "; ".join(errors))


def require_canonical_program_owner(root: Path, system: dict[str, Any]) -> Path:
    require_safe_system_owners(root, system)
    paths = system["paths"]
    if paths.get("program") != PROGRAM_RELATIVE_PATH:
        raise ProjectOSError(
            f"Program lifecycle requires SYSTEM paths.program to be {PROGRAM_RELATIVE_PATH}"
        )
    program_path = safe_relative(root, paths.get("program"))
    if program_path is None:
        raise ProjectOSError("SYSTEM Program path is unsafe")
    return program_path


def validate_failure_registry(
    path: Path,
    label: str,
    errors: list[str],
    verify_hashes: bool = True,
    strict_managed: bool = False,
) -> set[str]:
    required = (
        "id",
        "title",
        "status",
        "applies_to",
        "trigger",
        "mechanism",
        "prevention",
        "verification",
        "boundaries",
        "source",
    )
    try:
        value = load_json(path)
    except ProjectOSError as error:
        errors.append(str(error))
        return set()
    entries = value.get("entries", []) if isinstance(value, dict) else None
    identifiers = check_unique_ids(entries, label, errors, required, FAILURE_STATUSES)
    if isinstance(value, dict):
        validate_registry_schema(value, label, errors)
    if isinstance(entries, list):
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            source = entry.get("source")
            source_kind = source.get("kind") if isinstance(source, dict) else None
            if strict_managed:
                if not isinstance(source, dict):
                    errors.append(f"{label}[{index}] source must be an object")
                    continue
                if not isinstance(source_kind, str) or source_kind not in {
                    "project-os-pack",
                    "incident-derived",
                }:
                    errors.append(f"{label}[{index}] has invalid managed source kind")
                    continue
                source_pack = source.get("pack")
                if not isinstance(source_pack, str) or source_pack not in {
                    "core",
                    *PACK_NAMES,
                    *(f"overlay/{name}" for name in OVERLAY_NAMES),
                }:
                    errors.append(f"{label}[{index}] has invalid managed source pack")
                references = source.get("references")
                if not isinstance(references, list) or any(
                    not isinstance(reference, str) or not reference.startswith("https://")
                    for reference in references
                ):
                    errors.append(f"{label}[{index}] has invalid source references")
                if source_kind == "project-os-pack" and not references:
                    errors.append(f"{label}[{index}] needs a public source reference")
            if (
                not verify_hashes
                or not isinstance(source_kind, str)
                or source_kind not in {"project-os-pack", "incident-derived"}
            ):
                continue
            stored_hash = source.get("content_hash")
            if stored_hash != entry_content_hash(entry):
                errors.append(f"{label}[{index}] content_hash does not match its content")
    return identifiers


def validate_adoption_records(root: Path, paths: dict[str, Any], errors: list[str]) -> None:
    for key, maximum in (("context", 150), ("state", 80)):
        path = safe_relative(root, paths.get(key))
        if path is not None and path.is_file():
            lines = len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
            if lines > maximum:
                errors.append(f"{path.relative_to(root)} has {lines} lines; maximum is {maximum}")

    plans_path = safe_relative(root, paths.get("plans"))
    if plans_path is not None and plans_path.is_file():
        try:
            value = load_json(plans_path)
        except ProjectOSError as error:
            errors.append(str(error))
        else:
            if not isinstance(value, dict):
                errors.append("plans index must contain an object")
            else:
                validate_registry_schema(value, "plans index", errors)
                plans = value.get("plans", [])
                check_unique_ids(plans, "plans", errors, ("id", "status", "path", "outcome"))
                active_ids: list[str] = []
                if isinstance(plans, list):
                    for plan in plans:
                        if not isinstance(plan, dict):
                            continue
                        identifier = plan.get("id")
                        status = plan.get("status")
                        if not isinstance(status, str) or status not in PLAN_STATUSES:
                            errors.append(f"plan {identifier!r} has invalid status {status!r}")
                        if status == "active" and isinstance(identifier, str):
                            active_ids.append(identifier)
                        plan_path = safe_relative(root, plan.get("path"))
                        if plan_path is None or not plan_path.is_file():
                            errors.append(f"plan {identifier!r} has an invalid or missing path")
                        else:
                            lines = len(
                                plan_path.read_text(encoding="utf-8", errors="ignore").splitlines()
                            )
                            if lines > 200:
                                errors.append(
                                    f"plan {identifier!r} has {lines} lines; maximum is 200"
                                )
                execution_state = value.get("execution_state")
                if execution_state == "running" and len(active_ids) != 1:
                    errors.append("running execution requires exactly one active plan")
                elif execution_state == "idle" and active_ids:
                    errors.append("idle execution requires no active plan")
                elif not isinstance(execution_state, str) or execution_state not in {
                    "running",
                    "idle",
                }:
                    errors.append("execution_state must be idle or running")
                if "active_plan" in value:
                    expected_active = active_ids[0] if len(active_ids) == 1 else None
                    if value.get("active_plan") != expected_active:
                        errors.append("active_plan must match the derived active plan when present")

    findings_path = safe_relative(root, paths.get("findings"))
    if findings_path is not None and findings_path.is_file():
        try:
            value = load_json(findings_path)
        except ProjectOSError as error:
            errors.append(str(error))
        else:
            if not isinstance(value, dict):
                errors.append("findings registry must contain an object")
            else:
                validate_registry_schema(value, "findings registry", errors)
                findings = value.get("findings", [])
                check_unique_ids(
                    findings,
                    "findings",
                    errors,
                    ("id", "status", "impact", "evidence", "required_check"),
                    FINDING_STATUSES,
                )
                if isinstance(findings, list):
                    for finding in findings:
                        if not isinstance(finding, dict):
                            continue
                        evidence = finding.get("evidence", [])
                        if not isinstance(evidence, list):
                            errors.append(
                                f"finding {finding.get('id')!r} evidence must be an array"
                            )
                            continue
                        for raw_path in evidence:
                            evidence_path = safe_relative(root, raw_path)
                            if evidence_path is None or not evidence_path.exists():
                                errors.append(
                                    f"finding {finding.get('id')!r} has invalid or missing evidence"
                                )


def validate_knowledge_coverage(
    root: Path,
    inventory: Sequence[dict[str, Any]],
    coverage_path: Path,
    shared_targets: dict[str, str],
    errors: list[str],
) -> None:
    try:
        value = load_json(coverage_path)
    except ProjectOSError as error:
        errors.append(str(error))
        return
    if not isinstance(value, dict):
        errors.append("knowledge coverage must contain an object")
        return
    if value.get("schema_version") != 1:
        errors.append("knowledge coverage schema_version must be 1")
    entries = value.get("entries", [])
    if not isinstance(entries, list):
        errors.append("knowledge coverage entries must be an array")
        return
    expected: dict[str, dict[str, Any]] = {}
    for record in inventory:
        fingerprint = record["fingerprint"]
        if fingerprint in expected:
            errors.append(f"legacy inventory contains duplicate fingerprint {fingerprint}")
        expected[fingerprint] = record
    expected_sources = sorted({record["source"] for record in inventory})
    sources = value.get("sources", [])
    if not isinstance(sources, list):
        errors.append("knowledge coverage sources must be an array")
        sources = []
    seen_sources: set[str] = set()
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"knowledge coverage source {index} must be an object")
            continue
        raw_path = source.get("path")
        path = safe_relative(root, raw_path)
        if path is None or not path.is_file():
            errors.append(f"knowledge coverage source {index} has an invalid path")
            continue
        if raw_path in seen_sources:
            errors.append(f"knowledge coverage duplicates source {raw_path}")
            continue
        seen_sources.add(raw_path)
        expected_hash = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        if source.get("sha256") != expected_hash:
            errors.append(f"knowledge coverage source hash drifted: {raw_path}")
    if sorted(seen_sources) != expected_sources:
        missing_sources = sorted(set(expected_sources).difference(seen_sources))
        extra_sources = sorted(seen_sources.difference(expected_sources))
        if missing_sources:
            errors.append(
                "knowledge coverage is missing source hashes: " + ", ".join(missing_sources)
            )
        if extra_sources:
            errors.append(
                "knowledge coverage has unrelated source hashes: " + ", ".join(extra_sources)
            )

    seen: set[str] = set()
    canonical_seen: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"knowledge coverage entry {index} must be an object")
            continue
        fingerprint = entry.get("fingerprint")
        if not isinstance(fingerprint, str) or fingerprint not in expected:
            errors.append(f"knowledge coverage entry {index} has an unknown fingerprint")
            continue
        if fingerprint in seen:
            errors.append(f"knowledge coverage duplicates fingerprint {fingerprint}")
            continue
        seen.add(fingerprint)
        record = expected[fingerprint]
        for key in ("source", "legacy_id", "title", "occurrence"):
            if entry.get(key) != record[key]:
                errors.append(f"knowledge coverage {fingerprint} does not match source {key}")
        disposition = entry.get("disposition")
        if not isinstance(disposition, str) or disposition not in COVERAGE_DISPOSITIONS:
            errors.append(
                f"knowledge coverage {fingerprint} has invalid disposition {disposition!r}"
            )
        canonical_id = entry.get("canonical_id")
        if isinstance(disposition, str) and disposition in {"promoted", "merged"}:
            if not isinstance(canonical_id, str) or canonical_id not in shared_targets:
                errors.append(
                    f"knowledge coverage {fingerprint} references missing shared id {canonical_id!r}"
                )
            else:
                expected_target = shared_targets[canonical_id]
                if entry.get("target") != expected_target:
                    errors.append(
                        f"knowledge coverage {fingerprint} target must be {expected_target}"
                    )
            if isinstance(canonical_id, str) and canonical_id in shared_targets and disposition == "promoted":
                if canonical_id in canonical_seen:
                    errors.append(f"knowledge coverage duplicates canonical id {canonical_id}")
                canonical_seen.add(canonical_id)
        if disposition == "retained_private" and entry.get("target") != "project":
            errors.append(
                f"knowledge coverage {fingerprint} retained_private target must be project"
            )
        if disposition == "retired" and not entry.get("reason"):
            errors.append(f"knowledge coverage {fingerprint} retired entry needs a reason")
    missing = sorted(set(expected).difference(seen))
    extra = sorted(seen.difference(expected))
    if missing:
        errors.append(f"knowledge coverage is missing {len(missing)} source lessons")
    if extra:
        errors.append(f"knowledge coverage has {len(extra)} unknown source lessons")
    if value.get("source_count") != len(inventory):
        errors.append("knowledge coverage source_count does not match legacy inventory")
    if value.get("mapped_source_count") != len(seen):
        errors.append("knowledge coverage mapped_source_count does not match entries")


def validate_history_index(
    root: Path,
    history_path: Path,
    index_path: Path,
    errors: list[str],
) -> None:
    """Validate tamper-evident history entries against their recorded SHA-256 values."""
    try:
        value = load_json(index_path)
    except ProjectOSError as error:
        errors.append(str(error))
        return
    if not isinstance(value, dict):
        errors.append("history index must contain an object")
        return
    if value.get("schema_version") != 1:
        errors.append("history index schema_version must be 1")
    entries = value.get("entries")
    if not isinstance(entries, list):
        errors.append("history index entries must be an array")
        return

    identifiers: set[str] = set()
    indexed_paths: set[str] = set()
    for position, entry in enumerate(entries):
        label = f"history index entry {position}"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be an object")
            continue
        entry_id = entry.get("id")
        if not isinstance(entry_id, str) or not entry_id:
            errors.append(f"{label} has no valid id")
        elif entry_id in identifiers:
            errors.append(f"history index contains duplicate id {entry_id}")
        else:
            identifiers.add(entry_id)
        kind = entry.get("kind")
        if not isinstance(kind, str) or kind not in {"program", "snapshot"}:
            errors.append(f"{label} has invalid kind {kind!r}")
        raw_path = entry.get("path")
        path = safe_relative(root, raw_path)
        if path is None:
            errors.append(f"{label} has an unsafe path")
            continue
        try:
            path.resolve().relative_to(history_path.resolve())
        except ValueError:
            errors.append(f"{label} path is outside SYSTEM history")
            continue
        if path == index_path:
            errors.append(f"{label} cannot reference the history index itself")
            continue
        if isinstance(raw_path, str) and raw_path in indexed_paths:
            errors.append(f"history index contains duplicate path {raw_path}")
        elif isinstance(raw_path, str):
            indexed_paths.add(raw_path)
        check_no_symlink_path(root, path, label, errors)
        if not path.is_file():
            errors.append(f"{label} references a missing file: {raw_path}")
            continue
        expected_hash = entry.get("sha256")
        actual_hash = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        if expected_hash != actual_hash:
            errors.append(f"history snapshot hash mismatch: {raw_path}")
        if kind == "program":
            if not isinstance(entry_id, str) or not re.fullmatch(
                r"program-\d{8}-\d{3,}", entry_id
            ):
                errors.append(f"{label} has an invalid Program id")
            elif path != history_path / "programs" / entry_id / "PROGRAM.md":
                errors.append(f"{label} path does not match its Program id")
            disposition = entry.get("disposition")
            if not isinstance(disposition, str) or disposition not in {
                "completed",
                "stopped",
            }:
                errors.append(f"{label} has invalid program disposition")
            try:
                canonical_date(entry.get("closed_on"), f"{label} closed_on")
            except ProjectOSError as error:
                errors.append(str(error))
            if disposition == "stopped" and (
                not isinstance(entry.get("reason"), str) or not entry.get("reason", "").strip()
            ):
                errors.append(f"{label} stopped Program requires a non-empty reason")


def markdown_section(text: str, heading: str) -> str | None:
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)", text
    )
    return match.group(1).strip() if match else None


def validate_created_program_contract(
    program_text: str, active_program: dict[str, Any], errors: list[str]
) -> None:
    initiative = active_program.get("initiative")
    program_id = active_program.get("id")
    started_on = active_program.get("started_on")
    lines = program_text.splitlines()
    expected_metadata = {
        0: f"# Program: {initiative}",
        2: f"Program ID: {program_id}.",
        3: f"Started: {started_on}.",
        4: "Status: active.",
    }
    for line_index, expected in expected_metadata.items():
        if len(lines) <= line_index or lines[line_index] != expected:
            errors.append(f"PROGRAM.md metadata does not match SYSTEM: {expected}")

    sections = {
        heading: markdown_section(program_text, heading)
        for heading in (
            "Outcome",
            "Authority",
            "Phases",
            "Exit conditions",
            "Evidence requirements",
            "Cost boundary",
            "Exclusions",
        )
    }
    for heading, content in sections.items():
        if not content:
            errors.append(f"PROGRAM.md section must be non-empty: {heading}")

    for heading in (
        "Authority",
        "Exit conditions",
        "Evidence requirements",
        "Cost boundary",
        "Exclusions",
    ):
        content = sections.get(heading)
        if content and not any(line.startswith("- ") and line[2:].strip() for line in content.splitlines()):
            errors.append(f"PROGRAM.md section requires a non-empty list: {heading}")

    phases = sections.get("Phases")
    if not phases:
        return
    matches = list(re.finditer(r"(?m)^### ([1-9]\d*)\. (\S.*?)\s*$", phases))
    if len(matches) < 2:
        errors.append("PROGRAM.md requires at least two phases")
        return
    if [int(match.group(1)) for match in matches] != list(range(1, len(matches) + 1)):
        errors.append("PROGRAM.md phase numbers must be contiguous from 1")
    for index, match in enumerate(matches):
        body_end = matches[index + 1].start() if index + 1 < len(matches) else len(phases)
        body = phases[match.end() : body_end].strip()
        marker = "Phase exit conditions:"
        if marker not in body:
            errors.append(f"PROGRAM.md phase {index + 1} is missing exit conditions")
            continue
        outcome, conditions = body.split(marker, 1)
        if not outcome.strip():
            errors.append(f"PROGRAM.md phase {index + 1} outcome must be non-empty")
        if not any(
            line.startswith("- ") and line[2:].strip()
            for line in conditions.splitlines()
        ):
            errors.append(f"PROGRAM.md phase {index + 1} exit conditions must be non-empty")


def validate_active_program(
    program_path: Path | None, active_program: Any, errors: list[str]
) -> None:
    if not isinstance(active_program, dict):
        errors.append("Program mode requires SYSTEM active_program to be an object")
        return
    for key in ("id", "initiative", "origin"):
        if not isinstance(active_program.get(key), str) or not active_program.get(key):
            errors.append(f"SYSTEM active_program.{key} must be a non-empty string")
    program_id = active_program.get("id")
    if not isinstance(program_id, str) or not re.fullmatch(
        r"program-\d{8}-\d{3,}", program_id
    ):
        errors.append("SYSTEM active_program.id has an invalid format")
    origin = active_program.get("origin")
    if not isinstance(origin, str) or origin not in {"created", "legacy-migration"}:
        errors.append("SYSTEM active_program.origin must be created or legacy-migration")
        return
    if origin == "created":
        try:
            canonical_date(active_program.get("started_on"), "SYSTEM active_program.started_on")
        except ProjectOSError as error:
            errors.append(str(error))
        if program_path is not None and program_path.is_file():
            validate_created_program_contract(
                program_path.read_text(encoding="utf-8", errors="ignore"),
                active_program,
                errors,
            )
    else:
        if active_program.get("started_on") is not None:
            errors.append("Legacy-migration active_program.started_on must be null")
        try:
            canonical_date(
                active_program.get("migrated_on"), "SYSTEM active_program.migrated_on"
            )
        except ProjectOSError as error:
            errors.append(str(error))

def check_project(root: Path, config: Path | None = None) -> int:
    root = root.resolve()
    errors: list[str] = []
    config_path = config.resolve() if config else root / ".agents" / "SYSTEM.json"
    if config is None:
        check_no_symlink_path(root, config_path, "SYSTEM manifest", errors)
    try:
        loaded_system = load_json(config_path)
    except ProjectOSError as error:
        print("Project OS check: FAIL")
        print(f"error: {error}")
        return 1
    if not isinstance(loaded_system, dict):
        print("Project OS check: FAIL")
        print("error: SYSTEM configuration must contain an object")
        return 1
    system = loaded_system

    if system.get("schema_version") != SCHEMA_VERSION:
        errors.append(
            f"SYSTEM schema_version must be {SCHEMA_VERSION}, got {system.get('schema_version')!r}"
        )
    if system.get("project_os_version") != VERSION:
        errors.append(
            "SYSTEM project_os_version must match the installed Project OS version "
            f"{VERSION!r}, got {system.get('project_os_version')!r}; run the Project OS "
            "upgrade workflow with `$project-os upgrade`"
        )
    mode = system.get("mode")
    if not isinstance(mode, str) or mode not in {"standard", "program"}:
        errors.append(f"SYSTEM mode must be standard or program, got {mode!r}")
    installation = system.get("installation")
    if not isinstance(installation, str) or installation not in {"initialized", "adopted"}:
        errors.append(f"SYSTEM installation must be initialized or adopted, got {installation!r}")

    packs = system.get("packs", [])
    overlays = system.get("overlays", [])
    if not isinstance(packs, list) or any(pack not in PACK_NAMES for pack in packs):
        errors.append("SYSTEM packs must be an array of known capability packs")
        packs = []
    elif packs != [name for name in PACK_NAMES if name in set(packs)]:
        errors.append("SYSTEM packs must be unique and in canonical order")
    if not isinstance(overlays, list) or any(overlay not in OVERLAY_NAMES for overlay in overlays):
        errors.append("SYSTEM overlays must be an array of known ecosystem overlays")
        overlays = []
    elif overlays != [name for name in OVERLAY_NAMES if name in set(overlays)]:
        errors.append("SYSTEM overlays must be unique and in canonical order")
    try:
        validate_overlay_dependencies(packs, overlays)
    except ProjectOSError as error:
        errors.append(str(error))

    expected_pack_paths = [f".agents/packs/{name}.md" for name in packs]
    expected_overlay_paths = [f".agents/packs/overlays/{name}.md" for name in overlays]
    if system.get("pack_paths", []) != expected_pack_paths:
        errors.append("SYSTEM pack_paths must match packs in canonical order")
    if system.get("overlay_paths", []) != expected_overlay_paths:
        errors.append("SYSTEM overlay_paths must match overlays in canonical order")
    for raw_path in [*expected_pack_paths, *expected_overlay_paths]:
        path = safe_relative(root, raw_path)
        if path is not None:
            check_no_symlink_path(root, path, f"managed guidance {raw_path}", errors)
        if path is None or not path.is_file():
            errors.append(f"missing selected guidance file: {raw_path}")

    managed_guidance = system.get("managed_guidance")
    expected_managed_paths = [
        ".agents/packs/README.md",
        *expected_pack_paths,
        *expected_overlay_paths,
    ]
    if not isinstance(managed_guidance, dict) or list(managed_guidance) != expected_managed_paths:
        errors.append("SYSTEM managed_guidance must match selected guidance in canonical order")
        managed_guidance = {}
    for raw_path, expected_hash in managed_guidance.items():
        path = safe_relative(root, raw_path)
        if path is not None:
            check_no_symlink_path(root, path, f"managed guidance {raw_path}", errors)
        if path is None or not path.is_file():
            continue
        actual_hash = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        if expected_hash != actual_hash:
            errors.append(f"managed guidance differs from its recorded baseline: {raw_path}")

    managed_knowledge = system.get("managed_knowledge")
    if not isinstance(managed_knowledge, dict) or any(
        not isinstance(entry_id, str)
        or not isinstance(entry_hash, str)
        or not entry_hash.startswith("sha256:")
        for entry_id, entry_hash in (
            managed_knowledge.items() if isinstance(managed_knowledge, dict) else ()
        )
    ):
        errors.append("SYSTEM managed_knowledge must map ids to sha256 baselines")
        managed_knowledge = {}

    paths = system.get("paths")
    if not isinstance(paths, dict):
        errors.append("SYSTEM paths must contain an object")
        paths = {}
    validate_system_owner_paths(root, paths, mode, managed_guidance, errors)

    if not (root / "AGENTS.md").is_file():
        errors.append("missing required file: AGENTS.md")
    if installation == "initialized":
        for relative in (
            ".agents/README.md",
            ".agents/plans/README.md",
            ".agents/findings/README.md",
            ".agents/evidence/README.md",
            ".agents/knowledge/README.md",
            ".agents/packs/README.md",
        ):
            if not (root / relative).is_file():
                errors.append(f"missing required file: {relative}")

    context_path = system_path_value(root, paths, "context", errors, required=True)
    state_path = system_path_value(root, paths, "state", errors, required=True)
    plans_path = system_path_value(root, paths, "plans", errors, required=True)
    findings_path = system_path_value(root, paths, "findings", errors, required=True)
    evidence_path = system_path_value(root, paths, "evidence", errors)
    program_path = system_path_value(root, paths, "program", errors, required=mode == "program")
    history_path = system_path_value(root, paths, "history", errors)
    history_index_path = system_path_value(root, paths, "history_index", errors)
    shared_path = system_path_value(root, paths, "shared_knowledge", errors, required=True)

    for label, path in (
        ("context", context_path),
        ("state", state_path),
        ("plans", plans_path),
        ("findings", findings_path),
        ("evidence", evidence_path),
        ("program", program_path),
        ("history", history_path),
        ("history index", history_index_path),
        ("shared knowledge", shared_path),
    ):
        if path is not None:
            check_no_symlink_path(root, path, f"SYSTEM path {label}", errors)

    for label, path in (
        ("context", context_path),
        ("state", state_path),
        ("plans", plans_path),
        ("findings", findings_path),
        ("shared knowledge", shared_path),
    ):
        if path is not None and not path.is_file():
            errors.append(f"missing {label} file: {path.relative_to(root)}")
    if evidence_path is not None and not evidence_path.is_dir():
        errors.append(f"missing evidence directory: {evidence_path.relative_to(root)}")
    if program_path is not None and not program_path.is_file():
        errors.append(f"missing program file: {program_path.relative_to(root)}")
    if history_path is not None and not history_path.is_dir():
        errors.append(f"missing history directory: {history_path.relative_to(root)}")
    if history_index_path is not None and not history_index_path.is_file():
        errors.append(f"missing history index file: {history_index_path.relative_to(root)}")

    active_program = system.get("active_program")
    if mode == "standard":
        if program_path is not None:
            errors.append("Standard mode requires SYSTEM paths.program to be null")
        if active_program is not None:
            errors.append("Standard mode requires SYSTEM active_program to be null")
        if (root / ".agents" / "PROGRAM.md").exists():
            errors.append("Standard mode cannot retain an active .agents/PROGRAM.md")
    elif mode == "program":
        validate_active_program(program_path, active_program, errors)

    if (history_path is None) != (history_index_path is None):
        errors.append("SYSTEM history and history_index paths must be set together")
    if history_path is not None and history_index_path is not None and history_index_path.is_file():
        validate_history_index(root, history_path, history_index_path, errors)

    agents_path = root / "AGENTS.md"
    check_no_symlink_path(root, agents_path, "AGENTS.md", errors)
    if agents_path.is_file():
        agents_text = agents_path.read_text(encoding="utf-8", errors="ignore")
        for routed_path in (context_path, state_path):
            if routed_path is None:
                continue
            relative = routed_path.relative_to(root).as_posix()
            if relative not in agents_text:
                errors.append(f"AGENTS.md does not route to {relative}")

    for path, maximum in ((context_path, 150), (state_path, 80)):
        if path is not None and path.is_file():
            lines = len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
            if lines > maximum:
                errors.append(f"{path.relative_to(root)} has {lines} lines; maximum is {maximum}")

    if plans_path is not None and plans_path.is_file():
        try:
            plans_value = load_json(plans_path)
        except ProjectOSError as error:
            errors.append(str(error))
        else:
            if not isinstance(plans_value, dict):
                errors.append("plans index must contain an object")
            else:
                validate_registry_schema(plans_value, "plans index", errors)
                plans = plans_value.get("plans", [])
                check_unique_ids(plans, "plans", errors, ("id", "status", "path", "outcome"))
                active_ids: list[str] = []
                if isinstance(plans, list):
                    for plan in plans:
                        if not isinstance(plan, dict):
                            continue
                        if plan.get("status") == "active" and isinstance(plan.get("id"), str):
                            active_ids.append(plan["id"])
                        plan_status = plan.get("status")
                        if not isinstance(plan_status, str) or plan_status not in PLAN_STATUSES:
                            errors.append(
                                f"plan {plan.get('id')!r} has invalid status {plan.get('status')!r}"
                            )
                        path = safe_relative(root, plan.get("path"))
                        if path is None:
                            errors.append(f"plan {plan.get('id')!r} has invalid path")
                        elif not path.is_file():
                            errors.append(
                                f"plan {plan.get('id')!r} path does not exist: {plan.get('path')}"
                            )
                        else:
                            lines = len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
                            if lines > 200:
                                errors.append(
                                    f"plan {plan.get('id')!r} has {lines} lines; maximum is 200"
                                )
                execution_state = plans_value.get("execution_state")
                explicit_active = plans_value.get("active_plan")
                if execution_state == "running":
                    if len(active_ids) != 1:
                        errors.append("running execution requires exactly one active plan")
                    if "active_plan" in plans_value and explicit_active != (
                        active_ids[0] if len(active_ids) == 1 else None
                    ):
                        errors.append("active_plan must match the single active plan when present")
                elif execution_state == "idle":
                    if active_ids:
                        errors.append("idle execution requires no active plan")
                    if "active_plan" in plans_value and explicit_active is not None:
                        errors.append("idle execution requires active_plan null when present")
                else:
                    errors.append("execution_state must be idle or running")

    if findings_path is not None and findings_path.is_file():
        try:
            findings_value = load_json(findings_path)
        except ProjectOSError as error:
            errors.append(str(error))
        else:
            if isinstance(findings_value, dict):
                validate_registry_schema(findings_value, "findings registry", errors)
            findings = findings_value.get("findings", []) if isinstance(findings_value, dict) else None
            check_unique_ids(
                findings,
                "findings",
                errors,
                ("id", "status", "impact", "evidence", "required_check"),
                FINDING_STATUSES,
            )
            if isinstance(findings, list):
                for finding in findings:
                    if not isinstance(finding, dict):
                        continue
                    evidence = finding.get("evidence", [])
                    if not isinstance(evidence, list):
                        errors.append(f"finding {finding.get('id')!r} evidence must be an array")
                        continue
                    for raw_path in evidence:
                        path = safe_relative(root, raw_path)
                        if path is None:
                            errors.append(f"finding {finding.get('id')!r} has invalid evidence path")
                        elif not path.exists():
                            errors.append(
                                f"finding {finding.get('id')!r} evidence does not exist: {raw_path}"
                            )

    shared_targets: dict[str, str] = {}
    if shared_path is not None and shared_path.is_file():
        valid_shared_ids = validate_failure_registry(
            shared_path, "shared knowledge", errors, strict_managed=True
        )
        try:
            shared_value = load_json(shared_path)
        except ProjectOSError:
            shared_value = None
        if isinstance(shared_value, dict):
            if shared_value.get("knowledge_version") != system.get("project_os_version"):
                errors.append(
                    "shared knowledge_version must match SYSTEM project_os_version"
                )
            if shared_value.get("packs") != ["core", *packs]:
                errors.append("shared knowledge packs must match SYSTEM packs")
            if shared_value.get("overlays") != overlays:
                errors.append("shared knowledge overlays must match SYSTEM overlays")
            entries = shared_value.get("entries", [])
            if isinstance(entries, list):
                entries_by_id = {
                    entry.get("id"): entry
                    for entry in entries
                    if isinstance(entry, dict) and isinstance(entry.get("id"), str)
                }
                for entry_id, recorded_hash in managed_knowledge.items():
                    entry = entries_by_id.get(entry_id)
                    if entry is None:
                        errors.append(f"managed knowledge baseline references missing id {entry_id}")
                    elif entry_content_hash(entry) != recorded_hash:
                        errors.append(f"managed knowledge differs from its recorded baseline: {entry_id}")
                for entry in entries:
                    entry_id = entry.get("id") if isinstance(entry, dict) else None
                    if (
                        not isinstance(entry, dict)
                        or not isinstance(entry_id, str)
                        or entry_id not in valid_shared_ids
                    ):
                        continue
                    source = entry.get("source")
                    source_kind = source.get("kind") if isinstance(source, dict) else None
                    if (
                        isinstance(source_kind, str)
                        and source_kind in {"project-os-pack", "incident-derived"}
                        and entry["id"] not in managed_knowledge
                    ):
                        errors.append(f"managed knowledge baseline is missing id {entry['id']}")
                    source_pack = source.get("pack") if isinstance(source, dict) else None
                    if isinstance(source_pack, str):
                        shared_targets[entry["id"]] = source_pack
        for label in private_material_labels(shared_value):
            errors.append(f"shared knowledge contains a {label}")

    project_paths = paths.get("project_knowledge", [])
    if not isinstance(project_paths, list):
        errors.append("SYSTEM paths.project_knowledge must be an array")
        project_paths = []
    for raw_path in project_paths:
        path = safe_relative(root, raw_path)
        if path is None:
            errors.append(f"invalid project knowledge path: {raw_path!r}")
        else:
            check_no_symlink_path(root, path, f"SYSTEM project knowledge {raw_path}", errors)
            if not path.is_file():
                errors.append(f"missing project knowledge file: {raw_path}")
            elif path.suffix == ".json":
                validate_failure_registry(path, f"project knowledge {raw_path}", errors)

    legacy_roots = paths.get("legacy_knowledge", [])
    if not isinstance(legacy_roots, list):
        errors.append("SYSTEM paths.legacy_knowledge must be an array")
        legacy_roots = []
    for raw_path in legacy_roots:
        path = safe_relative(root, raw_path)
        if path is None:
            errors.append(f"invalid legacy knowledge path: {raw_path!r}")
        else:
            check_no_symlink_path(root, path, f"SYSTEM legacy knowledge {raw_path}", errors)
            if not path.exists():
                errors.append(f"missing legacy knowledge path: {raw_path}")
    inventory = scan_markdown_lessons(root, legacy_roots)
    counts: dict[str, int] = {}
    for record in inventory:
        counts[record["legacy_id"]] = counts.get(record["legacy_id"], 0) + 1
    duplicate_legacy_ids = sorted(identifier for identifier, count in counts.items() if count > 1)
    coverage_path = system_path_value(root, paths, "knowledge_coverage", errors)
    if coverage_path is not None:
        check_no_symlink_path(root, coverage_path, "SYSTEM knowledge coverage", errors)
        if not coverage_path.is_file():
            errors.append(f"missing knowledge coverage file: {coverage_path.relative_to(root)}")
        else:
            validate_knowledge_coverage(root, inventory, coverage_path, shared_targets, errors)
    elif inventory:
        errors.append(
            "legacy knowledge requires paths.knowledge_coverage"
            + (
                "; duplicate ids: " + ", ".join(duplicate_legacy_ids)
                if duplicate_legacy_ids
                else ""
            )
        )

    scan_paths: list[Path] = [config_path]
    scan_paths.extend(
        path for path in (shared_path, *[safe_relative(root, value) for value in expected_pack_paths])
        if path is not None
    )
    scan_paths.extend(
        path for path in (safe_relative(root, value) for value in expected_overlay_paths)
        if path is not None
    )
    if installation == "initialized":
        scan_paths.extend(path for path in (agents_path, context_path, state_path, program_path) if path)
        scan_paths.extend(
            root / relative
            for relative in (
                ".agents/README.md",
                ".agents/plans/README.md",
                ".agents/findings/README.md",
                ".agents/evidence/README.md",
                ".agents/knowledge/README.md",
                ".agents/packs/README.md",
            )
        )
    for path in scan_paths:
        if path.suffix not in {".md", ".json"} or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        tokens = sorted(token for token in RESERVED_TEMPLATE_TOKENS if token in text)
        if tokens:
            try:
                label = path.relative_to(root).as_posix()
            except ValueError:
                label = str(path)
            errors.append(
                f"unresolved template tokens in {label}: {', '.join(tokens)}"
            )

    if errors:
        print("Project OS check: FAIL")
        for error in errors:
            print(f"error: {error}")
    else:
        print("Project OS check: PASS")
    return 1 if errors else 0


def read_selected_system(root: Path) -> tuple[list[str], list[str], dict[str, Any]]:
    system_path = root / ".agents" / "SYSTEM.json"
    reject_symlink_path(root, system_path)
    system = load_json(system_path)
    if not isinstance(system, dict):
        raise ProjectOSError("SYSTEM configuration must contain an object")
    if system.get("schema_version") != SCHEMA_VERSION:
        raise ProjectOSError(
            f"sync requires SYSTEM schema_version {SCHEMA_VERSION}; migrate older state explicitly"
        )
    if system.get("project_os_version") != VERSION:
        raise ProjectOSError(
            f"Repository Project OS version must be {VERSION}; run upgrade before sync"
        )
    if not isinstance(system.get("mode"), str) or system.get("mode") not in {
        "standard",
        "program",
    }:
        raise ProjectOSError("SYSTEM mode must be standard or program")
    if not isinstance(system.get("installation"), str) or system.get("installation") not in {
        "initialized",
        "adopted",
    }:
        raise ProjectOSError("SYSTEM installation must be initialized or adopted")
    packs = system.get("packs", [])
    overlays = system.get("overlays", [])
    if not isinstance(packs, list) or not isinstance(overlays, list):
        raise ProjectOSError("SYSTEM packs and overlays must be arrays")
    if any(not isinstance(name, str) or name not in PACK_NAMES for name in packs):
        raise ProjectOSError("SYSTEM packs contain an unknown value")
    if any(not isinstance(name, str) or name not in OVERLAY_NAMES for name in overlays):
        raise ProjectOSError("SYSTEM overlays contain an unknown value")
    if packs != [name for name in PACK_NAMES if name in set(packs)]:
        raise ProjectOSError("SYSTEM packs must be known, unique, and in canonical order")
    if overlays != [name for name in OVERLAY_NAMES if name in set(overlays)]:
        raise ProjectOSError("SYSTEM overlays must be known, unique, and in canonical order")
    validate_overlay_dependencies(packs, overlays)
    if system.get("pack_paths") != [f".agents/packs/{name}.md" for name in packs]:
        raise ProjectOSError("SYSTEM pack_paths do not match selected packs")
    if system.get("overlay_paths") != [
        f".agents/packs/overlays/{name}.md" for name in overlays
    ]:
        raise ProjectOSError("SYSTEM overlay_paths do not match selected overlays")
    if not isinstance(system.get("paths"), dict):
        raise ProjectOSError("SYSTEM paths must contain an object")
    require_safe_system_owners(root, system)
    lifecycle_errors: list[str] = []
    raw_program = system["paths"].get("program")
    program_path = safe_relative(root, raw_program) if isinstance(raw_program, str) else None
    if system["mode"] == "standard":
        if raw_program is not None or system.get("active_program") is not None:
            lifecycle_errors.append(
                "Standard mode requires null Program path and active_program"
            )
        if (root / PROGRAM_RELATIVE_PATH).exists():
            lifecycle_errors.append("Standard mode cannot retain an active PROGRAM.md")
    else:
        if program_path is None or not program_path.is_file():
            lifecycle_errors.append("Program mode requires an existing PROGRAM.md")
        validate_active_program(program_path, system.get("active_program"), lifecycle_errors)
    if lifecycle_errors:
        raise ProjectOSError("Invalid Program lifecycle: " + "; ".join(lifecycle_errors))
    shared_path = safe_relative(root, system["paths"].get("shared_knowledge"))
    if shared_path is None:
        raise ProjectOSError("SYSTEM shared knowledge path is unsafe or missing")
    reject_symlink_path(root, shared_path)
    return packs, overlays, system


def sync_knowledge(
    root: Path,
    packs_value: str,
    overlays_value: str,
    dry_run: bool,
) -> int:
    root = root.resolve()
    selected_packs, selected_overlays, system = read_selected_system(root)
    packs = (
        selected_packs
        if packs_value.strip().lower() == "selected"
        else parse_selection(packs_value, selected_packs, PACK_NAMES, "packs")
    )
    overlays = (
        selected_overlays
        if overlays_value.strip().lower() == "selected"
        else parse_selection(overlays_value, selected_overlays, OVERLAY_NAMES, "overlays")
    )
    validate_overlay_dependencies(packs, overlays)
    if list(packs) != list(selected_packs):
        raise ProjectOSError("sync packs must exactly match SYSTEM packs")
    if list(overlays) != list(selected_overlays):
        raise ProjectOSError("sync overlays must exactly match SYSTEM overlays")
    expected_system = default_system(
        root,
        str(system.get("mode", "standard")),
        str(system.get("installation", "initialized")),
        packs,
        overlays,
        system.get("paths", {}),
        system.get("active_program") if isinstance(system.get("active_program"), dict) else None,
    )
    recorded_guidance = system.get("managed_guidance")
    expected_guidance = expected_system["managed_guidance"]
    if not isinstance(recorded_guidance, dict) or list(recorded_guidance) != list(expected_guidance):
        raise ProjectOSError("SYSTEM managed_guidance is missing or inconsistent")
    if any(not isinstance(value, str) for value in recorded_guidance.values()):
        raise ProjectOSError("SYSTEM managed_guidance contains an invalid baseline")
    recorded_knowledge = system.get("managed_knowledge")
    if not isinstance(recorded_knowledge, dict) or any(
        not isinstance(entry_id, str) or not isinstance(entry_hash, str)
        for entry_id, entry_hash in (
            recorded_knowledge.items() if isinstance(recorded_knowledge, dict) else ()
        )
    ):
        raise ProjectOSError("SYSTEM managed_knowledge is missing or invalid")

    guidance_contents = guidance_content_map(packs, overlays)
    guidance_conflicts: list[str] = []
    guidance_creates: list[tuple[Path, str]] = []
    guidance_replacements: list[tuple[Path, str, str]] = []
    for raw_path, recorded_hash in recorded_guidance.items():
        path = safe_relative(root, raw_path)
        if path is None:
            raise ProjectOSError(f"Managed guidance path is unsafe: {raw_path}")
        reject_symlink_path(root, path)
        desired_hash = expected_guidance[raw_path]
        desired_content = guidance_contents[raw_path]
        if not path.exists():
            guidance_creates.append((path, desired_content))
            continue
        if not path.is_file():
            raise ProjectOSError(f"Managed guidance is not a regular file: {raw_path}")
        actual_digest = hashlib.sha256(path.read_bytes()).hexdigest()
        actual_hash = "sha256:" + actual_digest
        if actual_hash == desired_hash:
            continue
        if actual_hash == recorded_hash:
            guidance_replacements.append((path, desired_content, actual_digest))
        else:
            guidance_conflicts.append(f"{raw_path} differs locally")
    if guidance_conflicts:
        for conflict in guidance_conflicts:
            print(f"guidance conflict: {conflict}")
        return 1
    paths = system.get("paths", {})
    raw_destination = paths.get("shared_knowledge", DEFAULT_PATHS["shared_knowledge"])
    destination = safe_relative(root, raw_destination)
    if destination is None:
        raise ProjectOSError(f"Invalid shared knowledge destination: {raw_destination!r}")
    require_destination_within_root(root, destination)
    reject_symlink_path(root, destination)
    system_path = root / ".agents" / "SYSTEM.json"
    reject_symlink_path(root, system_path)
    if destination == system_path or destination in {
        path for path, _ in guidance_creates
    } | {path for path, _, _ in guidance_replacements}:
        raise ProjectOSError("SYSTEM paths collide with Project OS-managed files")

    desired = composed_knowledge(packs, overlays)
    validate_composed_knowledge(desired, packs, overlays)
    pre_read_sha256: str | None = None
    if destination.exists():
        if not destination.is_file():
            raise ProjectOSError(f"Shared knowledge destination is not a file: {destination}")
        pre_read_sha256 = hashlib.sha256(destination.read_bytes()).hexdigest()
        current = load_json(destination)
    else:
        current = {
            "schema_version": 1,
            "knowledge_version": "0.0.0",
            "packs": [],
            "overlays": [],
            "entries": [],
        }
    if not isinstance(current, dict) or not isinstance(current.get("entries"), list):
        raise ProjectOSError(f"Invalid shared knowledge structure: {destination}")
    validation_errors: list[str] = []
    if destination.exists():
        validate_failure_registry(
            destination,
            "shared knowledge",
            validation_errors,
            verify_hashes=True,
            strict_managed=True,
        )
    if destination.exists():
        if current.get("packs") != ["core", *selected_packs]:
            validation_errors.append("shared knowledge packs do not match SYSTEM packs")
        if current.get("overlays") != selected_overlays:
            validation_errors.append("shared knowledge overlays do not match SYSTEM overlays")
    for label in private_material_labels(current):
        validation_errors.append(f"shared knowledge contains a {label}")
    if validation_errors:
        for error in validation_errors:
            print(f"knowledge conflict: {error}")
        print("knowledge sync aborted: invalid or locally changed knowledge")
        return 1

    current_by_id: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(current["entries"]):
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            raise ProjectOSError(f"Invalid shared knowledge entry at index {index}")
        if entry["id"] in current_by_id:
            raise ProjectOSError(f"Duplicate shared knowledge id: {entry['id']}")
        current_by_id[entry["id"]] = entry

    desired_by_id = {entry["id"]: entry for entry in desired["entries"]}
    additions: list[dict[str, Any]] = []
    updates: list[dict[str, Any]] = []
    conflicts: list[str] = []
    for entry in desired["entries"]:
        existing = current_by_id.get(entry["id"])
        if existing is None:
            additions.append(entry)
        elif existing == entry:
            continue
        else:
            recorded_hash = recorded_knowledge.get(entry["id"])
            if isinstance(recorded_hash, str) and entry_content_hash(existing) == recorded_hash:
                updates.append(entry)
            else:
                conflicts.append(entry["id"])

    retained = sorted(set(current_by_id).difference(desired_by_id))
    for entry_id in retained:
        source = current_by_id[entry_id].get("source")
        source_kind = source.get("kind") if isinstance(source, dict) else None
        if (
            isinstance(source_kind, str)
            and source_kind in {"project-os-pack", "incident-derived"}
            and entry_id not in recorded_knowledge
        ):
            conflicts.append(entry_id)

    print(f"knowledge additions: {len(additions)}")
    for entry in additions:
        print(f"knowledge add: {entry['id']} {entry['title']}")
    print(f"knowledge updates: {len(updates)}")
    for entry in updates:
        print(f"knowledge update: {entry['id']} {entry['title']}")
    for entry_id in conflicts:
        print(f"conflict: {entry_id} differs locally and was not overwritten")
    for entry_id in retained:
        print(f"retain: {entry_id} is not in the selected upstream set")

    if conflicts:
        print("knowledge sync aborted: resolve conflicts before applying any changes")
        return 1

    next_managed_knowledge = {
        entry_id: entry_hash
        for entry_id, entry_hash in recorded_knowledge.items()
        if entry_id in retained
    }
    next_managed_knowledge.update(expected_system["managed_knowledge"])
    next_system = copy.deepcopy(system)
    next_system["project_os_version"] = VERSION
    next_system["generated_on"] = date.today().isoformat()
    next_system["managed_guidance"] = expected_guidance
    next_system["managed_knowledge"] = dict(sorted(next_managed_knowledge.items()))

    next_by_id = dict(current_by_id)
    for entry in additions:
        next_by_id[entry["id"]] = entry
    for entry in updates:
        next_by_id[entry["id"]] = entry
    current["entries"] = sorted(next_by_id.values(), key=lambda entry: str(entry.get("id", "")))
    current["knowledge_version"] = VERSION
    current["packs"] = ["core", *packs]
    current["overlays"] = list(overlays)
    serialized = json.dumps(current, indent=2, ensure_ascii=False) + "\n"
    serialized_system = json.dumps(next_system, indent=2, ensure_ascii=False) + "\n"

    destination_changed = (
        pre_read_sha256 is None
        or hashlib.sha256(serialized.encode("utf-8")).hexdigest() != pre_read_sha256
    )
    system_pre_read = hashlib.sha256(system_path.read_bytes()).hexdigest()
    system_changed = hashlib.sha256(serialized_system.encode("utf-8")).hexdigest() != system_pre_read

    creates = list(guidance_creates)
    replacements = list(guidance_replacements)
    if destination_changed:
        if pre_read_sha256 is None:
            creates.append((destination, serialized))
        else:
            replacements.append((destination, serialized, pre_read_sha256))
    if system_changed:
        replacements.append((system_path, serialized_system, system_pre_read))
    print_transaction_preview(root, creates, replacements)
    if dry_run:
        print("dry-run: no files written")
        return 0
    execute_sync_transaction(root, creates, replacements)
    return 0


def nonempty_string_list(value: Any, label: str) -> list[str]:
    if (
        not isinstance(value, list)
        or not value
        or any(not isinstance(item, str) or not item.strip() for item in value)
    ):
        raise ProjectOSError(f"{label} must be a non-empty array of non-empty strings")
    return [item.strip() for item in value]


def canonical_date(value: str | None, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ProjectOSError(f"{label} requires a YYYY-MM-DD date")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise ProjectOSError(f"{label} must be a valid YYYY-MM-DD date") from error
    if parsed.isoformat() != value:
        raise ProjectOSError(f"{label} must use canonical YYYY-MM-DD form")
    return value


def validate_program_definition(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ProjectOSError("Program definition must contain a JSON object")
    normalized: dict[str, Any] = {}
    for key in ("initiative", "outcome"):
        raw = value.get(key)
        if not isinstance(raw, str) or not raw.strip():
            raise ProjectOSError(f"Program definition {key} must be a non-empty string")
        if key == "initiative" and any(character in raw for character in ("\r", "\n")):
            raise ProjectOSError("Program definition initiative must be a single line")
        normalized[key] = raw.strip()
    for key in (
        "authority",
        "exit_conditions",
        "evidence_requirements",
        "cost_boundary",
        "exclusions",
    ):
        normalized[key] = nonempty_string_list(value.get(key), f"Program definition {key}")

    phases = value.get("phases")
    if not isinstance(phases, list) or len(phases) < 2:
        raise ProjectOSError("Program definition phases must contain at least two phases")
    normalized_phases: list[dict[str, Any]] = []
    for index, phase in enumerate(phases, 1):
        if not isinstance(phase, dict):
            raise ProjectOSError(f"Program definition phase {index} must be an object")
        normalized_phase: dict[str, Any] = {}
        for key in ("name", "outcome"):
            raw = phase.get(key)
            if not isinstance(raw, str) or not raw.strip():
                raise ProjectOSError(
                    f"Program definition phase {index} {key} must be a non-empty string"
                )
            if key == "name" and any(character in raw for character in ("\r", "\n")):
                raise ProjectOSError(
                    f"Program definition phase {index} name must be a single line"
                )
            normalized_phase[key] = raw.strip()
        normalized_phase["exit_conditions"] = nonempty_string_list(
            phase.get("exit_conditions"),
            f"Program definition phase {index} exit_conditions",
        )
        normalized_phases.append(normalized_phase)
    normalized["phases"] = normalized_phases
    for text in iter_string_values(normalized):
        if any(token in text for token in RESERVED_TEMPLATE_TOKENS):
            raise ProjectOSError("Program definition contains a reserved template token")
    return normalized


def markdown_bullets(values: Sequence[str]) -> str:
    return "\n".join(f"- {value}" for value in values)


def render_program_definition(
    definition: dict[str, Any], program_id: str, started_on: str
) -> str:
    phases: list[str] = []
    for index, phase in enumerate(definition["phases"], 1):
        phases.extend(
            (
                f"### {index}. {phase['name']}",
                "",
                phase["outcome"],
                "",
                "Phase exit conditions:",
                "",
                markdown_bullets(phase["exit_conditions"]),
                "",
            )
        )
    replacements = {
        "__PROGRAM_INITIATIVE__": definition["initiative"],
        "__PROGRAM_ID__": program_id,
        "__PROGRAM_STARTED_ON__": started_on,
        "__PROGRAM_OUTCOME__": definition["outcome"],
        "__PROGRAM_AUTHORITY__": markdown_bullets(definition["authority"]),
        "__PROGRAM_PHASES__": "\n".join(phases).rstrip(),
        "__PROGRAM_EXIT_CONDITIONS__": markdown_bullets(definition["exit_conditions"]),
        "__PROGRAM_EVIDENCE__": markdown_bullets(definition["evidence_requirements"]),
        "__PROGRAM_COST_BOUNDARY__": markdown_bullets(definition["cost_boundary"]),
        "__PROGRAM_EXCLUSIONS__": markdown_bullets(definition["exclusions"]),
    }
    return render_template(PROGRAM_TEMPLATE.read_text(encoding="utf-8"), replacements)


def load_history_for_mutation(
    root: Path, system: dict[str, Any]
) -> tuple[Path, Path, dict[str, Any], str | None]:
    paths = system.get("paths")
    if not isinstance(paths, dict):
        raise ProjectOSError("SYSTEM paths must contain an object")
    raw_history = paths.get("history") or ".agents/history"
    raw_index = paths.get("history_index") or ".agents/history/index.json"
    history_path = safe_relative(root, raw_history)
    index_path = safe_relative(root, raw_index)
    if history_path is None or index_path is None:
        raise ProjectOSError("SYSTEM history paths are unsafe")
    reject_symlink_path(root, history_path)
    reject_symlink_path(root, index_path)
    try:
        index_path.resolve().relative_to(history_path.resolve())
    except ValueError as error:
        raise ProjectOSError("SYSTEM history_index must be inside SYSTEM history") from error
    if history_path.exists() and not history_path.is_dir():
        raise ProjectOSError("SYSTEM history path must be a directory")
    index_sha256: str | None = None
    if index_path.exists():
        if not index_path.is_file():
            raise ProjectOSError("SYSTEM history index must be a regular file")
        errors: list[str] = []
        validate_history_index(root, history_path, index_path, errors)
        if errors:
            raise ProjectOSError("Invalid history index: " + "; ".join(errors))
        value = load_json(index_path)
        index_sha256 = hashlib.sha256(index_path.read_bytes()).hexdigest()
    else:
        value = {"schema_version": 1, "entries": []}
    if not isinstance(value, dict) or not isinstance(value.get("entries"), list):
        raise ProjectOSError("History index must contain an entries array")
    return history_path, index_path, copy.deepcopy(value), index_sha256


def next_program_id(index: dict[str, Any], history_path: Path | None = None) -> str:
    prefix = f"program-{date.today().strftime('%Y%m%d')}-"
    used = {
        entry.get("id")
        for entry in index.get("entries", [])
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    }
    sequence = 1
    while f"{prefix}{sequence:03d}" in used or (
        history_path is not None
        and (history_path / "programs" / f"{prefix}{sequence:03d}").exists()
    ):
        sequence += 1
    return f"{prefix}{sequence:03d}"


def active_plan_ids(root: Path, system: dict[str, Any]) -> list[str]:
    paths = system.get("paths")
    if not isinstance(paths, dict):
        raise ProjectOSError("SYSTEM paths must contain an object")
    plans_path = safe_relative(root, paths.get("plans"))
    if plans_path is None or not plans_path.is_file():
        raise ProjectOSError("SYSTEM plans registry is missing")
    value = load_json(plans_path)
    if not isinstance(value, dict) or not isinstance(value.get("plans"), list):
        raise ProjectOSError("Plans registry must contain a plans array")
    active = [
        plan.get("id")
        for plan in value["plans"]
        if isinstance(plan, dict)
        and plan.get("status") == "active"
        and isinstance(plan.get("id"), str)
    ]
    if value.get("execution_state") == "running" or active:
        return active or ["<running execution>"]
    if value.get("execution_state") != "idle":
        raise ProjectOSError("Plans registry execution_state must be idle or running")
    return []


def require_current_system(root: Path) -> dict[str, Any]:
    _, _, system = read_selected_system(root)
    if system.get("project_os_version") != VERSION:
        raise ProjectOSError("Repository must be upgraded before Program lifecycle changes")
    return system


def require_passing_check(root: Path, operation: str) -> None:
    if check_project(root) != 0:
        raise ProjectOSError(f"{operation} produced invalid Project OS state")


def print_transaction_preview(
    root: Path,
    creates: Sequence[tuple[Path, str | bytes]],
    replacements: Sequence[tuple[Path, str, str]],
    deletions: Sequence[tuple[Path, str]] = (),
) -> None:
    for path, _ in creates:
        print(f"create: {path.relative_to(root)}")
    for path, _, _ in replacements:
        print(f"update: {path.relative_to(root)}")
    for path, _ in deletions:
        print(f"delete: {path.relative_to(root)}")


def start_program(root: Path, definition_path: Path, dry_run: bool) -> int:
    root = root.resolve()
    if check_project(root) != 0:
        raise ProjectOSError("Program start requires a clean Project OS check")
    system = require_current_system(root)
    if system.get("mode") != "standard" or system.get("active_program") is not None:
        raise ProjectOSError("A Program is already active")
    definition = validate_program_definition(load_json(definition_path.resolve()))
    history_path, index_path, history_index, index_sha256 = load_history_for_mutation(
        root, system
    )
    program_id = next_program_id(history_index, history_path)
    started_on = date.today().isoformat()
    program_path = root / PROGRAM_RELATIVE_PATH
    reject_symlink_path(root, program_path)
    if program_path.exists():
        raise ProjectOSError("Refusing to overwrite an existing .agents/PROGRAM.md")
    content = render_program_definition(definition, program_id, started_on)

    next_system = copy.deepcopy(system)
    next_system["mode"] = "program"
    next_system["active_program"] = {
        "id": program_id,
        "initiative": definition["initiative"],
        "started_on": started_on,
        "origin": "created",
    }
    next_system["paths"]["program"] = ".agents/PROGRAM.md"
    if index_sha256 is not None:
        next_system["paths"]["history"] = history_path.relative_to(root).as_posix()
        next_system["paths"]["history_index"] = index_path.relative_to(root).as_posix()
    next_system["generated_on"] = started_on
    contract_errors: list[str] = []
    validate_created_program_contract(content, next_system["active_program"], contract_errors)
    if contract_errors:
        raise ProjectOSError("Invalid rendered Program: " + "; ".join(contract_errors))

    creates: list[tuple[Path, str]] = [(program_path, content)]
    replacements: list[tuple[Path, str, str]] = []
    system_path = root / ".agents" / "SYSTEM.json"
    system_sha256 = hashlib.sha256(system_path.read_bytes()).hexdigest()
    replacements.append(
        (system_path, json.dumps(next_system, indent=2) + "\n", system_sha256)
    )
    print_transaction_preview(root, creates, replacements)
    if dry_run:
        print("dry-run: no files written")
        return 0
    execute_sync_transaction(
        root,
        creates,
        replacements,
        after_write=lambda: require_passing_check(root, "Program start"),
    )
    return 0


def program_status(root: Path) -> int:
    root = root.resolve()
    system = require_current_system(root)
    paths = system.get("paths", {})
    index_path = safe_relative(root, paths.get("history_index")) if isinstance(paths, dict) else None
    archive_count = 0
    if index_path is not None and index_path.is_file():
        index = load_json(index_path)
        if isinstance(index, dict) and isinstance(index.get("entries"), list):
            archive_count = len(index["entries"])
    print(
        json.dumps(
            {
                "mode": system.get("mode"),
                "active_program": system.get("active_program"),
                "indexed_history_entries": archive_count,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


def close_program(
    root: Path,
    disposition: str,
    reason: str | None,
    dry_run: bool,
) -> int:
    root = root.resolve()
    if check_project(root) != 0:
        raise ProjectOSError("Program close requires a clean Project OS check")
    system = require_current_system(root)
    if system.get("mode") != "program" or not isinstance(system.get("active_program"), dict):
        raise ProjectOSError("No Program is active")
    if disposition == "stopped" and (not isinstance(reason, str) or not reason.strip()):
        raise ProjectOSError("A stopped Program requires --reason")
    if active_plan_ids(root, system):
        raise ProjectOSError("Close the active plan before closing the Program")
    program_path = require_canonical_program_owner(root, system)
    if not program_path.is_file():
        raise ProjectOSError("Active PROGRAM.md is missing")
    reject_symlink_path(root, program_path)
    program_content = program_path.read_bytes()
    program_digest = hashlib.sha256(program_content).hexdigest()
    active = system["active_program"]
    program_id = active.get("id")
    if not isinstance(program_id, str) or not program_id:
        raise ProjectOSError("SYSTEM active_program has no valid id")

    history_path, index_path, history_index, index_sha256 = load_history_for_mutation(
        root, system
    )
    archive_path = history_path / "programs" / program_id / "PROGRAM.md"
    reject_symlink_path(root, archive_path)
    if archive_path.exists():
        raise ProjectOSError(f"Program archive already exists: {archive_path.relative_to(root)}")
    if any(
        isinstance(entry, dict) and entry.get("id") == program_id
        for entry in history_index["entries"]
    ):
        raise ProjectOSError(f"History already contains Program id {program_id}")
    entry: dict[str, Any] = {
        "id": program_id,
        "kind": "program",
        "path": archive_path.relative_to(root).as_posix(),
        "sha256": "sha256:" + program_digest,
        "closed_on": date.today().isoformat(),
        "disposition": disposition,
    }
    if reason:
        entry["reason"] = reason.strip()
    history_index["entries"].append(entry)

    next_system = copy.deepcopy(system)
    next_system["mode"] = "standard"
    next_system["active_program"] = None
    next_system["paths"]["program"] = None
    next_system["paths"]["history"] = history_path.relative_to(root).as_posix()
    next_system["paths"]["history_index"] = index_path.relative_to(root).as_posix()
    next_system["generated_on"] = date.today().isoformat()

    creates: list[tuple[Path, str | bytes]] = [(archive_path, program_content)]
    replacements: list[tuple[Path, str, str]] = []
    serialized_index = json.dumps(history_index, indent=2, ensure_ascii=False) + "\n"
    if index_sha256 is None:
        creates.append((index_path, serialized_index))
    else:
        replacements.append((index_path, serialized_index, index_sha256))
    readme_path = history_path / "README.md"
    if not readme_path.exists():
        creates.append((readme_path, HISTORY_README_TEMPLATE.read_text(encoding="utf-8")))
    system_path = root / ".agents" / "SYSTEM.json"
    replacements.append(
        (
            system_path,
            json.dumps(next_system, indent=2, ensure_ascii=False) + "\n",
            hashlib.sha256(system_path.read_bytes()).hexdigest(),
        )
    )
    deletions = [(program_path, program_digest)]
    print_transaction_preview(root, creates, replacements, deletions)
    if dry_run:
        print("dry-run: no files written")
        return 0
    execute_sync_transaction(
        root,
        creates,
        replacements,
        deletions,
        after_write=lambda: require_passing_check(root, "Program close"),
    )
    return 0


def validate_system_selection(system: dict[str, Any]) -> tuple[list[str], list[str]]:
    packs = system.get("packs")
    overlays = system.get("overlays")
    if not isinstance(packs, list) or any(
        not isinstance(name, str) or name not in PACK_NAMES for name in packs
    ):
        raise ProjectOSError("SYSTEM packs must contain known capability packs")
    if not isinstance(overlays, list) or any(
        not isinstance(name, str) or name not in OVERLAY_NAMES for name in overlays
    ):
        raise ProjectOSError("SYSTEM overlays must contain known ecosystem overlays")
    if packs != [name for name in PACK_NAMES if name in set(packs)]:
        raise ProjectOSError("SYSTEM packs must be unique and in canonical order")
    if overlays != [name for name in OVERLAY_NAMES if name in set(overlays)]:
        raise ProjectOSError("SYSTEM overlays must be unique and in canonical order")
    validate_overlay_dependencies(packs, overlays)
    if system.get("pack_paths") != [f".agents/packs/{name}.md" for name in packs]:
        raise ProjectOSError("SYSTEM pack_paths do not match selected packs")
    if system.get("overlay_paths") != [
        f".agents/packs/overlays/{name}.md" for name in overlays
    ]:
        raise ProjectOSError("SYSTEM overlay_paths do not match selected overlays")
    return list(packs), list(overlays)


def plan_managed_release_update(
    root: Path,
    original_system: dict[str, Any],
    next_system: dict[str, Any],
) -> tuple[list[tuple[Path, str]], list[tuple[Path, str, str]]]:
    """Plan conflict-safe managed guidance and knowledge updates without writing."""
    packs, overlays = validate_system_selection(original_system)
    expected = default_system(
        root,
        str(next_system.get("mode")),
        str(next_system.get("installation")),
        packs,
        overlays,
        next_system.get("paths", {}),
        next_system.get("active_program")
        if isinstance(next_system.get("active_program"), dict)
        else None,
    )
    recorded_guidance = original_system.get("managed_guidance")
    expected_guidance = expected["managed_guidance"]
    if not isinstance(recorded_guidance, dict) or list(recorded_guidance) != list(
        expected_guidance
    ):
        raise ProjectOSError("SYSTEM managed_guidance is missing or inconsistent")
    if any(not isinstance(value, str) for value in recorded_guidance.values()):
        raise ProjectOSError("SYSTEM managed_guidance contains an invalid baseline")
    recorded_knowledge = original_system.get("managed_knowledge")
    if not isinstance(recorded_knowledge, dict) or any(
        not isinstance(entry_id, str) or not isinstance(entry_hash, str)
        for entry_id, entry_hash in (
            recorded_knowledge.items() if isinstance(recorded_knowledge, dict) else ()
        )
    ):
        raise ProjectOSError("SYSTEM managed_knowledge is missing or invalid")

    creates: list[tuple[Path, str | bytes]] = []
    replacements: list[tuple[Path, str, str]] = []
    conflicts: list[str] = []
    guidance_contents = guidance_content_map(packs, overlays)
    for raw_path, recorded_hash in recorded_guidance.items():
        path = safe_relative(root, raw_path)
        if path is None:
            raise ProjectOSError(f"Managed guidance path is unsafe: {raw_path}")
        reject_symlink_path(root, path)
        desired_hash = expected_guidance[raw_path]
        desired_content = guidance_contents[raw_path]
        if not path.exists():
            creates.append((path, desired_content))
            continue
        if not path.is_file():
            raise ProjectOSError(f"Managed guidance is not a regular file: {raw_path}")
        actual_digest = hashlib.sha256(path.read_bytes()).hexdigest()
        actual_hash = "sha256:" + actual_digest
        if actual_hash == desired_hash:
            continue
        if actual_hash == recorded_hash:
            replacements.append((path, desired_content, actual_digest))
        else:
            conflicts.append(f"managed guidance differs locally: {raw_path}")

    paths = original_system.get("paths")
    if not isinstance(paths, dict):
        raise ProjectOSError("SYSTEM paths must contain an object")
    destination = safe_relative(root, paths.get("shared_knowledge"))
    if destination is None:
        raise ProjectOSError("SYSTEM shared knowledge path is unsafe or missing")
    reject_symlink_path(root, destination)
    desired = composed_knowledge(packs, overlays)
    validate_composed_knowledge(desired, packs, overlays)
    destination_digest: str | None = None
    if destination.exists():
        if not destination.is_file():
            raise ProjectOSError("Shared knowledge destination must be a regular file")
        destination_digest = hashlib.sha256(destination.read_bytes()).hexdigest()
        current = load_json(destination)
        registry_errors: list[str] = []
        validate_failure_registry(
            destination,
            "shared knowledge",
            registry_errors,
            verify_hashes=True,
            strict_managed=True,
        )
        if registry_errors:
            conflicts.extend(registry_errors)
    else:
        current = {
            "schema_version": 1,
            "knowledge_version": "0.0.0",
            "packs": ["core", *packs],
            "overlays": overlays,
            "entries": [],
        }
    if not isinstance(current, dict) or not isinstance(current.get("entries"), list):
        raise ProjectOSError("Shared knowledge must contain an entries array")
    if destination.exists() and current.get("packs") != ["core", *packs]:
        conflicts.append("shared knowledge packs do not match SYSTEM packs")
    if destination.exists() and current.get("overlays") != overlays:
        conflicts.append("shared knowledge overlays do not match SYSTEM overlays")
    for label in private_material_labels(current):
        conflicts.append(f"shared knowledge contains a {label}")

    current_by_id: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(current["entries"]):
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            raise ProjectOSError(f"Invalid shared knowledge entry at index {index}")
        if entry["id"] in current_by_id:
            raise ProjectOSError(f"Duplicate shared knowledge id: {entry['id']}")
        current_by_id[entry["id"]] = entry
    desired_by_id = {entry["id"]: entry for entry in desired["entries"]}
    additions: list[dict[str, Any]] = []
    updates: list[dict[str, Any]] = []
    for entry in desired["entries"]:
        existing = current_by_id.get(entry["id"])
        if existing is None:
            additions.append(entry)
        elif existing == entry:
            continue
        elif entry_content_hash(existing) == recorded_knowledge.get(entry["id"]):
            updates.append(entry)
        else:
            conflicts.append(f"shared knowledge differs locally: {entry['id']}")
    retained = sorted(set(current_by_id).difference(desired_by_id))
    for entry_id in retained:
        source = current_by_id[entry_id].get("source")
        source_kind = source.get("kind") if isinstance(source, dict) else None
        if (
            isinstance(source_kind, str)
            and source_kind in {"project-os-pack", "incident-derived"}
            and entry_id not in recorded_knowledge
        ):
            conflicts.append(f"shared knowledge has an unreviewed managed entry: {entry_id}")
    if conflicts:
        raise ProjectOSError("Upgrade conflicts: " + "; ".join(conflicts))
    print(f"knowledge additions: {len(additions)}")
    print(f"knowledge updates: {len(updates)}")
    next_by_id = dict(current_by_id)
    for entry in [*additions, *updates]:
        next_by_id[entry["id"]] = entry
    current["entries"] = sorted(
        next_by_id.values(), key=lambda entry: str(entry.get("id", ""))
    )
    current["knowledge_version"] = VERSION
    current["packs"] = ["core", *packs]
    current["overlays"] = overlays
    serialized = json.dumps(current, indent=2, ensure_ascii=False) + "\n"
    if destination_digest is None:
        creates.append((destination, serialized))
    elif hashlib.sha256(serialized.encode("utf-8")).hexdigest() != destination_digest:
        replacements.append((destination, serialized, destination_digest))

    next_managed_knowledge = {
        entry_id: entry_hash
        for entry_id, entry_hash in recorded_knowledge.items()
        if entry_id in retained
    }
    next_managed_knowledge.update(expected["managed_knowledge"])
    next_system["schema_version"] = SCHEMA_VERSION
    next_system["project_os_version"] = VERSION
    next_system["managed_guidance"] = expected_guidance
    next_system["managed_knowledge"] = dict(sorted(next_managed_knowledge.items()))
    comparison_before = copy.deepcopy(original_system)
    comparison_after = copy.deepcopy(next_system)
    comparison_before.pop("generated_on", None)
    comparison_after.pop("generated_on", None)
    if comparison_after != comparison_before or creates or replacements:
        next_system["generated_on"] = date.today().isoformat()
    return creates, replacements


def upgrade_project(
    root: Path,
    legacy_program_state: str | None,
    disposition: str | None,
    closed_on: str | None,
    reason: str | None,
    dry_run: bool,
) -> int:
    root = root.resolve()
    system_path = root / ".agents" / "SYSTEM.json"
    reject_symlink_path(root, system_path)
    loaded = load_json(system_path)
    if not isinstance(loaded, dict):
        raise ProjectOSError("SYSTEM configuration must contain an object")
    original_system = loaded
    schema = original_system.get("schema_version")
    if not isinstance(schema, int) or schema not in {2, SCHEMA_VERSION}:
        raise ProjectOSError(
            f"Upgrade supports SYSTEM schema 2 or {SCHEMA_VERSION}, got {schema!r}"
        )
    if not isinstance(original_system.get("installation"), str) or original_system.get(
        "installation"
    ) not in {"initialized", "adopted"}:
        raise ProjectOSError("SYSTEM installation must be initialized or adopted")
    validate_system_selection(original_system)
    if not isinstance(original_system.get("paths"), dict):
        raise ProjectOSError("SYSTEM paths must contain an object")

    next_system = copy.deepcopy(original_system)
    next_paths = next_system["paths"]
    next_paths.setdefault("history_index", None)
    creates: list[tuple[Path, str | bytes]] = []
    replacements: list[tuple[Path, str, str]] = []
    deletions: list[tuple[Path, str]] = []

    if schema == SCHEMA_VERSION:
        if any(
            value is not None
            for value in (legacy_program_state, disposition, closed_on, reason)
        ):
            raise ProjectOSError("Legacy Program flags are valid only for a schema 2 upgrade")
        if not isinstance(next_system.get("mode"), str) or next_system.get("mode") not in {
            "standard",
            "program",
        }:
            raise ProjectOSError("Schema 3 SYSTEM mode must be standard or program")
        if "active_program" not in next_system:
            raise ProjectOSError("Schema 3 SYSTEM must declare active_program")
        require_safe_system_owners(root, next_system)
    else:
        old_mode = original_system.get("mode")
        if not isinstance(old_mode, str) or old_mode not in {"lite", "full"}:
            raise ProjectOSError("Schema 2 SYSTEM mode must be lite or full")
        if old_mode == "lite":
            if any(
                value is not None
                for value in (legacy_program_state, disposition, closed_on, reason)
            ):
                raise ProjectOSError("Lite migration does not accept legacy Program flags")
            if next_paths.get("program") is not None:
                raise ProjectOSError("Lite schema 2 state cannot declare a Program path")
            next_system["mode"] = "standard"
            next_system["active_program"] = None
            next_paths["program"] = None
            if next_paths.get("history") is None:
                next_paths["history_index"] = None
            require_safe_system_owners(root, next_system)
        else:
            if legacy_program_state not in {"active", "closed"}:
                raise ProjectOSError(
                    "Schema 2 Full migration requires --legacy-program-state active or closed"
                )
            raw_program = next_paths.get("program") or PROGRAM_RELATIVE_PATH
            if raw_program != PROGRAM_RELATIVE_PATH:
                raise ProjectOSError(
                    f"Schema 2 Program migration requires paths.program to be {PROGRAM_RELATIVE_PATH}"
                )
            next_paths["program"] = raw_program
            owner_check_system = copy.deepcopy(next_system)
            owner_check_system["mode"] = "program"
            require_safe_system_owners(root, owner_check_system)
            program_path = safe_relative(root, raw_program)
            if program_path is None or not program_path.is_file():
                raise ProjectOSError("Schema 2 Full migration requires an existing PROGRAM.md")
            reject_symlink_path(root, program_path)
            history_path, index_path, history_index, index_sha256 = load_history_for_mutation(
                root, next_system
            )
            next_paths["history"] = history_path.relative_to(root).as_posix()
            next_paths["history_index"] = index_path.relative_to(root).as_posix()
            readme_path = history_path / "README.md"
            if not readme_path.exists():
                creates.append(
                    (readme_path, HISTORY_README_TEMPLATE.read_text(encoding="utf-8"))
                )
            elif not readme_path.is_file() or readme_path.is_symlink():
                raise ProjectOSError("History README must be a regular file when present")
            program_id = next_program_id(history_index, history_path)
            if legacy_program_state == "active":
                if disposition is not None or closed_on is not None or reason is not None:
                    raise ProjectOSError("Active legacy Program migration cannot set disposition")
                next_system["mode"] = "program"
                next_system["active_program"] = {
                    "id": program_id,
                    "initiative": "Migrated schema 2 Program",
                    "started_on": None,
                    "migrated_on": date.today().isoformat(),
                    "origin": "legacy-migration",
                }
                next_paths["program"] = program_path.relative_to(root).as_posix()
                if index_sha256 is None:
                    creates.append((index_path, json.dumps(history_index, indent=2) + "\n"))
            else:
                if disposition not in {"completed", "stopped"}:
                    raise ProjectOSError(
                        "Closed legacy Program migration requires --disposition completed or stopped"
                    )
                actual_closed_on = canonical_date(
                    closed_on, "Closed legacy Program migration --closed-on"
                )
                if disposition == "stopped" and (not reason or not reason.strip()):
                    raise ProjectOSError("A stopped legacy Program requires --reason")
                if active_plan_ids(root, original_system):
                    raise ProjectOSError(
                        "Close the active plan before migrating a closed legacy Program"
                    )
                archive_path = history_path / "programs" / program_id / "PROGRAM.md"
                reject_symlink_path(root, archive_path)
                if archive_path.exists():
                    raise ProjectOSError(
                        f"Program archive already exists: {archive_path.relative_to(root)}"
                    )
                program_content = program_path.read_bytes()
                program_digest = hashlib.sha256(program_content).hexdigest()
                history_entry: dict[str, Any] = {
                    "id": program_id,
                    "kind": "program",
                    "path": archive_path.relative_to(root).as_posix(),
                    "sha256": "sha256:" + program_digest,
                    "closed_on": actual_closed_on,
                    "disposition": disposition,
                }
                if reason:
                    history_entry["reason"] = reason.strip()
                history_index["entries"].append(history_entry)
                creates.append((archive_path, program_content))
                serialized_index = json.dumps(history_index, indent=2, ensure_ascii=False) + "\n"
                if index_sha256 is None:
                    creates.append((index_path, serialized_index))
                else:
                    replacements.append((index_path, serialized_index, index_sha256))
                deletions.append((program_path, program_digest))
                next_system["mode"] = "standard"
                next_system["active_program"] = None
                next_paths["program"] = None

    managed_creates, managed_replacements = plan_managed_release_update(
        root, original_system, next_system
    )
    creates.extend(managed_creates)
    replacements.extend(managed_replacements)
    serialized_system = json.dumps(next_system, indent=2, ensure_ascii=False) + "\n"
    original_digest = hashlib.sha256(system_path.read_bytes()).hexdigest()
    if hashlib.sha256(serialized_system.encode("utf-8")).hexdigest() != original_digest:
        replacements.append((system_path, serialized_system, original_digest))

    print(f"upgrade schema: {schema} -> {SCHEMA_VERSION}")
    print(f"upgrade mode: {original_system.get('mode')} -> {next_system.get('mode')}")
    print_transaction_preview(root, creates, replacements, deletions)
    if dry_run:
        print("dry-run: no files written")
        return 0
    execute_sync_transaction(
        root,
        creates,
        replacements,
        deletions,
        after_write=lambda: require_passing_check(root, "Upgrade"),
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    detect_parser = subparsers.add_parser("detect", help="Inspect toolchain and capability signals")
    detect_parser.add_argument("--target", required=True, type=Path)

    init_parser = subparsers.add_parser("init", help="Create a new Project OS control plane")
    init_parser.add_argument("--target", required=True, type=Path)
    init_parser.add_argument(
        "--packs", default="auto", help="auto, none, or comma-separated capability packs"
    )
    init_parser.add_argument(
        "--overlays", default="auto", help="auto, none, or comma-separated ecosystem overlays"
    )
    init_parser.add_argument("--dry-run", action="store_true")
    init_parser.add_argument(
        "--allow-existing-agents",
        action="store_true",
        help="preserve an existing AGENTS.md that already routes to CONTEXT.md and STATE.md",
    )

    adopt_parser = subparsers.add_parser(
        "adopt", help="Discover and safely attach to an existing Project OS-like layout"
    )
    adopt_parser.add_argument("--target", required=True, type=Path)
    adopt_parser.add_argument("--dry-run", action="store_true")
    adopt_parser.add_argument(
        "--inventory", action="store_true", help="include legacy Markdown lesson inventory"
    )

    check_parser = subparsers.add_parser("check", help="Validate Project OS state and invariants")
    check_parser.add_argument("--target", required=True, type=Path)
    check_parser.add_argument("--config", type=Path, help="validate against a proposed SYSTEM manifest")

    sync_parser = subparsers.add_parser(
        "sync-knowledge", help="Add selected guidance and lessons without overwriting conflicts"
    )
    sync_parser.add_argument("--target", required=True, type=Path)
    sync_parser.add_argument("--packs", default="selected")
    sync_parser.add_argument("--overlays", default="selected")
    sync_parser.add_argument("--dry-run", action="store_true")

    upgrade_parser = subparsers.add_parser(
        "upgrade", help="Upgrade schema, managed guidance, knowledge, and release metadata"
    )
    upgrade_parser.add_argument("--target", required=True, type=Path)
    upgrade_parser.add_argument(
        "--legacy-program-state",
        choices=("active", "closed"),
        help="required classification when migrating a schema 2 Full repository",
    )
    upgrade_parser.add_argument("--disposition", choices=("completed", "stopped"))
    upgrade_parser.add_argument("--closed-on")
    upgrade_parser.add_argument("--reason")
    upgrade_parser.add_argument("--dry-run", action="store_true")

    program_parser = subparsers.add_parser("program", help="Manage a multi-phase Program")
    program_subparsers = program_parser.add_subparsers(
        dest="program_command", required=True
    )
    program_start_parser = program_subparsers.add_parser(
        "start", help="Start a Program from a validated JSON definition"
    )
    program_start_parser.add_argument("--target", required=True, type=Path)
    program_start_parser.add_argument("--definition", required=True, type=Path)
    program_start_parser.add_argument("--dry-run", action="store_true")
    program_status_parser = program_subparsers.add_parser(
        "status", help="Report current Program state"
    )
    program_status_parser.add_argument("--target", required=True, type=Path)
    program_close_parser = program_subparsers.add_parser(
        "close", help="Archive and close the active Program"
    )
    program_close_parser.add_argument("--target", required=True, type=Path)
    program_close_parser.add_argument(
        "--disposition", required=True, choices=("completed", "stopped")
    )
    program_close_parser.add_argument("--reason")
    program_close_parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "detect":
            print(json.dumps(detect_repository(args.target), indent=2, ensure_ascii=False))
            return 0
        if args.command == "init":
            return init_project(
                args.target,
                args.packs,
                args.overlays,
                args.dry_run,
                args.allow_existing_agents,
            )
        if args.command == "adopt":
            return adopt_project(args.target, args.dry_run, args.inventory)
        if args.command == "check":
            return check_project(args.target, args.config)
        if args.command == "sync-knowledge":
            return sync_knowledge(args.target, args.packs, args.overlays, args.dry_run)
        if args.command == "upgrade":
            return upgrade_project(
                args.target,
                args.legacy_program_state,
                args.disposition,
                args.closed_on,
                args.reason,
                args.dry_run,
            )
        if args.command == "program":
            if args.program_command == "start":
                return start_program(args.target, args.definition, args.dry_run)
            if args.program_command == "status":
                return program_status(args.target)
            if args.program_command == "close":
                return close_program(
                    args.target, args.disposition, args.reason, args.dry_run
                )
    except ProjectOSError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
