# Refocus and learning protocol

Run this at startup/restore, after compaction or seat handoff, after an objective
revision, and before a resumed task produces another side effect.

1. Resolve your actual identity with `rig whoami`; read your owned queue rows.
2. Read the current slice → mission → project chain, including each revision,
   content hash and parent relation. Missing links are a named blocker.
3. State the user's intended outcome, your current action and why the action
   advances that outcome. Drop unneeded scope and inherited ceremony.
4. Recheck path ownership, authority and dependencies against current state.
   A revoked grant or changed ancestor suspends dependent execution/acceptance.
5. Read accepted learning records cited by this assignment. Each record needs
   ID, revision, source evidence, author, applicability, reviewing authority,
   status and supersession links. Proposals do not become operating rules merely
   because an agent wrote them.
6. Record the new checkpoint and resume one concrete next action. Escalate only
   the unresolved decision with its evidence; do not repeat settled approvals.

`command-continuity@carbon6-office` curates provenance and dependency links. It proposes
lessons after a demonstrated failure or successful correction, and removes
obsolete checks through versioned supersession rather than erasing history.
Lead accepts applicability; verifier checks evidence. Changing or withdrawing a
lesson invalidates packets citing its old revision and all downstream packets
whose current objective/artifact records have changed. Updating only a file
does not prove any running seat read it: send a bounded refocus and obtain the
seat's updated checkpoint before dependent work resumes.

OpenRig's optional `openrig-core` hook can deliver refocus at runtime boundaries.
This package does not vendor that plugin or silently change provider hooks.
The startup files and this operational protocol work independently. Automatic
post-compaction delivery is unverified until installed hook configuration and a
real successor/compaction exercise establish it. A hook delivery receipt is
not proof of understanding or of task acceptance.
