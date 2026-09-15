# How Project OS works

I built Project OS after repeating the same recovery ritual too many times. The repository still had the code, but the next conversation did not know which decision was current, which check had actually passed or which "done" item still depended on a deployment or a person.

The usual answer was to reconstruct everything from chat history. That worked until the history became long, the task crossed several sessions or one apparently successful check turned out to prove less than I remembered.

Project OS is for developers who want AI-assisted engineering work to survive that boundary. It solves the problem with a reusable plugin, one visible repository contract and ordinary files. The bundled skill knows how to create and maintain the system. The repository files keep the working truth after a conversation ends.

The immediate benefit is continuity. Decisions, checkpoints, plans and evidence stay with the code. The longer-term benefit is compounding knowledge: a confirmed failure can become a lesson that the same repository remembers and, after deliberate sanitization and review, another repository can reuse.

That second benefit matters more than it first appears. After spending weeks learning which failure mechanism was real, repeating the same investigation in the next project feels less like engineering and more like paying an avoidable tax. Project OS cannot make every lesson universal, but it can help you carry the useful ones forward without carrying the old product with them.

ChatGPT and Codex can use the same plugin from the Universal Plugin Directory. They do not receive repository context in the same way. ChatGPT works with the project description and files supplied in the chat. Codex works with the local workspace selected for the task. Installing the plugin alone grants neither surface automatic access to a repository.

## Selecting Project OS

In ChatGPT, `@Engineering Project OS` selects the plugin for the current message. In Codex, `$project-os` selects its bundled skill. Neither form is shell syntax, an environment variable, a Python command or a mode that stays enabled.

The overview is the simplest first request. It explains the product, its benefits and the next useful workflow without inspecting a repository or asking for files.

**Type this in ChatGPT:**

~~~text
@Engineering Project OS Tell me what Project OS does, how it works and when I should use it.
~~~

**Type this in Codex chat:**

~~~text
$project-os overview
~~~

**Type this in ChatGPT after describing the project:**

~~~text
@Engineering Project OS Help me set up Project OS for this project and start with a safe preview.
~~~

**Type this in Codex chat with the repository open:**

~~~text
$project-os bootstrap
~~~

- Result: the selected surface inspects the available project context and prepares a safe Standard setup preview.
- Files: none change until the user approves the proposed setup. ChatGPT returns artifacts while Codex can apply the reviewed helper operation in its open workspace.
- Proof: the response explains the selected packs and overlays, shows the affected files and keeps every unsupported claim unverified.
- Skip it when: the repository already has Project OS; use `check` instead.

The words after the skill name are normal language. Project OS publishes short requests because they are easy to remember, not because it implements a command parser.

| Codex message | Interpretation |
| --- | --- |
| `$project-os overview` | Explain who Project OS is for, what it provides and what to do next without reading or changing a repository |
| `$project-os check` | Validate the current control plane without writing |
| `$project-os check only plan state` | Run the same check with extra focus |
| `$project-os проверь систему и ничего не меняй` | Read-only check expressed in Russian |
| `$project-os program status` | Report Program and current Project OS state |
| `$project-os make this better` | Ambiguous: explain choices or ask before any write |
| `$project-os fix the null check in the handler` | Ordinary code task: do not create Project OS records merely because the prefix is present |

Case, punctuation and explanatory sentences may vary. A clear user constraint such as `do not change files` always keeps the request read-only. A variant is accepted when its intent is clear. An ambiguous mutation is not guessed.

`$project-os overview` and `$project-os help` are both read-only, but they serve different readers. Overview explains the product and recommends a next step. Help returns every supported short request with its purpose, required argument and examples, then distinguishes those chat requests from Terminal helper commands.

The package allows implicit invocation so the selected plugin can expose its skill when a request clearly concerns Project OS. Explicit `@Engineering Project OS` or `$project-os` invocation remains the clearest route. Unrelated work must not create Project OS records merely because the plugin is installed.

