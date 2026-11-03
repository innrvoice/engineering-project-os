# How Project OS works

The plugin supplies instructions and a Python helper. The repository owns its working records. A later Codex task reads and checks those files instead of depending on the old conversation.

<a id="scene-one-resume-tomorrow"></a>

## From a request to the next task

Source changes pass their checks, but a remote migration is pending. Codex saves both facts and the next action. The next task checks that blocker before continuing.

The records have different jobs:

| Record | What it keeps |
| --- | --- |
| Context | Verified facts and commands |
| Checkpoint | Progress, blockers and next action |
| Plan and contract | Outcome and required evidence |
| Requests | Additions, decisions and routing |
| Findings and evidence | Failures and actual check results |
| Knowledge | Confirmed lessons |

`AGENTS.md` routes Codex to relevant files under `.agents/`. Codex reads the records needed for the task. The checkpoint is a compact handoff, separate from the plan.

When helper execution is available and permitted, the read-only `brief` helper gives Codex a compact first view of record integrity, checkpoint freshness and unfinished work at the start of a fresh session or resumed work. Complete open requests stay visible without reloading the historical registries. Codex then reads the context, checkpoint, any active Program contract and active plan with its contract. Original registries remain necessary before edits or when history or errors require them. A successful inspection can still show an active plan that is not ready. See [Reference](REFERENCE.md#interfaces).

<a id="scene-two-track-the-proof-that-is-still-missing"></a>
<a id="readiness-before-delivery"></a>

## Evidence keeps completion honest

Passing local tests cannot satisfy a required remote migration or device check. Codex records what each check established. The helper refuses closure while required recorded conditions or scoped requests remain unresolved.

Evidence hashes detect changed proof. Checkpoint freshness shows that captured records still match. Neither proves the narrative is complete or production works. The agent assesses the actual evidence and reports its limits.

Successful closure saves the completed plan and idle checkpoint together. A following independent plan stays planned without acquiring new permission.

## Preserve a requirement before the conversation forgets it

Codex saves material additions while processing your message. Compatible work joins the current outcome; independent work gets a following plan. Conflicts stay visible until you decide. After compaction, Codex reads unresolved additions alongside the checkpoint.

The agent must do this writeback; there is no background chat recorder. Discussing an option does not automatically make it a work order.

<a id="scene-four-reuse-a-failure-without-importing-the-old-product"></a>

## A lesson can leave the project; its private history does not

A finding starts with an observation and the next check. A confirmed mechanism can become a project lesson with local paths and evidence.

For reuse, Codex preserves the trigger, mechanism, prevention, decisive check and limits while removing private context. You review and approve the proposal. The destination receives the selection, explains skips and preserves conflicting local changes. Repeating the import does not duplicate lessons.

The source stays unchanged. Portable bundles serve another machine or ChatGPT. The publisher receives no lessons and nothing synchronizes automatically. See [Usage](USAGE.md).

<a id="scene-three-coordinate-a-real-multi-phase-migration"></a>
<a id="the-repository-model"></a>

## Use only the structure the work needs

Standard is the normal setup. A bounded repair can stay plan-free while saving findings and a checkpoint. Longer work can have one active plan. Program adds a temporary shared contract for several plans with one sequence and exit condition.

## Installation and repository connection

Directory is the primary [installation channel](https://chatgpt.com/plugins/plugins_6aa793523ba481918ea921c5438d98c9). This guide describes 2.3.0 source; verify the actual channel and installed version separately. Connecting a repository creates or adopts records after a preview. Existing instructions remain authoritative. [Setup](SETUP.md) covers alternatives and upgrades.

## ChatGPT is the companion surface

ChatGPT uses supplied files and bundles, without live repository access from installation. Check actual returned file bytes before applying them. Codex works directly with the repository and its current Git state.

If ChatGPT can read the files but cannot run the helper, it can explain the recorded state while leaving integrity and freshness unverified. It preserves the files and pending acceptance, reports the missing execution and does not invent successful checks or a validated download. A user prohibition on execution follows the same read-only route. An older selected helper uses its supported checks without being silently replaced. See the capability routes in [Reference](REFERENCE.md#interfaces).

Generic file tools may still produce a transport copy with matching bytes and hashes. That is useful for moving the records, but it does not prove Project OS validation ran. A supplied skill copy and a working returned ZIP also do not prove that an installed plugin was discovered or that account Memory was isolated.

<a id="what-the-helper-can-and-cannot-do"></a>

## Safety boundary

The helper runs when invoked and initiates no network request. Project OS grants no new authority for application changes, Git operations or publication. Exact commands, ownership and file-safety guarantees belong in the [advanced Reference](REFERENCE.md).
