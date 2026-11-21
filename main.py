#!/usr/bin/env python3
"""make.fun entry copier for VELMORA.

Stdlib-only: copies the repo's entry.png to the output directory,
verifies its sha256, prints the digest, and exits 0. No network.
"""

import hashlib
import os
import shutil
import sys

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(REPO_DIR, "entry.png")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")

    shutil.copyfile(SOURCE, dest)

    src_hash = sha256(SOURCE)
    dst_hash = sha256(dest)
    if src_hash != dst_hash:
        print("ERROR: copied file hash mismatch", file=sys.stderr)
        sys.exit(1)

    print(src_hash)
    sys.exit(0)


if __name__ == "__main__":
    main()