#!/usr/bin/env python3
"""Create or check a complete byte snapshot; this does not validate Project OS records."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import os
import stat
import unicodedata
import zipfile
from pathlib import Path, PurePosixPath


_SPEC = importlib.util.spec_from_file_location(
    "project_os_snapshot_runtime", Path(__file__).with_name("project_os.py")
)
_RUNTIME = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_RUNTIME)
SnapshotError = _RUNTIME.ProjectOSError
MANIFEST = "PROJECT-OS-SNAPSHOT.json"
MAX_ENTRIES = 50000
MAX_BYTES = 512 * 1024 * 1024
MAX_MANIFEST_BYTES = 16 * 1024 * 1024
MAX_ARCHIVE_BYTES = MAX_BYTES + 4 * MAX_MANIFEST_BYTES


def safe_relative(value: str) -> str:
    path = PurePosixPath(value)
    if (not value or value == "." or "\\" in value or "\x00" in value or path.is_absolute()
            or any(part in {".", "..", ""} for part in path.parts)
            or path.as_posix() != value or ":" in path.parts[0]):
        raise SnapshotError(f"Unsafe snapshot path: {value!r}")
    return value


def portable_key(component: str) -> str:
    return unicodedata.normalize("NFD", unicodedata.normalize("NFD", component).casefold())


class PortablePaths:
    """Reject aliases without rewriting spellings, in linear path-segment work."""

    def __init__(self):
        self.children = {}

    def add(self, value: str, directory: bool = False) -> None:
        parts = PurePosixPath(safe_relative(value)).parts
        children = self.children
        for index, component in enumerate(parts):
            final = index == len(parts) - 1
            expected_directory = directory or not final
            key = portable_key(component)
            current = children.get(key)
            if current is None:
                current = {"name": component, "directory": expected_directory,
                           "explicit": final, "children": {}}
                children[key] = current
            else:
                if current["name"] != component or current["directory"] != expected_directory:
                    raise SnapshotError(f"Portable snapshot path collision: {value!r} aliases {current['name']!r}")
                if final and current["explicit"]:
                    raise SnapshotError(f"Duplicate snapshot path: {value}")
                current["explicit"] = current["explicit"] or final
            children = current["children"]


def validate_namespace(files, directories) -> None:
    paths = PortablePaths()
    paths.add(MANIFEST)
    for name in directories:
        paths.add(name, directory=True)
    for name in files:
        paths.add(name)


def absolute_path(value: Path) -> Path:
    path = value.expanduser().absolute()
    if ".." in path.parts:
        raise SnapshotError(f"Path must not contain parent traversal: {path}")
    return path


def identity(details: os.stat_result) -> tuple:
    return (details.st_dev, details.st_ino, details.st_size,
            details.st_mtime_ns, details.st_ctime_ns)


def bounded_read_at(directory_fd: int, name: str, limit: int) -> tuple[bytes, os.stat_result]:
    descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory_fd)
    with os.fdopen(descriptor, "rb") as handle:
        before = os.fstat(handle.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
            raise SnapshotError(f"Snapshot read exceeds its regular-file byte limit: {name}")
        content = bytearray()
        while True:
            chunk = handle.read(min(65536, limit - len(content) + 1))
            if not chunk:
                break
            content.extend(chunk)
            if len(content) > limit:
                raise SnapshotError(f"Snapshot read exceeds its byte limit: {name}")
        after = os.fstat(handle.fileno())
        if identity(before) != identity(after) or len(content) != after.st_size:
            raise SnapshotError(f"Snapshot file changed during read: {name}")
        return bytes(content), after


def collect_tree(filesystem) -> dict:
    """Read the actual tree through anchored descriptors, including hidden files."""
    files, directories, identities = {}, [], {}
    paths = PortablePaths()
    paths.add(MANIFEST)
    total = 0

    def visit(path: Path, descriptor: int) -> None:
        nonlocal total
        for name in sorted(os.listdir(descriptor)):
            child = path / name
            relative = safe_relative(child.relative_to(filesystem.root).as_posix())
            if portable_key(relative) == portable_key(MANIFEST):
                raise SnapshotError(f"Source collides with reserved inventory: {MANIFEST}")
            if len(files) + len(directories) >= MAX_ENTRIES:
                raise SnapshotError("Snapshot exceeds the entry limit")
            before = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
            if stat.S_ISDIR(before.st_mode):
                paths.add(relative, directory=True)
                directories.append(relative)
                nested = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                 dir_fd=descriptor)
                try:
                    opened = os.fstat(nested)
                    if (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
                        raise SnapshotError(f"Source directory changed during read: {relative}")
                    identities[relative + "/"] = (opened.st_dev, opened.st_ino)
                    visit(child, nested)
                    after = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
                    if (not stat.S_ISDIR(after.st_mode)
                            or (after.st_dev, after.st_ino) != (opened.st_dev, opened.st_ino)):
                        raise SnapshotError(f"Source directory changed during read: {relative}")
                finally:
                    os.close(nested)
            elif stat.S_ISREG(before.st_mode):
                paths.add(relative)
                if before.st_size > MAX_BYTES - total:
                    raise SnapshotError("Snapshot exceeds the byte limit")
                content, opened = bounded_read_at(descriptor, name, MAX_BYTES - total)
                after = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
                if (not stat.S_ISREG(after.st_mode) or identity(before) != identity(opened)
                        or identity(opened) != identity(after) or len(content) != after.st_size):
                    raise SnapshotError(f"Source file changed during read: {relative}")
                total += len(content)
                if total > MAX_BYTES:
                    raise SnapshotError("Snapshot exceeds the byte limit")
                files[relative] = content
                identities[relative] = identity(after)
            else:
                raise SnapshotError(f"Snapshot source must contain only regular files/directories: {relative}")

    visit(filesystem.root, filesystem.directories[filesystem.root])
    filesystem.verify()
    return {"files": files, "directories": sorted(directories), "identities": identities}


def required_paths(snapshot: dict, values) -> list[str]:
    required = sorted({safe_relative(value) for value in values})
    for name in required:
        if name in snapshot["files"]:
            continue
        if name in snapshot["directories"] and any(
            path.startswith(name + "/") for path in snapshot["files"]
        ):
            continue
        raise SnapshotError(f"Required snapshot path is missing or an empty directory: {name}")
    return required


def inventory(snapshot: dict, required: list[str]) -> dict:
    validate_namespace(snapshot["files"], snapshot["directories"])
    return {
        "format": "project-os-byte-snapshot",
        "schema_version": 1,
        "algorithm": "sha256",
        "required_paths": required,
        "directories": snapshot["directories"],
        "files": [
            {"path": name, "size": len(content),
             "sha256": hashlib.sha256(content).hexdigest()}
            for name, content in sorted(snapshot["files"].items())
        ],
    }


def write_zip(handle, snapshot: dict, required: list[str]) -> None:
    serialized = (json.dumps(inventory(snapshot, required), indent=2, sort_keys=True) + "\n").encode()
    if len(serialized) > MAX_MANIFEST_BYTES:
        raise SnapshotError("Snapshot inventory exceeds the byte limit")
    contents = dict(snapshot["files"])
    contents.update({name + "/": b"" for name in snapshot["directories"]})
    contents[MANIFEST] = serialized
    with zipfile.ZipFile(handle, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in sorted(contents.items()):
            entry = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = ((stat.S_IFDIR | 0o755) if name.endswith("/")
                                   else (stat.S_IFREG | 0o600)) << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, content)


def verify_zip(data: bytes, snapshot: dict, required: list[str]) -> None:
    """Compare the serialized artifact with the source, not just its own manifest."""
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        entries = archive.infolist()
        if len(entries) > MAX_ENTRIES + 1:
            raise SnapshotError("Snapshot exceeds the entry limit")
        paths = PortablePaths()
        for entry in entries:
            directory = entry.filename.endswith("/")
            paths.add(entry.filename[:-1] if directory else entry.filename, directory)
        names = [entry.filename for entry in entries]
        expected = set(snapshot["files"]) | {name + "/" for name in snapshot["directories"]} | {MANIFEST}
        if len(names) != len(set(names)) or set(names) != expected:
            raise SnapshotError("Snapshot paths differ from the actual source inventory")
        for entry in entries:
            directory = entry.filename.endswith("/")
            safe_relative(entry.filename[:-1] if directory else entry.filename)
            mode = entry.external_attr >> 16
            if entry.flag_bits & 1 or (not stat.S_ISDIR(mode) if directory else not stat.S_ISREG(mode)):
                raise SnapshotError(f"Unsafe snapshot ZIP entry: {entry.filename}")
            expected_size = (0 if directory else MAX_MANIFEST_BYTES if entry.filename == MANIFEST
                             else len(snapshot["files"][entry.filename]))
            if entry.file_size > expected_size or (entry.filename != MANIFEST and entry.file_size != expected_size):
                raise SnapshotError(f"Snapshot size differs from source: {entry.filename}")
        manifest = json.loads(archive.read(MANIFEST).decode("utf-8"))
        if (not isinstance(manifest, dict) or not isinstance(manifest.get("files"), list)
                or not isinstance(manifest.get("directories"), list)
                or not all(isinstance(name, str) for name in manifest["directories"])
                or not all(isinstance(row, dict) and isinstance(row.get("path"), str)
                           for row in manifest["files"])):
            raise SnapshotError("Invalid snapshot inventory paths")
        if len(manifest["files"]) + len(manifest["directories"]) > MAX_ENTRIES:
            raise SnapshotError("Snapshot inventory exceeds the entry limit")
        validate_namespace([row["path"] for row in manifest["files"]], manifest["directories"])
        stored_required = manifest.get("required_paths") if isinstance(manifest, dict) else None
        if not isinstance(stored_required, list) or not all(isinstance(name, str) for name in stored_required):
            raise SnapshotError("Invalid snapshot required paths")
        if required_paths(snapshot, stored_required) != stored_required:
            raise SnapshotError("Snapshot required paths are not canonical")
        required_paths(snapshot, required)
        if manifest != inventory(snapshot, stored_required):
            raise SnapshotError("Snapshot inventory differs from the actual source")
        for name, content in snapshot["files"].items():
            if archive.read(name) != content:
                raise SnapshotError(f"Snapshot bytes differ from source: {name}")
        if archive.testzip() is not None:
            raise SnapshotError("Snapshot CRC verification failed")


def ensure_unchanged(filesystem, original: dict) -> None:
    if collect_tree(filesystem) != original:
        raise SnapshotError("Snapshot source paths or bytes changed during operation")


def external_path(root: Path, path: Path) -> Path:
    path = absolute_path(path)
    if path.is_relative_to(root):
        raise SnapshotError("Snapshot archive must be outside the source root")
    return path


def reject_source_ancestor(source, external) -> None:
    source_details = os.fstat(source.directories[source.root])
    source_identity = (source_details.st_dev, source_details.st_ino)
    if any((details.st_dev, details.st_ino) == source_identity
           for details in (os.fstat(descriptor) for descriptor in external.descriptors)):
        raise SnapshotError("Snapshot archive must be outside the source root")


def archive_bytes(filesystem, path: Path) -> tuple[bytes, os.stat_result]:
    parent = filesystem.parent(path)
    details = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
    if not stat.S_ISREG(details.st_mode) or details.st_size > MAX_ARCHIVE_BYTES:
        raise SnapshotError("Snapshot archive must be a bounded regular file")
    data, opened = bounded_read_at(parent, path.name, MAX_ARCHIVE_BYTES)
    if identity(details) != identity(opened):
        raise SnapshotError("Snapshot archive changed during read")
    return data, opened


def write_output(descriptor: int, data: bytes) -> None:
    writer = os.dup(descriptor)
    try:
        handle = os.fdopen(writer, "wb")
    except BaseException:
        os.close(writer)
        raise
    with handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def open_output(directory_fd: int, name: str) -> int:
    return os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                   0o600, dir_fd=directory_fd)


def create(root: Path, output: Path, require=(), dry_run: bool = False) -> dict:
    root = absolute_path(root)
    output = external_path(root, output)
    source = _RUNTIME.AnchoredFilesystem(root)
    destination = None
    descriptor = None
    try:
        destination = _RUNTIME.AnchoredFilesystem(output.parent)
        reject_source_ancestor(source, destination)
        parent = destination.parent(output)
        try:
            os.stat(output.name, dir_fd=parent, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise SnapshotError(f"Refusing to overwrite an existing snapshot: {output}")
        snapshot = collect_tree(source)
        selected = required_paths(snapshot, require)
        result = {"files": len(snapshot["files"]), "directories": len(snapshot["directories"]),
                  "required_paths": selected, "output": str(output), "archive_created": False,
                  "project_os_validation": "NOT_PERFORMED"}
        if dry_run:
            ensure_unchanged(source, snapshot)
            destination.verify()
            return dict(result, operation="create dry-run", transport_integrity="NOT_PERFORMED",
                        inventory=inventory(snapshot, selected))
        with io.BytesIO() as handle:
            write_zip(handle, snapshot, selected)
            if handle.tell() > MAX_ARCHIVE_BYTES:
                raise SnapshotError("Serialized snapshot exceeds its byte limit")
            data = handle.getvalue()
        verify_zip(data, snapshot, selected)
        ensure_unchanged(source, snapshot)
        destination.verify()
        descriptor = open_output(parent, output.name)
        created = os.fstat(descriptor)
        created_identity = (created.st_dev, created.st_ino)
        write_output(descriptor, data)
        ensure_unchanged(source, snapshot)
        destination.verify()
        saved, details = archive_bytes(destination, output)
        if (details.st_dev, details.st_ino) != created_identity or saved != data:
            raise SnapshotError("Published snapshot bytes changed")
        destination.verify()
        return dict(result, operation="create", archive_created=True,
                    transport_integrity="VERIFIED", sha256=hashlib.sha256(data).hexdigest())
    except Exception as error:
        if descriptor is not None:
            raise SnapshotError(
                "Snapshot creation failed after output creation; an unverified output may remain "
                f"at {output}; do not deliver it: {error}"
            ) from error
        raise
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if destination is not None:
            destination.close()
        source.close()


def check(root: Path, archive: Path, require=()) -> dict:
    root = absolute_path(root)
    archive = external_path(root, archive)
    source = _RUNTIME.AnchoredFilesystem(root)
    stored = None
    try:
        stored = _RUNTIME.AnchoredFilesystem(archive.parent)
        reject_source_ancestor(source, stored)
        snapshot = collect_tree(source)
        selected = required_paths(snapshot, require)
        data, details = archive_bytes(stored, archive)
        verify_zip(data, snapshot, selected)
        ensure_unchanged(source, snapshot)
        again, current = archive_bytes(stored, archive)
        if identity(details) != identity(current) or again != data:
            raise SnapshotError("Snapshot archive changed during verification")
        stored.verify()
        return {"operation": "check", "files": len(snapshot["files"]),
                "directories": len(snapshot["directories"]), "required_paths": selected,
                "transport_integrity": "VERIFIED", "project_os_validation": "NOT_PERFORMED",
                "sha256": hashlib.sha256(data).hexdigest()}
    finally:
        if stored is not None:
            stored.close()
        source.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("create", "check"):
        subparser = commands.add_parser(command)
        subparser.add_argument("--root", required=True, type=Path, help="Actual complete input tree, not a copied subset")
        subparser.add_argument("--require", action="append", default=[], help="Required relative file or nonempty directory; repeat as needed")
        if command == "create":
            subparser.add_argument("--output", required=True, type=Path)
            subparser.add_argument("--dry-run", action="store_true")
        else:
            subparser.add_argument("--archive", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = (create(args.root, args.output, args.require, args.dry_run)
                  if args.command == "create" else check(args.root, args.archive, args.require))
    except (SnapshotError, OSError, ValueError, KeyError, zipfile.BadZipFile,
            NotImplementedError, RecursionError) as error:
        parser.exit(2, f"Snapshot failed: {error}\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
