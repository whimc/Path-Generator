"""Resolve the running Path-Generator version.

Preference order:
1. Latest matching git tag (`v*`) when a checkout with tags is available
2. The repo-root `VERSION` file
"""

from __future__ import annotations

import subprocess
from functools import lru_cache
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_VERSION_FILE = _REPO_ROOT / 'VERSION'


def _version_from_git() -> str | None:
    try:
        tag = subprocess.check_output(
            ['git', 'describe', '--tags', '--match', 'v*', '--abbrev=0'],
            cwd=_REPO_ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None

    if tag.startswith('v'):
        tag = tag[1:]
    return tag or None


def _version_from_file() -> str:
    try:
        return _VERSION_FILE.read_text(encoding='utf-8').strip()
    except OSError:
        return '0.0'


@lru_cache(maxsize=1)
def get_version() -> str:
    return _version_from_git() or _version_from_file()


__version__ = get_version()
