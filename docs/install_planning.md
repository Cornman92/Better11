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

### Sample CLI Output

Basic plan for an application with dependencies:

```bash
$ python -m better11.cli plan visual-studio-code
ACTION    APP ID              VERSION    STATUS       NOTES
------    ----------------    -------    ----------   -----
SKIP      dotnet-runtime      6.0.0      installed
INSTALL   vs-code-deps        1.2.0      pending
INSTALL   visual-studio-code  1.85.0     pending
```

Plan with warnings (circular dependency):

```bash
$ python -m better11.cli plan app-with-cycle
ACTION    APP ID         VERSION    STATUS     NOTES
------    ----------     -------    --------   --------------------------
BLOCKED   dep-a          1.0.0      pending    Cycle detected
BLOCKED   dep-b          1.0.0      pending    Cycle detected
BLOCKED   app-with-cycle 1.0.0      pending    Depends on blocked dependency: dep-a

Warnings:
- Circular dependency detected: dep-a -> dep-b -> dep-a
```

Plan with missing dependency:

```bash
$ python -m better11.cli plan app-with-missing-dep
ACTION    APP ID              VERSION    STATUS     NOTES
------    -----------------   -------    --------   ------------------------
BLOCKED   (missing)           unknown    pending    Missing from catalog
BLOCKED   app-with-missing-dep 1.0.0     pending    Depends on blocked dependency: unknown-dep

Warnings:
- Missing catalog entry for dependency 'unknown-dep'
```

### GUI Integration
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

## Programmatic Usage

```python
from pathlib import Path
from better11.apps.manager import AppManager

# Initialize manager
catalog_path = Path("better11/apps/catalog.json")
manager = AppManager(catalog_path)

# Build plan
plan = manager.build_install_plan("my-app")

# Check for issues
if plan.warnings:
    for warning in plan.warnings:
        print(f"Warning: {warning}")

# Inspect steps
for step in plan.steps:
    print(f"{step.action}: {step.app_id} v{step.version}")
    if step.notes:
        print(f"  Note: {step.notes}")

# Check if installation would succeed
blocked = any(step.action == "blocked" for step in plan.steps)
if blocked:
    print("Installation cannot proceed due to blocked dependencies")
```

## Security Considerations

### Hash Verification
All cached installers undergo SHA-256 hash verification before reuse. This ensures:
- **Integrity**: The file hasn't been corrupted
- **Authenticity**: The file matches the catalog specification
- **Protection**: Prevents using tampered or modified installers

### No State Mutation
The planning operation is read-only and never:
- Downloads files
- Modifies the installation state
- Executes installers
- Changes system configuration

This makes `plan` safe to execute at any time without side effects.

## Operational Guidance
- Keep `plan.md` updated when expanding the planning or caching behavior.
- Encourage users to run `plan` before `install` on production systems.
- Cached installers should be periodically cleaned via existing OS tooling when disk space is scarce (`~/.better11/downloads`).

## Benefits

### 1. Transparency
Operators can see exactly what will be installed before committing to the operation.

### 2. Resource Planning
Understanding the full dependency tree helps with:
- Estimating disk space requirements
- Planning network bandwidth usage
- Scheduling maintenance windows

### 3. Troubleshooting
Clear diagnostic messages for:
- Circular dependencies with exact paths
- Missing catalog entries
- Version conflicts

### 4. Efficiency
Download cache reuse eliminates redundant network transfers, particularly useful when:
- Re-installing applications
- Installing multiple apps with shared dependencies
- Testing installation procedures
