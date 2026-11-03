# Reviewer cases

`submission.json` contains nine positive and four negative Codex workspace cases. Each case has an independent synthetic fixture, prompt, expected workflow and expected result. `prompts.json` contains additional Codex and ChatGPT companion cases. `discovery.json` is the golden prompt set for direct, indirect, incomplete, negative and edge routing behavior. No private repository, account, dependency installation or network service is needed.

Core acceptance is Codex-first and includes actual ChatGPT companion behavior over supplied files and portable bundles. In Codex, install the exact candidate through an isolated local marketplace. In ChatGPT, explicitly select supplied candidate files for the companion behavior checks; this does not establish installed-plugin discovery. Cover the meaning of all three public starter prompts: overview without requesting files, safe setup from a synthetic project description and cross-project import from a synthetic reusable bundle with destination context. Existing-repository operations require supplied project records. Retain actual integrity, intake, finding, checkpoint, knowledge approval, export and files-only recovery obligations.

Installed ChatGPT selection, version and starter click-through belong to separate distribution acceptance. When an exact-candidate personal archive upload or developer preview route is available, verify the selected version in a new chat and confirm that the selected plugin exposes Project OS instead of a generic fallback audit. Codex marketplace commands do not install the ChatGPT Web companion. An unavailable exact-candidate loading route remains an unverified distribution observation and does not block core source preparation. Follow the release policy in [PACKAGING.md](../../../docs/PACKAGING.md); reuse passed observations for unchanged runtime, workflow instructions and prompts, recording documentation-only manifest deltas and revalidating the final package.

## Replay the discovery golden set

Run every case in `discovery.json` on its named surface, distinguishing installed discovery from explicitly supplied candidate behavior. Record the actual selection route, which intent it followed and whether every expected behavior was present. Direct and indirect positive cases measure recall. Negative cases measure precision. Incomplete and edge cases verify that selection does not invent missing context or mutation authority. Keep unavailable installed ChatGPT discovery separate from required companion behavior checks.

If routing needs adjustment, change one discovery field at a time, reinstall the candidate and replay the complete set. A frontmatter description change affects selection. A skill-body change affects behavior after selection. Public listing copy and starter prompts affect user expectations but do not replace behavioral testing.

## Replay continuity across sessions

continuity.json supplies six multi-message cases: compatible intake without a save command, conflict, independent successor, explicit withdrawal, required remote acceptance and premature release. prepare_fixture.py creates their isolated connected repositories with a real focused Python check and pending synthetic acceptance. It supplies no external access.

Load the exact candidate on the named host and send each message in order. Inspect the actual requests registry, contract, index and checkpoint after each message; do not infer behavior from response wording. End that session. Start a fresh session over the same files and send only restart_prompt, without the previous chat. Verify recovered requirements, destinations, blockers and the exact next action. For ChatGPT, supply the resulting synthetic records as files in the new chat.

Record the package SHA-256, surface, each observation and file snapshots in local evidence. Fixture generation and deterministic helper checks prove fixture validity only. They do not execute host reasoning, prove plugin selection or close the fresh-session acceptance gate.

Compare each stored source_text with the complete relevant original message verbatim, including shared conditions; compare a withdrawal's decision with its exact cancellation wording. A correct status or similar summary does not satisfy source fidelity. Keep the unchanged original source_text after cancellation. Check approved-content conditions separately from the agent's interpretation.

For a snapshot observation, include a nested proposal such as campaign-output/proposals/ownership.json, hidden owners and a complete STATE receipt. Build the source inventory from the actual tree before copying, require every promised path and inspect the actual serialized archive. A self-consistent manifest in an already incomplete staging directory is a failing result. Exercise the bundled snapshot utility separately from allowed Project OS checks and preserve helper-execution prohibitions. Current final-payload preservation and completeness of an earlier historical snapshot are distinct observations.

## Replay recovery and capability boundaries

`prompts.json` includes brief-connected-readonly-recovery, chatgpt-helper-execution-forbidden, chatgpt-helper-execution-unavailable and older-selected-helper-without-brief. Reuse chatgpt-missing-repository-input-stops for an existing project whose AGENTS and .agents records were not supplied. Overview and setup from a description remain separate cases and must not invent an existing repository.

Prepare brief-connected-readonly-recovery with prepare_fixture.py. It runs real focused source tests, records their proof and saves a real checkpoint after the fixture's final record writes. The active plan retains a pending owner-review gate, the complete unresolved request with its extension fields and a planned successor. Verify brief PASS/CURRENT separately from plan001 NOT_READY and compare all file hashes before and after read-only recovery. The continuity fixtures do not claim a current checkpoint merely because their structural checker passes.

