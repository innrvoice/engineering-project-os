# Privacy Policy

Effective date: September 14, 2026.

## Scope

Engineering Project OS is a skills-only Codex plugin that helps inspect, create and maintain
repository-local engineering records. This policy describes data handling by the Project OS plugin
and its publisher.

## Data processing

Project OS does not operate a hosted service, MCP server, user account system or analytics service.
Its bundled Python helper initiates no network requests. When a user explicitly invokes a workflow,
the plugin may read files in the repository or other local path selected by the user and may write
Project OS records inside the selected target repository after the applicable preview and approval
steps.

The publisher does not receive, transmit or store repository contents, prompts, credentials or usage
telemetry through Project OS. Data processed by ChatGPT, Codex, GitHub or another environment remains
subject to that provider's terms and privacy policy.

## Retention and deletion

Project OS has no publisher-controlled data store and therefore retains no user data on behalf of the
publisher. Repository files created by Project OS remain under the user's control and can be reviewed,
versioned or removed using the repository's normal tools and policies.

## Security and permissions

Project OS requests only the filesystem and command permissions needed for the selected repository
workflow. Installation does not grant authority to change application code, install dependencies,
delete files, commit, push, deploy or contact external systems. Those actions remain subject to the
user's instructions and the host environment's permission controls.

Security details and vulnerability reporting instructions are available in the
[Security Policy](../SECURITY.md).

## Changes and contact

Material changes to this policy will be published in this repository with an updated effective date.
Questions can be filed through [GitHub Issues](https://github.com/innrvoice/engineering-project-os/issues).
