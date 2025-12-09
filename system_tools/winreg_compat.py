from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Dict, Tuple


if sys.platform.startswith("win"):
    import winreg  # type: ignore  # noqa: F401
else:
    # Minimal in-memory stand-in for winreg to allow cross-platform testing.
    @dataclass
    class _RegistryKey:
        path: str

        def __enter__(self) -> "_RegistryKey":  # pragma: no cover - trivial
            return self

        def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # pragma: no cover - trivial
            return None

    class _InMemoryWinreg:
        HKEY_CURRENT_USER = "HKEY_CURRENT_USER"
        HKEY_LOCAL_MACHINE = "HKEY_LOCAL_MACHINE"

        def __init__(self) -> None:
            self.values: Dict[Tuple[str, str], Tuple[int, object]] = {}

        def CreateKeyEx(self, hive: str, sub_key: str) -> _RegistryKey:
            return _RegistryKey(f"{hive}\\{sub_key}")

        def SetValueEx(self, key: _RegistryKey, name: str, reserved: int, value_type: int, value: object) -> None:
            self.values[(key.path, name)] = (value_type, value)

    winreg = _InMemoryWinreg()

__all__ = ["winreg"]
