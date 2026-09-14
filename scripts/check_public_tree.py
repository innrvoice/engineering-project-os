#!/usr/bin/env python3
"""Reject this repository's local working records in a staged or exported source tree."""

import argparse
import subprocess
from pathlib import Path


PUBLIC_RECORD = ".agents/plugins/marketplace.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tree", type=Path, help="inspect an exported directory instead of the Git index")
    args = parser.parse_args()
    if args.tree is not None:
        root = args.tree.resolve()
        if not root.is_dir():
            parser.error("--tree must be an existing directory")
        records = root / ".agents"
        paths = [path.relative_to(root).as_posix() for path in records.rglob("*")
                 if not path.is_dir() or path.is_symlink()]
        if records.is_symlink():
            paths.append(".agents")
    else:
        root = Path(__file__).resolve().parent.parent
        result = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--", ".agents"],
                                capture_output=True, check=True)
        paths = result.stdout.decode("utf-8").strip("\0").split("\0")
    unexpected = sorted(path for path in paths if path and path != PUBLIC_RECORD)
    if unexpected:
        print("FAIL: local working records must not be published:")
        for path in unexpected:
            print(path)
        return 1
    print("PASS: source tree excludes local working records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