## What each surface loads

The plugin bundles one Project OS skill. When a surface selects it, the skill routes to the focused bootstrap, maintenance or knowledge reference needed for the operation.

ChatGPT can give setup advice or prepare a starter package from a project description, selected files or a repository snapshot. Claims about an existing setup require its actual files. If that evidence is missing, ChatGPT must ask for the relevant files. It must not inspect an empty host workspace, claim the skill is unavailable and continue with a generic repository audit.

Codex can inspect the local workspace selected for the task. It also discovers applicable `AGENTS.md` files when the task starts. A root file can define project authority, working method and routes to durable Project OS records. Instructions closer to the working directory can refine broader ones.

| Situation | Initial route | What happens next |
| --- | --- | --- |
| ChatGPT Project OS request | `@Engineering Project OS`, then a project description or relevant files | ChatGPT advises from the supplied context or works against the supplied copies |
| Codex Project OS request | `$project-os`, then the installed skill | Codex follows the requested control-plane workflow in the selected workspace |
| Ordinary repository request | Applicable `AGENTS.md` files | Codex reads only the state, plan, packs and knowledge relevant to the work |
| Direct helper use | Python command in Terminal | The helper performs only its deterministic operation |

The `.agents` directory is not a hidden database and is not loaded all at once for every message. Its files matter because `AGENTS.md` routes Codex to them and each file owns a specific kind of truth.

## Installation and repository connection are different

Installing the Directory plugin makes the reusable workflow available to ChatGPT and Codex. Installing the standalone alternative makes the skill available in Codex only. Neither installation touches a repository.

Providing or connecting repository context is a separate action. In ChatGPT, describe the project or attach the relevant files. A complete ZIP is optional and useful only when the whole tree matters. In Codex, open the local repository as the task workspace. Bootstrap creates a new Standard control plane and adoption maps compatible records already present. Both inspect first, preview changes and use the helper for deterministic structure.

After a new `AGENTS.md` is created or changed, apply the file to the real repository and start a fresh chat or task. In Codex, open that repository so the new startup instruction route can load. The already running conversation is not proof that the new route works.

Installing the skill is not connecting a repository. Connecting a repository is not opening a plan. Opening a plan is not starting a Program.

## Standard and Program

### Standard

Standard is the normal, complete state of a connected repository. It includes routing, context, checkpoint state, just-in-time plans, findings, evidence, knowledge, capability packs and overlays.

Bootstrap always creates Standard. Standard can support a long task and many sequential plans. A repository does not need a Program merely because work spans several Codex tasks.

### Program

Program is a temporary coordination layer above plans. Use it when one initiative has multiple distinct phases or outcomes that need one shared contract.

A useful distinction:

| Work | Use |
| --- | --- |
| Fix one API pagination failure | Standard, usually without a plan |
| Implement one resumable authentication change | Standard plus one plan |
| Migrate authentication across API, workers, web and mobile through separate rollout phases | Program plus separate plans as needed |
| Maintain a repository for years | Standard, not one permanent Program |

A Program contract owns:

- the initiative name and observable outcome;
- explicit authority;
- at least two phases, each with an outcome and exit conditions;
- evidence requirements;
- cost boundaries;
- exclusions;
- overall exit conditions.

Nothing creates `PROGRAM.md` during bootstrap, adoption or ordinary work.

**Type this in Codex chat:**

~~~text
$project-os program start: migrate authentication across the API, workers, web and mobile without downtime
~~~

Codex inspects repository truth and prepares a complete definition. If material fields cannot be verified or derived, it asks for the missing decision and does not write. Once the definition is complete, the helper dry-runs the transition, Codex reviews it, the helper creates `.agents/PROGRAM.md`, `SYSTEM.mode` becomes `program` and the checker runs.

Starting a Program does not create or activate a plan. Plans remain outcome-sized execution packages inside the wider initiative.

**Type this in Codex chat:**

~~~text
$project-os program status
~~~

