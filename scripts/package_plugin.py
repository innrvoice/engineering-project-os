#!/usr/bin/env python3
"""Build and check the skills-only ZIP from the current working tree (standard library)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
FILES = ("plugin.json", ".codex-plugin/plugin.json", "README.md", "LICENSE",
         "SECURITY.md", "CHANGELOG.md", "CONTRIBUTING.md", "scripts/package_plugin.py")
TREES = ("skills", "assets", "docs")
MAX_ENTRIES = 5000
MAX_COMPRESSED = 100 * 1024 * 1024
MAX_EXTRACTED = 512 * 1024 * 1024


def source_files(root: Path) -> list[Path]:
    paths = [root / name for name in FILES]
    for name in TREES:
        directory = root / name
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError(f"Expected a real package directory: {directory}")
        for path in sorted(directory.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"Symlink is not allowed in the package: {path}")
            if "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            if path.is_file():
                paths.append(path)
            elif not path.is_dir():
                raise ValueError(f"Non-regular package entry: {path}")
    for path in paths:
        if path.is_symlink() or not stat.S_ISREG(path.stat().st_mode):
            raise ValueError(f"Expected a regular package file: {path}")
        if any(parent.is_symlink() for parent in path.parents if parent != root.parent):
            raise ValueError(f"Symlink package parent: {path}")
    return sorted(paths)


def validate_zip(path: Path) -> dict[str, object]:
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        names = {member.filename for member in members}
        if len(names) != len(members) or len(names) > MAX_ENTRIES:
            raise ValueError("ZIP has duplicate paths or too many entries")
        extracted_size = sum(member.file_size for member in members)
        if path.stat().st_size > MAX_COMPRESSED or extracted_size > MAX_EXTRACTED:
            raise ValueError("ZIP exceeds submission size limits")
        for member in members:
            name = member.filename
            normalized = PurePosixPath(name)
            if ("\\" in name or normalized.is_absolute() or ".." in normalized.parts
                    or normalized.as_posix() != name or name.startswith(".agents/")):
                raise ValueError(f"Unsafe ZIP path: {name}")
            if not stat.S_ISREG(member.external_attr >> 16):
                raise ValueError(f"Non-regular ZIP entry: {name}")
        if archive.testzip() is not None:
            raise ValueError("ZIP CRC validation failed")
        if "plugin.json" not in names or "skills/project-os/SKILL.md" not in names:
            raise ValueError("ZIP is missing the portable manifest or skill")
        portable = json.loads(archive.read("plugin.json"))
        compatibility = json.loads(archive.read(".codex-plugin/plugin.json"))
        if portable["version"] != compatibility["version"]:
            raise ValueError("Package manifest versions disagree")
        # Relative public-document links must also work in the extracted artifact.
        public_docs = [name for name in names if name.endswith(".md")
                       and ("/" not in name or name.startswith("docs/"))]
        for name in public_docs:
            text = archive.read(name).decode("utf-8")
            links = re.findall(r"\[[^\]\n]*\]\(([^\s)]+)(?:\s+[^)]*)?\)", text)
            for raw_link in links:
                link = urlsplit(raw_link.strip("<>"))
                if link.scheme or link.netloc or not link.path:
                    continue
                parts = list(PurePosixPath(name).parent.parts)
                for part in PurePosixPath(unquote(link.path)).parts:
                    if part == "..":
                        if not parts:
                            raise ValueError(f"Escaping document link: {name}: {raw_link}")
                        parts.pop()
                    elif part != ".":
                        parts.append(part)
                target = "/".join(parts)
                if target not in names and not any(item.startswith(target + "/") for item in names):
                    raise ValueError(f"Broken packaged document link: {name}: {raw_link}")
        return {"version": portable["version"], "entries": len(members),
                "compressed_bytes": path.stat().st_size, "extracted_bytes": extracted_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def build_zip(root: Path, output: Path) -> dict[str, object]:
    paths = source_files(root)
    # Exclusive output creation prevents replacing an earlier reviewed artifact.
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in paths:
            info = zipfile.ZipInfo(path.relative_to(root).as_posix(), (2026, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
    return validate_zip(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output", type=Path, help="New ZIP path; existing files are never overwritten")
    group.add_argument("--check", type=Path, help="Validate an existing ZIP without writes")
    arguments = parser.parse_args()
    try:
        result = validate_zip(arguments.check) if arguments.check else build_zip(ROOT, arguments.output)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        parser.exit(2, f"Package validation failed: {error}\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
