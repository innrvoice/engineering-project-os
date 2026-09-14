# Reviewer cases

`submission.json` contains six positive and three negative Codex workspace cases. Each case has an independent synthetic fixture, prompt, expected workflow and expected result. `prompts.json` contains additional ChatGPT and Codex behavioral cases. No private repository, account, dependency installation or network service is needed.

The three public starter prompts also require a fresh ChatGPT check. Install the exact candidate ZIP through the local marketplace, start a new chat, attach a synthetic repository archive and run inspect, bootstrap preview and validation. Confirm that the selected plugin exposes Project OS instead of a generic fallback audit. In a separate new chat, run a repository-dependent starter prompt without attaching files and confirm that Project OS asks for them without inspecting an empty host workspace.

## Prepare one case

Extract the submission ZIP. Resolve `<plugin-root>` to its absolute extraction directory. Select a case name from `submission.json` and a new target directory whose parent already exists:

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
- Empty bootstrap: Standard, no Program, no plan and no history archive.
- Expo bootstrap: select `mobile` and `react-native-expo`, exclude `web`, preserve package and app JSON.
- Current upgrade: dry run lists no create/update/delete actions and all hashes stay unchanged.
- Unrelated code: `python3 -B -m unittest -v test_handler.py` initially fails on `None` in `handler.py`. After the ordinary code fix, both tests pass and no `.agents` directory exists.
- Private lesson: `REVIEW-PRIVATE-001` has synthetic placeholders and a synthetic signed URL. Keep the proposal read-only, refuse carrying those details into shared knowledge and preserve the verified mechanism only in a sanitized draft.
- Blocked resume: `sample.txt` proves the recorded blocker is resolved. Resume plan 001, set execution to running and update STATE. Leave the acceptance item incomplete and the next step unimplemented, as the prompt requests.

## Evidence boundary

The source test suite builds a ZIP and executes its fixtures, bootstrap, checker and upgrade paths. Those deterministic checks do not execute ChatGPT or Codex reasoning workflows and do not prove plugin discovery. Record fresh ChatGPT and Codex plugin-loader results separately, including the exact ZIP hash and host. Portal ingestion, review approval and publication also remain separate checks.