This is read-only. It reports the Program contract, current phase, related plan state and unresolved exit conditions from repository evidence.

A Program can close only when no plan is active.

**Type this in Codex chat:**

~~~text
$project-os program close completed
~~~

Use `completed` only when the Program's exit evidence exists. Use `$project-os program close stopped: <reason>` when the initiative is deliberately discontinued.

Closing preserves the exact Program contract under `.agents/history/programs/<program-id>/PROGRAM.md`, records its disposition and SHA-256 digest in `.agents/history/index.json`, removes the active `.agents/PROGRAM.md` and returns `SYSTEM.mode` to `standard`. The first closure also creates `.agents/history/README.md`.

Whether evidence actually proves the Program outcome is a user and Codex judgment. The helper checks the structural lifecycle and refuses closure while a plan is active; it cannot verify the meaning of product, deployment or external evidence.

## What the records own

- `AGENTS.md` owns startup routing, authority and working rules.
- `.agents/SYSTEM.json` owns release, schema, mode, active Program identity, path mappings, selected capabilities and managed guidance baselines.
- `.agents/CONTEXT.md` owns durable verified facts and exact commands.
- `.agents/STATE.md` owns the current checkpoint and exact next action.
- `.agents/plans/` owns resumable outcome packages and execution status.
- `.agents/findings/` owns concrete defects, candidates and accepted risks.
- `.agents/evidence/` stores sanitized proof referenced by an owning record.
- `.agents/knowledge/project/` owns confirmed repository-specific lessons.
- `.agents/knowledge/reusable/` owns sanitized, reviewed and user-controlled portable failure mechanisms.
- `.agents/packs/` contains managed capability and ecosystem guidance.
- `.agents/PROGRAM.md` exists only while one Program is active.
- `.agents/history/` contains the Program history index and closed snapshots when they exist.

Do not duplicate one status in several files. `STATE.md` is a handoff, not a diary. `CONTEXT.md` is not an active task list.

## How failure knowledge becomes reusable

This is the part of Project OS that is easiest to underestimate. Context and plans help the next session continue. Failure knowledge can help the next project avoid paying for the same lesson again.

Imagine one project has spent two months collecting confirmed failures around React Native lifecycle, image handling and native handoffs. A new project starts. It should not inherit the first product's paths, names or history, but throwing away every mechanism would be absurd. The useful unit is a sanitized lesson with a trigger, mechanism, prevention, verification and honest boundaries.

The lifecycle is deliberate:

1. A finding records the observed failure, its impact, current evidence and the next decisive check without pretending that a hypothesis is already a cause.
2. After the mechanism is confirmed, `knowledge capture` creates project knowledge with applicability, trigger, mechanism, prevention, decisive verification and scope boundaries.
3. `knowledge prepare: all` creates a read-only batch proposal and removes project names, credentials, personal data, private paths, every URL, deployment identifiers, evidence paths and copied product history.
4. A person reviews the batch and approves only lessons that remain safe, accurate and useful. The approved entries become the user's reusable library inside that repository.
5. Codex can read that reusable library directly from the old repository. ChatGPT or a different machine can use a deterministic JSON bundle exported by the user.
6. The destination previews which active lessons match its capabilities and ecosystem, considers lifecycle tombstones independently of applicability, explains every skipped entry and imports only after confirmation.

`failure -> finding -> confirmed project lesson -> sanitized batch -> human approval -> user-owned reusable library -> explicit import into another project`

No Project OS release sits in that path. No author reviews your lessons and no central database receives them. The source repository does not change during import. The destination receives the reusable mechanism, not the old project's identity or evidence.

The first repository records the lesson. The next repository does not need to repeat the failure. At least not that particular failure. Software will kindly invent new ones.

This is reusable knowledge without hidden sharing. Every write stays visible, target-local changes win over incoming content and repeated imports are idempotent.

## What the helper does

The helper provides deterministic operations:

