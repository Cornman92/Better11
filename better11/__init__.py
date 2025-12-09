from __future__ import annotations

from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parent
_SRC_DIR = _PKG_DIR.parent / "src" / "better11"
__path__ = [str(_PKG_DIR)]
if _SRC_DIR.exists():
    __path__.append(str(_SRC_DIR))