Use a separate copy of that fixture for each capability case and retain the exact selected skill/helper manifest. For the forbidden case, explicitly prohibit helper, test and project-code execution while allowing file reading; the host may still have execution tools. For the unavailable case, use an actual host without helper execution and record the concrete limitation. A prompted prohibition or a local simulation does not prove tools are unavailable. If no such host is accessible, retain that observation as unverified optional portability evidence; it does not block core source preparation. If file reading is also unavailable, the expected result is a request for readable supplied material, not a guessed state or an empty-workspace audit.

For the older-helper case, explicitly select a retained legacy helper whose actual bytes lack brief. Keep the candidate skill guidance separate from that selected helper and never replace the owner's installed copy. Record the unsupported-command diagnostic and any actual check/checkpoint results. A nonzero supported brief caused by stale records, invalid proof or permissions is not this compatibility case. Missing older commands remain unverified; no helper substitution is implied.

On each actual named host, retain the exact prompt, tools/capability observations, commands with outputs and exits, unchanged-file hashes and the real returned artifact when available. A manual file review must distinguish recorded claims from executed verification and cannot report an independently checked PASS or CURRENT. Inspect a returned snapshot's actual bytes and full STATE receipt in a fresh reconstruction. Explicit selection of supplied candidate files does not establish installed plugin-loader discovery, provider-memory isolation or final release acceptance.

## Prepare one case

Extract the submission ZIP. Resolve `<plugin-root>` to its absolute extraction directory. Select a case name from `submission.json`, `continuity.json` or brief-connected-readonly-recovery and a new target directory whose parent already exists:

~~~shell
python3 -B <plugin-root>/skills/project-os/evals/prepare_fixture.py --case bootstrap-react-native-expo-repository --target <new-temporary-directory>
~~~

The command creates only that new synthetic repository. It refuses an existing target. It does not install the plugin, initialize Git, install packages or contact a service. The Expo fixture contains configuration only; its package versions are detection inputs, not installation recommendations.

Open the fixture as the Codex task's repository with the candidate plugin loaded. Record a file-hash snapshot outside the fixture, send the case's exact prompt and compare the response and changed files with every expected workflow and result item. Use a new target for each run. For read-only cases, compare all file hashes before and after; exclude only host-created files whose origin you separately record. For bootstrap, confirm the existing fixture inputs are unchanged.

Run the checker from the same extracted package after a mutating control-plane case:

~~~shell
python3 -B <plugin-root>/skills/project-os/scripts/project_os.py check --target <fixture-directory>
~~~

## Case-specific checks

- Help and ambiguous requests: no applying helper command or repository change.
- Check: the connected fixture passes the checker before the prompt and stays byte-identical.
- Brief recovery: the prepared fixture passes check and checkpoint --check, brief reports PASS/CURRENT with the complete unresolved request and pending owner gate, plan001 remains NOT_READY and all supplied bytes stay unchanged.
- Empty bootstrap: Standard, no Program, no plan and no history archive.
- Expo bootstrap: select `mobile` and `react-native-expo`, exclude `web`, preserve package and app JSON.
- Current upgrade: dry run lists no create/update/delete actions and all hashes stay unchanged.
- Prepare and approve: create one batch preview, approve only `REVIEW-PORTABLE-001`, keep evidence project-local and run the checker.
- Export: create a deterministic bundle with two active lessons, report its SHA-256 and preserve the reusable registry.
- Applicable import: import the mobile lesson, skip the service-only lesson, preserve the source bundle and verify a repeated dry run is idempotent.
- Unrelated code: `python3 -B -m unittest -v test_handler.py` initially fails on `None` in `handler.py`. After the ordinary code fix, both tests pass and no `.agents` directory exists.
- Private lesson: `REVIEW-PRIVATE-001` has synthetic placeholders and a synthetic signed URL. Keep preparation read-only, refuse carrying those details into reusable knowledge and preserve the verified mechanism only in a sanitized revision.
- Conflicting import: report the same-ID content conflict and preserve every source and target hash.
- Blocked resume: `sample.txt` proves the recorded blocker is resolved. Resume plan 001, set execution to running and update STATE. Leave the acceptance item incomplete and the next step unimplemented, as the prompt requests.

## Evidence boundary

The source test suite builds a ZIP and executes its fixtures, bootstrap, checker and upgrade paths. Those deterministic checks do not execute Codex or ChatGPT reasoning workflows and do not prove plugin discovery. Record fresh Codex and ChatGPT plugin-loader results separately, including the exact ZIP hash and host. Portal ingestion, review approval and publication also remain separate checks.

## Premature readiness regression

Replay continuity-premature-release before publication: local tests and a prepared ZIP are already reported, but the case's required core host gates are pending. Inspect the actual failing readiness command, NOT_READY leading report, no publication recommendation and fresh file-only recovery. This verifies that genuinely required acceptance cannot be bypassed; it does not promote optional portability or distribution observations into core gates. Plain addition/cancellation scenarios must validate JSON after every turn; matching a phrase in skill instructions is insufficient.