- `detect` inspects stack and capability signals.
- `init` creates a Standard control plane.
- `adopt` validates and maps compatible existing owners.
- `check` validates paths, registries, state invariants, archive hashes, managed guidance baselines and version alignment.
- `knowledge list`, `approve`, `export`, `import`, `revise`, `retire` and `remove` manage the user's reusable library through deterministic previews and conflict checks.
- `sync-knowledge` is a read-only compatibility notice that directs older workflows to `knowledge import`.
- `upgrade` conflict-checks and migrates supported repository state to the installed release, rolling back completed changes when a caught write or final-validation failure occurs.
- `program start`, `program status` and `program close` manage the Program lifecycle.

The helper does not infer product requirements, invent authority, write a real implementation plan, confirm a finding or turn a source check into production evidence. Codex and the user make those judgments from current evidence.

### The mutation sequence

A clear mutating short request causes Codex to:

1. Inspect Git state, applicable instructions and the current Project OS records.
2. Prepare the intended operation and run the helper with `--dry-run` when available.
3. Review every proposed write and stop on ambiguity, stale state or conflict.
4. Apply the same clean operation.
5. Run `check` and report the diff and remaining unverified boundaries.

For plan, finding or knowledge edits that are reasoned record updates rather than a dedicated helper subcommand, Codex still prepares and validates the intended record change before writing, then runs the checker.

## What tamper-evident history means

The Program archive is ordinary repository content. On close, the helper copies the exact `PROGRAM.md` bytes and records their SHA-256 digest. The checker recomputes that digest and requires every indexed archive path to exist.

This catches an uncoordinated edit, deletion or substitution. It does not make a file technically immutable, prevent a person from rewriting both the file and its index, provide a cryptographic signature or replace Git hosting controls. Git remains the review and distribution mechanism.

History is available to Standard and Program states. It is created when the first Program closes or when compatible indexed history is adopted. Starting the first Program creates no empty history scaffold. Archived snapshots never become current authority.

## What is not running in the background

Project OS has no:

- daemon or watcher;
- MCP server or remote service;
- lifecycle hook;
- hidden database;
- automatic upload;
- automatic Git operation;
- automatic cross-project synchronization;
- a publisher-managed failure database.

No repository learns from another repository by itself. Local additions and conflicts remain visible for review.

## Versions and upgrades

The installed helper defines the Project OS release version. Release 2.1.0 uses `SYSTEM.schema_version: 4` and `SYSTEM.mode: standard|program`. Knowledge registries and portable bundles have their own schema version.

Updating the Directory plugin or standalone skill does not update repositories. `$project-os upgrade` inspects the old state, previews every managed file change, preserves project-owned records, migrates proven user-owned lessons into the reusable library, removes old release-managed seeds, aborts on conflicts, applies only a clean preview with caught-failure rollback and runs the checker. In ChatGPT, the same workflow operates on supplied file copies and returns artifacts that still need deliberate application to the repository.

When developing Project OS itself, the installed stable skill governs the workflow while the candidate helper is developed and tested from the source checkout. Do not replace the installed skill with a mutable candidate. Install only a published versioned tag, then start a fresh Codex task.

## Authority and safety

Project OS narrows where engineering state lives. It does not broaden what ChatGPT or Codex may do. Application edits, dependency installation, deletion, Git operations, deployment, publication and external communication still require user authority and must follow repository instructions.

A passing Project OS checker proves structural consistency. It does not prove application correctness, artifact identity, deployment state, production behavior or manual and physical acceptance.

For the shared plugin catalog and product-specific invocation, see OpenAI's [plugin documentation](https://learn.chatgpt.com/docs/plugins). For Codex behavior outside this project, see OpenAI's documentation for [skills](https://learn.chatgpt.com/docs/build-skills) and [`AGENTS.md`](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

## Next

- [Install or connect a repository](SETUP.md)
- [Use Project OS day to day](USAGE.md)
- [Read the technical reference](REFERENCE.md)
