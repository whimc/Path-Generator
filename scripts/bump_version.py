#!/usr/bin/env python3
"""Bump VERSION by 0.1, preferring the higher of the file and latest git tag."""

from __future__ import annotations

import subprocess
import sys
from decimal import Decimal
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = REPO_ROOT / 'VERSION'
STEP = Decimal('0.1')


def latest_tag_version() -> Decimal | None:
    try:
        output = subprocess.check_output(
            ['git', 'tag', '-l', 'v*', '--sort=-v:refname'],
            cwd=REPO_ROOT,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None

    for line in output.splitlines():
        tag = line.strip()
        if not tag:
            continue
        raw = tag[1:] if tag.startswith('v') else tag
        try:
            return Decimal(raw)
        except Exception:
            continue
    return None


def file_version() -> Decimal:
    if not VERSION_FILE.exists():
        return Decimal('1.0')
    return Decimal(VERSION_FILE.read_text(encoding='utf-8').strip())


def main() -> int:
    candidates = [file_version()]
    tag_version = latest_tag_version()
    if tag_version is not None:
        candidates.append(tag_version)

    current = max(candidates)
    nxt = (current + STEP).quantize(STEP)
    VERSION_FILE.write_text(f'{nxt}\n', encoding='utf-8')
    print(nxt)
    return 0


if __name__ == '__main__':
    sys.exit(main())
