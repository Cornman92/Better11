from __future__ import annotations

from pathlib import Path

import better11
import pytest
from _pytest.monkeypatch import MonkeyPatch
from packaging.version import Version

from system_tools.package_builder import PackageArtifact, PackageBuilder, PackageBuilderError


@pytest.fixture
def builder(tmp_path: Path) -> PackageBuilder:
    return PackageBuilder(project_root=Path(__file__).resolve().parents[1], output_dir=tmp_path)


def test_dry_run_reports_expected_metadata(builder: PackageBuilder) -> None:
    artifact = builder.build(dry_run=True)

    assert isinstance(artifact, PackageArtifact)
    assert artifact.version == str(Version(better11.__version__))
    assert artifact.path.name.endswith(".whl")
    assert "MIT License" in artifact.license_text


def test_build_checks_for_dependency(builder: PackageBuilder, monkeypatch: MonkeyPatch) -> None:
    import importlib.util as util

    monkeypatch.setattr(util, "find_spec", lambda _: None)

    with pytest.raises(PackageBuilderError):
        builder.ensure_build_dependency()


def test_build_uses_existing_wheel(builder: PackageBuilder, monkeypatch: MonkeyPatch) -> None:
    version = str(Version(better11.__version__))
    fake_wheel = builder.output_dir / f"better11-{version}-py3-none-any.whl"
    fake_wheel.parent.mkdir(parents=True, exist_ok=True)
    fake_wheel.write_text("content")

    invoked = {"count": 0}

    def _counting_build() -> None:
        invoked["count"] += 1

    monkeypatch.setattr(builder, "ensure_build_dependency", lambda: None)
    monkeypatch.setattr(builder, "_invoke_build", _counting_build)
    artifact = builder.build()

    assert invoked["count"] == 1
    assert artifact.path == fake_wheel
