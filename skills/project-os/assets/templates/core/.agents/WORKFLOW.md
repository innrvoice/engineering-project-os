# Durable engineering workflow

Current user and repository instructions take precedence. This managed file supplies the Project OS workflow; project facts, permissions and commands belong to repository-owned records.

## Intake and recovery

Read CONTEXT, STATE, the plan registry, unresolved requests and the active plan with its JSON contract before non-trivial work or after context compaction. When idle, inspect unresolved requests and planned slices. Load only relevant evidence and capability guidance.

Capture a material user correction, clarification or new instruction in the requests registry while handling that message, before long-running work or ending the response. Do not wait for a compaction warning or a separate instruction to save it. Preserve a short source formulation, interpretation, origin, target, relationship, gate IDs and decision. Keep credentials and private data out of records. Discussion of alternatives alone is not an implementation instruction; preserve a consequential ambiguity as needs_clarification.

Integrate compatible additions to the same outcome into the active contract. Route independent outcomes to a planned slice with its own contract and explicit sequence. Preserve conflicts as needs_clarification, ask the necessary question and continue authorized independent work. Capturing and incorporating an authorized clarification requires no separate approval. External actions retain their existing authorization requirements.

Captured means saved. Integrated means routed. Implemented requires verified gates and evidence. Withdrawal requires the user's explicit cancellation or replacement, recorded in decision. Never silently discard, complete or defer an actionable requirement.

## Outcomes and contracts

Define one observable outcome and every prerequisite needed for it, including effective schema, migrations, configuration, delivery and verification in the named target when applicable. A code-only outcome is valid only when it matches the actual instruction and is stated explicitly. Do not move a required prerequisite to an independent slice to make the original plan appear complete.

The plan registry owns status. The plan Markdown owns implementation narrative and decisions. Its JSON contract owns acceptance gates and evidence. The requests registry owns intake and routing. STATE is a compact checkpoint with references, not another task register.

Before resuming a legacy_uncontracted plan, prepare its contract from current instructions and repository truth, preview the change and remove the legacy mark only after validation. Retain historical legacy_closed dispositions without claiming new acceptance.

On material outcome changes, increment contract revision and record the reason and controlling request in the plan narrative. Reassess all evidence before attaching it to the new revision. Also revalidate evidence made stale by code or external changes. Missing access, permission or proof is pending, never not_applicable. Not_applicable requires a scope-grounded reason.

## Checkpoints and closure

At each meaningful checkpoint, reconcile requirements, contracts, findings and evidence. Report what was implemented, what was verified and where, what remains for closure, what needs an owner decision or authorization and which additions belong to the current or a following slice. Leave one exact next action.

Use plan status to expose open gates and requirements. Close only through plan complete with a reviewed checkpoint draft and dry run. A passing structural check does not prove hosted, artifact, production, manual, owner-reported or physical acceptance. The helper validates recorded proof; the agent must judge whether it demonstrates the outcome.

After closure, independent planned slices remain planned. Do not automatically activate the next slice or grant new authority. For a correction to an already closed outcome, preserve historical proof and open a new corrective slice rather than rewriting its completion receipt.

## Boundaries

Project OS has no background access to chat, automatic cross-repository synchronization or independent production verification. Persistence depends on the agent recording incoming instructions. Keep exact candidate package and fresh host behavior checks separate; never replace an installed stable skill with a mutable candidate.
