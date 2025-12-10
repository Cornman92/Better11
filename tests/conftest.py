from __future__ import annotations

import json
import sys
import pathlib
from pathlib import Path
from typing import Callable, Iterable, Mapping

try:
    import _pytest.nodes as _pytest_nodes

    # Force pytest internals to use PosixPath semantics even if upstream tests
    # monkeypatch `os.name` to simulate Windows environments. This prevents
    # `WindowsPath` from being instantiated on non-Windows hosts, which causes
    # `NotImplementedError` during error reporting.
    _pytest_nodes.Path = pathlib.PosixPath  # type: ignore[attr-defined]
except Exception:
    # If pytest internals change, fallback gracefully without breaking tests.
    pass

# Prevent accidental promotion to WindowsPath on POSIX hosts. Some libraries
# instantiate ``WindowsPath`` when simulating Windows behavior; remapping it to
# ``PosixPath`` keeps path handling compatible in this environment.
pathlib.WindowsPath = pathlib.PosixPath  # type: ignore[attr-defined]

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
root_path = str(REPO_ROOT)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

DEFAULT_CATALOG = REPO_ROOT / "better11" / "apps" / "catalog.json"
SAMPLES_DIR = REPO_ROOT / "better11" / "apps" / "samples"


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def samples_dir() -> Path:
    return SAMPLES_DIR


@pytest.fixture
def default_catalog_path() -> Path:
    return DEFAULT_CATALOG


@pytest.fixture
def manager_factory(tmp_path: Path):
    from better11.apps.manager import AppManager
    from better11.apps.runner import InstallerRunner

    def factory(**overrides):
        catalog_path: Path = overrides.get("catalog_path", DEFAULT_CATALOG)
        download_dir: Path = overrides.get("download_dir", tmp_path / "downloads")
        state_file: Path = overrides.get("state_file", tmp_path / "state.json")
        runner = overrides.get("runner", InstallerRunner(dry_run=True))
        downloader = overrides.get("downloader")
        verifier = overrides.get("verifier")
        return AppManager(
            catalog_path=catalog_path,
            download_dir=download_dir,
            state_file=state_file,
            runner=runner,
            downloader=downloader,
            verifier=verifier,
        )

    return factory


@pytest.fixture
def catalog_writer(tmp_path: Path) -> Callable[[Iterable[Mapping[str, object]]], Path]:
    def _write(entries: Iterable[Mapping[str, object]]) -> Path:
        catalog_path = tmp_path / "catalog.json"
        with catalog_path.open("w", encoding="utf-8") as handle:
            json.dump({"applications": list(entries)}, handle, indent=2)
        return catalog_path

    return _write


@pytest.fixture
def make_installer(tmp_path: Path) -> Callable[[str, bytes | str], Path]:
    def _make(filename: str, contents: bytes | str = b"payload") -> Path:
        path = tmp_path / filename
        data = contents if isinstance(contents, bytes) else contents.encode("utf-8")
        path.write_bytes(data)
        return path

    return _make
