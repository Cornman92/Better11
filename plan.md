# Better11 Enhancements Plan

## Objectives
- Provide operators a safe way to preview dependency trees, installation order, and current system state before executing potentially destructive actions.
- Reduce redundant network usage by reusing verified installers already present in the download cache.
- Document the new behavior so CLI and GUI users understand how to use installation planning and cached downloads.

## Scope & Deliverables
1. **Installation Planning API and CLI command**
   - Introduce planning data structures (e.g., `InstallPlanStep`, `InstallPlanSummary`) describing dependency ordering, whether each dependency is already satisfied, and any blockers (missing catalog entry, circular dependency, etc.).
   - Extend `AppManager` with `build_install_plan(app_id: str)` that performs a DFS without mutating state. It must:
     - Detect circular dependencies and surface human-readable diagnostics instead of raising the generic `DependencyError`.
     - Flag dependencies not present in the catalog.
     - Annotate whether each dependency is already installed and its currently installed version.
     - Provide a topologically sorted order that mirrors the actual install sequence (`leaf → root`).
   - Add a new CLI subcommand `plan <app_id>` that renders a readable table/summary of the plan, highlighting which steps are skipped because they are already installed, which require installation, and any warnings collected during planning.
   - Update GUI status footer messaging to leverage the new plan summary when an install completes (so the user knows which dependency triggered the action).

2. **Verified Download Cache**
   - Add optional reuse of cached installers to `AppManager.download`. Before downloading, check whether the expected destination file already exists. If so, run the `DownloadVerifier.verify_hash` to confirm integrity; when the hash matches, reuse the cached file and skip the network transfer.
   - Log (CLI + GUI) when cache hits occur vs. when a fresh download is required.
   - Ensure stale or corrupted cached files are overwritten: on hash mismatch, delete the bad file before downloading again.

3. **Documentation & Testing**
   - Create supporting documentation (`docs/install_planning.md`) describing the planning algorithm, CLI usage examples, and cache behavior.
   - Expand automated tests:
     - Unit tests for `AppManager.build_install_plan` covering happy path, already-installed dependencies, missing dependency, and cycle detection messaging.
     - Tests for the cache path ensuring `DownloadVerifier` is invoked and that corrupted caches trigger redownloads.
     - CLI-level smoke test verifying the `plan` command prints plan data (stub via capturing stdout).

## Implementation Steps
1. Author supporting design/usage documentation to align stakeholders before coding.
2. Implement planning data classes and AppManager logic (manager module + state store helper queries).
3. Wire the planning API into the CLI (`plan` command) and GUI status reporting.
4. Enhance download caching in `AppManager.download` with verifier integration.
5. Add/adjust tests in `tests/test_manager.py` (and new files if necessary) plus CLI test.
6. Run the full test suite (`pytest`).
7. Update README snippets if CLI usage changes materially.

## Non-Goals
- Modifying the JSON catalog schema.
- Building a GUI visualization for the entire dependency tree (only textual summary).
- Refactoring download/storage paths beyond the cache verification work described above.
