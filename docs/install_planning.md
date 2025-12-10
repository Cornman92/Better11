# Installation Planning & Cached Download Design

## Overview
The Better11 installer manager now supports a *planning* phase and a *verified download cache*. The planning phase simulates an install without mutating system state and provides a deterministic dependency order. The download cache feature prevents redundant network transfers by reusing installers whose checksums already match the catalog.

This document dives into the data structures, algorithms, and user experience expected from both features. It supplements `plan.md` and should be kept current alongside implementation changes.

## Planning Data Model
- `InstallPlanStep`
  - `app_id`, `name`, `version` pulled from the catalog entry.
  - `installed`: whether `InstallationStateStore` reports the app as currently installed with the catalog's version.
  - `action`: one of `"skip"` (already installed) or `"install"`.
  - `dependencies`: IDs of immediate dependencies so the CLI/GUI can render extra context without re-parsing the catalog.
  - `notes`: free-form string describing warnings (missing dependency, circular reference, etc.).
- `InstallPlanSummary`
  - `target_app_id`
  - ordered list of `InstallPlanStep` sorted leaf-to-root, representing the actual install order the manager will follow.
  - `warnings`: collection of strings produced during DFS (missing entries, attempted cycles, cached state mismatches, etc.).

## Planning Algorithm
1. **DFS Traversal**: AppManager walks dependencies depth-first, pushing steps onto a stack once all children are processed. The resulting stack reversed is the topological order.
2. **Cycle Detection**: Maintain `visited` and `in_stack` sets. When encountering a node already in `in_stack`, append a warning instead of raising `DependencyError`; the plan marks the offending step with `notes="Cycle detected"`.
3. **Missing Dependencies**: When a dependency ID is not found in the catalog, emit a warning, mark the step with `action="blocked"`, and continue (so the CLI can report the failure without crashing).
4. **State Inspection**: Each step inspects `InstallationStateStore` to see if the catalog version is already installed. If so, mark `installed=True` and `action="skip"`.
5. **Output Formatting**: Consumers (CLI/GUI) use the ordered steps and warnings to render human-friendly summaries. Planning never mutates persistent state.

## CLI/GUI Experience
- New CLI command: `python -m better11.cli plan <app_id>`
  - Prints a table with columns `ACTION`, `APP ID`, `VERSION`, `STATUS`, `NOTES`.
  - Lists warnings after the table if present.
- GUI footer update: after an install finishes, the footer mentions which plan step completed (e.g., `Installed demo-appx (included demo-msi, demo-exe)`). GUI does not expose the full table but shows the aggregated sequence.

## Verified Download Cache
- **Cache hit**: before downloading, `AppManager` checks whether `_destination_for(app)` exists. If yes, run `DownloadVerifier.verify_hash`. Successful verification marks a cache hit and returns the cached path.
- **Cache miss**: continue with the existing download flow.
- **Corruption handling**: on hash mismatch, delete the stale file and force a fresh download. Log the event so operators can inspect repeated corruption.
- **Observability**: CLI prints `Using cached installer ...` vs `Downloading ...`. GUI footer replicates the message.

## Testing Strategy
- `tests/test_manager.py`
  - new tests for planning success, missing dependency warning, cycle warning (use small synthetic catalog fixtures or monkeypatch `AppManager.catalog`).
  - tests for cache: pre-create matching/mismatching files under the download directory, validate behavior.
- `tests/test_application_manager.py`
  - unaffected, but ensure download cache changes do not break existing semantics.
- Additional CLI test verifying `plan` command output is non-empty for known app IDs (use `capsys`).

## Operational Guidance
- Keep `plan.md` updated when expanding the planning or caching behavior.
- Encourage users to run `plan` before `install` on production systems.
- Cached installers should be periodically cleaned via existing OS tooling when disk space is scarce (`~/.better11/downloads`).
