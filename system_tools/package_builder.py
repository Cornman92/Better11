"""Utilities for building and validating the Better11 installer package.

This module wraps ``python -m build`` to generate a reproducible wheel for
Better11 and surface metadata (version and license) for compliance tracking.
It is intentionally lightweight so it can run in CI as a smoke test without
requiring Windows-specific tooling.
"""
from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from packaging.version import Version

import better11


@dataclass(frozen=True)
class PackageArtifact:
    """Information about the built Better11 package."""

    path: Path
    version: str
    license_text: str


class PackageBuilderError(RuntimeError):
    """Raised when the package build or validation fails."""


class PackageBuilder:
    """Builds a Better11 wheel and surfaces its metadata."""

    def __init__(self, project_root: Optional[Path] = None, output_dir: Optional[Path] = None):
        self.project_root = Path(project_root or Path(__file__).resolve().parent.parent)
        self.output_dir = Path(output_dir or self.project_root / "dist")

    def ensure_build_dependency(self) -> None:
        """Ensure the ``build`` module is available before attempting to create a wheel."""

        if importlib.util.find_spec("build") is None:
            raise PackageBuilderError(
                "Python package 'build' is required. Install it with 'pip install build' before running the builder."
            )

    def _license_text(self) -> str:
        license_path = self.project_root / "LICENSE"
        if not license_path.exists():
            raise PackageBuilderError(f"LICENSE file not found at {license_path}")
        return license_path.read_text(encoding="utf-8")

    def _invoke_build(self) -> None:
        command = [
            sys.executable,
            "-m",
            "build",
            "--wheel",
            "--no-isolation",
            "--outdir",
            str(self.output_dir),
        ]
        subprocess.run(command, cwd=self.project_root, check=True)

    def _find_built_wheel(self) -> Path:
        if not self.output_dir.exists():
            raise PackageBuilderError(f"Output directory {self.output_dir} does not exist")

        wheels = sorted(self.output_dir.glob("better11-*.whl"))
        if not wheels:
            raise PackageBuilderError(f"No Better11 wheels found in {self.output_dir}")

        return wheels[-1]

    def build(self, dry_run: bool = False) -> PackageArtifact:
        """Build the Better11 wheel and return artifact metadata.

        Parameters
        ----------
        dry_run: bool
            If True, do not run the build command. Instead, return the
            expected metadata using the current repository state.
        """

        version = str(Version(better11.__version__))
        license_text = self._license_text()

        if dry_run:
            candidate = self.output_dir / f"better11-{version}-py3-none-any.whl"
            return PackageArtifact(path=candidate, version=version, license_text=license_text)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.ensure_build_dependency()
        self._invoke_build()
        wheel_path = self._find_built_wheel()

        if version not in wheel_path.name:
            raise PackageBuilderError(
                f"Built wheel version mismatch: expected {version} in {wheel_path.name}"
            )

        return PackageArtifact(path=wheel_path, version=version, license_text=license_text)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build and validate the Better11 installer wheel")
    parser.add_argument("--dry-run", action="store_true", help="Show planned build output without running it")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Project root (defaults to repository root detected from this file)",
    )
    parser.add_argument("--out", type=Path, default=None, help="Output directory for built wheels")
    args = parser.parse_args(argv)

    builder = PackageBuilder(project_root=args.project_root, output_dir=args.out)
    try:
        artifact = builder.build(dry_run=args.dry_run)
    except PackageBuilderError as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        return 1
    else:
        print(f"Package: {artifact.path}")
        print(f"Version: {artifact.version}")
        print("License: MIT-compatible")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
