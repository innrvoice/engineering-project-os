# Persistence acceptance before packaging

Run [persistence.json](persistence.json) against the exact frozen candidate skill before building a release ZIP. These repository-level cases supplement the bundled discovery, submission and continuity cases under `skills/project-os/evals/`. The files here describe acceptance procedures; their presence does not prove a host pass and they are not part of the plugin package allowlist.

Use isolated synthetic repositories and actual Codex and ChatGPT sessions. Record the candidate file manifest, helper SHA-256, host, commands, responses and resulting file snapshots. A locally installed older release or a fresh session given the old conversation does not evaluate the candidate or files-only recovery.

Required companion acceptance covers actual supplied-file behavior and the basic overview, setup, missing-input and knowledge boundaries. Installed ChatGPT loading, selected-version and starter click-through checks are distribution acceptance; a genuinely execution-free host and account Memory isolation are separate portability observations. Keep missing optional observations unverified without blocking core source preparation. Follow [release packaging](../docs/PACKAGING.md) and reuse passed observations when runtime, workflow instructions and prompts are unchanged; documentation-only updates require an explicit manifest delta and final artifact revalidation.

The first ordinary repair case starts with the user's own defect report. The finding must still be persisted: the agent did not need to discover the symptom itself. The second case starts with a bounded contract review and requires a reproduced mismatch before a confirmed finding. Neither user prompt asks to invoke Project OS or to save a finding. Existing repository guidance supplies the workflow.

The knowledge case requires two separate messages. Review must remain read-only with respect to reusable knowledge until approval. After the selected import, inspect the real registry and the real checkpoint. An imported lesson with scaffold STATE is a failure even if the helper's structural check passes.

After each initial session ends, start a separate session containing only its actual resulting files. For a supplied-material companion, verify each path and file hash before reconstruction and preserve the exact recovered bytes. The restart message must not reveal the previous result, expected finding ID or imported selection beyond what the supplied records contain. Compare every file hash before and after the read-only recovery.

The required terminal observations are:

- Focused behavior checks have actual recorded results and target boundaries.
- The stable finding ID and evidence hashes survive the ordinary repair and files-only recovery.
- `checkpoint --target <repository> --check --json` returns `CURRENT` after the meaningful operation and in the recovery session.
- `check --target <repository>` passes without treating structural consistency as proof of behavioral acceptance.
- The imported selection, excluded entries, recorded approval provenance, source preservation and exact next action match actual files.

Preserve failed attempts and their snapshots. Rerun affected cases whenever candidate workflow instructions or runtime bytes change. An unaccepted inspection/test ZIP may be built to test candidate bytes. Before release acceptance, require actual fresh-session persistence and recovery and compare the final package manifest against the tested frozen manifest, accounting explicitly for documentation-only deltas. Missing required core evidence or a failed required case keeps the release outcome open; optional portability and later distribution observations retain their own unverified status.
