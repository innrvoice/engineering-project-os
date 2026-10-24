<img src="assets/logo.svg" width="96" height="96" alt="Engineering Project OS logo">

# Engineering Project OS

**Built for Codex.**

Resume engineering work with durable state and reusable failure knowledge.

<a id="legacy-directory"></a>

[Install Engineering Project OS from the Directory](https://chatgpt.com/plugins/plugins_6aa793523ba481918ea921c5438d98c9)

Project OS 2.2.4 is available in the Universal Plugin Directory, the primary installation route. GitHub marketplace and standalone Codex installations are [alternatives](docs/SETUP.md).

The problem usually appears after the first productive session. Codex has explored the repository, ruled out two plausible causes, made a decision and found one check that passes. Then the task ends.

Tomorrow the code is still there, but the working state is not. Which decision was current? Which failure was confirmed? Did green CI prove the change worked or did the result still need a physical device, deployment or human check? A long chat may contain the answer, but chat history is a poor project database.

Project OS keeps that working state in visible repository files. Codex can resume from the current plan, checkpoint, findings and evidence instead of reconstructing them from conversation fragments.

## What it gives a developer

- **Continue without retelling the project.** Keep progress and the next action.
- **Keep additions during work.** Corrections survive context compaction.
- **See what "done" still needs.** Separate passing tests from production acceptance.
- **Carry useful lessons forward.** Reuse lessons from confirmed failures across your own projects.

## Start in Codex

1. Install from the [Directory](https://chatgpt.com/plugins/plugins_6aa793523ba481918ea921c5438d98c9).
2. Open the target repository in Codex and start a new task.
3. Ask for a safe connection:

~~~text
$project-os Help me connect this repository. Preserve its existing instructions and show me the changes first.
~~~

Codex inspects existing records and previews the proposed changes. You review the proposal before it writes. After the approved setup and checks, start a new task to load the repository instructions.

Installation makes the workflow available; connecting a repository creates or adopts its working records. See [Setup](docs/SETUP.md) for upgrades and alternative installation routes.

<a id="knowledge-that-compounds"></a>
<a id="reuse-a-failure-without-copying-the-old-project"></a>

## Carry useful lessons into the next project

One React Native repository confirms a lifecycle failure. The next project can use its trigger, mechanism, prevention and decisive check without receiving the first project's private history.

Open the destination repository and ask:

~~~text
$project-os Reuse the useful failure lessons from /path/to/earlier-repository here. Prepare only lessons that fit this project, keep the source unchanged and show me one batch to review.
~~~

Give Codex the real source path. It checks both projects, prepares missing lessons and removes private context. You review what fits and why. After approval, Codex transfers the selection and checks the destination. The source stays unchanged.

Codex should record findings during ordinary work, without a separate save request for every bug. Unconfirmed explanations stay labelled as hypotheses. Lessons require review and do not synchronize automatically.

The first repository records the lesson. The next repository does not need to repeat the failure. Software will still invent new ones, but at least it has to be creative.

See [Usage](docs/USAGE.md) for same-machine transfer, portable bundles and working with the ChatGPT companion.

<a id="what-that-looks-like-in-practice"></a>

## Continue a long Codex task

A migration is halfway through. Its plan records changes, rejected approaches and the next check. Open a new task in the same repository:

~~~text
Continue the migration from the repository records. Check the recorded blocker before changing code.
~~~

Codex checks the saved state and continues from the next action. It saves a compact checkpoint after meaningful work. The agent must follow the workflow; Project OS does not secretly record the chat.

## Keep "green" honest

A React Native fix passes TypeScript and unit tests. That is useful evidence, but it does not prove a native modal behaves correctly on the affected device. Project OS preserves both facts: source checks passed and physical acceptance remains open. "Done" stops being a mood.

Ask what remains whenever the result is unclear:

~~~text
$project-os What is still missing before we can call this done?
~~~

The answer names what changed, what was checked and where, what remains and the next action. A required remote migration stays open despite passing local tests. The helper checks records; it cannot independently verify production.

## Add a thought while work is running

Send the instruction normally:

~~~text
Also handle reconnecting after the app has been offline. Keep the existing retry behavior.
~~~

Codex saves the addition while handling your message. Compatible work joins the current outcome; independent work gets a following plan. Conflicts stay recorded until you decide.

## ChatGPT companion

Select `@Engineering Project OS` to ask for explanations or work with supplied files and lesson bundles. ChatGPT cannot see your local checkout through installation alone. Apply returned files deliberately and validate the real repository in Codex.

<a id="install-in-codex-from-github"></a>
<a id="standalone-codex-skill"></a>
<a id="standard-and-program"></a>
<a id="what-is-installed"></a>

## When you want more control

Ordinary development needs ordinary requests after setup. Use `$project-os` to select the skill explicitly when asking about plans, findings, lessons or maintenance. These requests are natural language, not a command parser.

Direct helper commands, record formats and migration details live in the [advanced Reference](docs/REFERENCE.md).

## Continue reading

- [Setup](docs/SETUP.md): install, connect or upgrade a repository.
- [Usage](docs/USAGE.md): ask for the result you need.
- [How it works](docs/HOW_IT_WORKS.md): understand what gets saved and why.
- [Reference](docs/REFERENCE.md): use the helper and inspect exact formats.

For maintainers: [Contributing](CONTRIBUTING.md), [release packaging](docs/PACKAGING.md) and [changelog](CHANGELOG.md). Policies: [security](SECURITY.md), [privacy](docs/PRIVACY.md), [terms](docs/TERMS.md) and [MIT License](LICENSE). For help, use [GitHub Issues](https://github.com/innrvoice/engineering-project-os/issues).
