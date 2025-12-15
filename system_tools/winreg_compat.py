"""Compatibility module for Windows registry operations.

Provides a cross-platform compatible interface for registry operations.
On Windows, it uses the real winreg module. On other platforms, it provides
a minimal in-memory implementation for testing.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any, Dict, Tuple


if sys.platform.startswith("win"):
    from winreg import *  # noqa: F401, F403
    import winreg as _winreg
    winreg = _winreg  # For compatibility
else:
    # Registry root key constants
    HKEY_CLASSES_ROOT = 0x80000000
    HKEY_CURRENT_USER = 0x80000001
    HKEY_LOCAL_MACHINE = 0x80000002
    HKEY_USERS = 0x80000003
    HKEY_CURRENT_CONFIG = 0x80000005

    # Access rights
    KEY_READ = 0x20019
    KEY_WRITE = 0x20006
    KEY_ALL_ACCESS = 0xF003F

    # Value types
    REG_SZ = 1
    REG_BINARY = 3
    REG_DWORD = 4
    REG_MULTI_SZ = 7
    REG_QWORD = 11

    @dataclass
    class _RegistryKey:
        """Mock registry key handle."""
        path: str
        hive: Any = None

        def __enter__(self) -> "_RegistryKey":
            return self

        def __exit__(self, exc_type, exc_val, exc_tb) -> None:
            return None

    # In-memory registry store for testing
    _registry_store: Dict[Tuple[Any, str, str], Tuple[int, Any]] = {}

    def CreateKeyEx(
        key: Any,
        sub_key: str,
        reserved: int = 0,
        access: int = KEY_WRITE
    ) -> _RegistryKey:
        """Create or open a registry key."""
        return _RegistryKey(path=sub_key, hive=key)

    def OpenKey(
        key: Any,
        sub_key: str,
        reserved: int = 0,
        access: int = KEY_READ
    ) -> _RegistryKey:
        """Open a registry key."""
        return _RegistryKey(path=sub_key, hive=key)

    def CloseKey(key: _RegistryKey) -> None:
        """Close a registry key."""
        pass

    def SetValueEx(
        key: _RegistryKey,
        value_name: str,
        reserved: int,
        value_type: int,
        value: Any
    ) -> None:
        """Set a registry value."""
        _registry_store[(key.hive, key.path, value_name)] = (value_type, value)

    def QueryValueEx(key: _RegistryKey, value_name: str) -> Tuple[Any, int]:
        """Query a registry value."""
        store_key = (key.hive, key.path, value_name)
        if store_key in _registry_store:
            value_type, value = _registry_store[store_key]
            return (value, value_type)
        raise FileNotFoundError(f"Registry value not found: {value_name}")

    def DeleteValue(key: _RegistryKey, value_name: str) -> None:
        """Delete a registry value."""
        store_key = (key.hive, key.path, value_name)
        if store_key in _registry_store:
            del _registry_store[store_key]
        else:
            raise FileNotFoundError(f"Registry value not found: {value_name}")

    def DeleteKey(key: Any, sub_key: str) -> None:
        """Delete a registry key."""
        # Remove all values under this key
        keys_to_remove = [k for k in _registry_store if k[0] == key and k[1] == sub_key]
        for k in keys_to_remove:
            del _registry_store[k]

    def EnumValue(key: _RegistryKey, index: int) -> Tuple[str, Any, int]:
        """Enumerate registry values."""
        matching = [(k, v) for k, v in _registry_store.items() 
                   if k[0] == key.hive and k[1] == key.path]
        if index >= len(matching):
            raise OSError("No more values")
        store_key, (value_type, value) = matching[index]
        return (store_key[2], value, value_type)

    def EnumKey(key: _RegistryKey, index: int) -> str:
        """Enumerate registry subkeys."""
        raise OSError("No more keys")

    def clear_registry_store() -> None:
        """Clear the in-memory registry store (for testing)."""
        _registry_store.clear()

    # For compatibility, create a module-like object
    class _ModuleLike:
        HKEY_CLASSES_ROOT = HKEY_CLASSES_ROOT
        HKEY_CURRENT_USER = HKEY_CURRENT_USER
        HKEY_LOCAL_MACHINE = HKEY_LOCAL_MACHINE
        HKEY_USERS = HKEY_USERS
        HKEY_CURRENT_CONFIG = HKEY_CURRENT_CONFIG
        KEY_READ = KEY_READ
        KEY_WRITE = KEY_WRITE
        KEY_ALL_ACCESS = KEY_ALL_ACCESS
        REG_SZ = REG_SZ
        REG_BINARY = REG_BINARY
        REG_DWORD = REG_DWORD
        REG_MULTI_SZ = REG_MULTI_SZ
        REG_QWORD = REG_QWORD
        CreateKeyEx = staticmethod(CreateKeyEx)
        OpenKey = staticmethod(OpenKey)
        CloseKey = staticmethod(CloseKey)
        SetValueEx = staticmethod(SetValueEx)
        QueryValueEx = staticmethod(QueryValueEx)
        DeleteValue = staticmethod(DeleteValue)
        DeleteKey = staticmethod(DeleteKey)
        EnumValue = staticmethod(EnumValue)
        EnumKey = staticmethod(EnumKey)

    _winreg = _ModuleLike()


# For backward compatibility - provide a module-like 'winreg' object
winreg = _winreg

__all__ = [
    "winreg",
    "HKEY_CLASSES_ROOT",
    "HKEY_CURRENT_USER", 
    "HKEY_LOCAL_MACHINE",
    "HKEY_USERS",
    "HKEY_CURRENT_CONFIG",
    "KEY_READ",
    "KEY_WRITE",
    "KEY_ALL_ACCESS",
    "REG_SZ",
    "REG_BINARY",
    "REG_DWORD",
    "REG_MULTI_SZ",
    "REG_QWORD",
    "CreateKeyEx",
    "OpenKey",
    "CloseKey",
    "SetValueEx",
    "QueryValueEx",
    "DeleteValue",
    "DeleteKey",
    "EnumValue",
    "EnumKey",
]
