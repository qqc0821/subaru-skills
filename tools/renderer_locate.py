#!/usr/bin/env python3
"""Locate the optional PPTX renderer (soffice / pdftoppm) at runtime.

The renderer is an optional enhancer, never a hard dependency. Discovery order:

1. an explicit environment override (SOFFICE_BIN / PDFTOPPM_BIN)
2. the process PATH (shutil.which)
3. well-known absolute install locations
4. runtime-probed cache overrides under the user home (e.g. bundled runtime
   dependencies placed in a bin/override directory)

Home-derived locations are globbed at runtime; no user name or absolute home
path is hard-coded, so this stays portable across machines. If nothing is
found the caller must report the capability as unavailable rather than assume it.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

SOFFICE_NAMES = ("soffice", "libreoffice")
PDFTOPPM_NAMES = ("pdftoppm",)

SOFFICE_ENV = ("SOFFICE_BIN", "LIBREOFFICE_BIN")
PDFTOPPM_ENV = ("PDFTOPPM_BIN",)

ABS_SOFFICE = (
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    "/usr/bin/soffice",
    "/usr/bin/libreoffice",
)
ABS_PDFTOPPM = (
    "/usr/bin/pdftoppm",
    "/opt/homebrew/bin/pdftoppm",
    "/usr/local/bin/pdftoppm",
)

# Globs are relative to the user home and resolved at runtime.
HOME_GLOBS_SOFFICE = (
    ".cache/codex-runtimes/*/dependencies/bin/override/soffice",
    ".cache/codex-runtimes/*/dependencies/bin/soffice",
)
HOME_GLOBS_PDFTOPPM = (
    ".cache/codex-runtimes/*/dependencies/bin/override/pdftoppm",
    ".cache/codex-runtimes/*/dependencies/bin/pdftoppm",
)


def _is_file(value) -> bool:
    return bool(value) and Path(value).is_file()


def locate(names=(), env_names=(), abs_paths=(), home_globs=(), home=None):
    """Return the first executable that exists, or None."""
    for env_name in env_names:
        value = os.environ.get(env_name)
        if _is_file(value):
            return value
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    for candidate in abs_paths:
        if Path(candidate).is_file():
            return candidate
    root = Path(home) if home is not None else Path.home()
    for pattern in home_globs:
        for candidate in sorted(root.glob(pattern)):
            if candidate.is_file():
                return str(candidate)
    return None


def find_soffice(home=None):
    return locate(SOFFICE_NAMES, SOFFICE_ENV, ABS_SOFFICE, HOME_GLOBS_SOFFICE, home)


def find_pdftoppm(home=None):
    return locate(PDFTOPPM_NAMES, PDFTOPPM_ENV, ABS_PDFTOPPM, HOME_GLOBS_PDFTOPPM, home)
