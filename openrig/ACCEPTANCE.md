# Acceptance contract — version 1

## Delivery sequence

1. Front office and lead bind the authorized objective to one project → mission
   → slice chain. Every node has a stable ID, revision, content hash and exact
   parent revision. Lead assigns a queue owner, paths, action and terminal gate.
2. Builder or office owner produces an artifact for a candidate commit. Record
   its relative path, revision and SHA-256; evidence must name that same commit
   and artifact revision. No authoritative production record is seeded here.
3. Verifier exercises the user-visible outcome and necessary negative cases.
   Passing a parser, queue transition or process health probe is insufficient.
4. The authorized approver receives objective ancestry, exact artifact,
   evidence, learning dependencies and action scope. The authority ledger
   records the decision against the packet digest; self-approval is rejected.
   Oracle recommendations, votes and synthesis are inputs to this decision and
   cannot authorize or approve their own output.
5. Run `validate-packet.mjs` against a freshly read authoritative state and the
   actual artifact/evidence files. At an execution boundary, the application
   must revalidate and execute atomically or use version preconditions. This
   read-only CLI does not execute actions or eliminate a later race.
6. Close the queue row with an explicit disposition. Record accepted outcome
   separately. A provider receipt establishes only the result it actually says.

## Packet and state

`packet.schema.json` is a closed Draft-07 JSON Schema. `validate-packet.mjs`
checks schema, full objective ancestry, current revisions, file bytes, candidate
binding, positive terminal outcome evidence, current authority, independent
approval identity, decision time and learning validity. It writes no files.

The approval digest is SHA-256 over UTF-8 canonical JSON of the whole packet
except `decision`. Object keys are sorted recursively; array order is retained.
Use the exported `packetDigest` function instead of another serializer. Approval
metadata must exactly match `current.approvals[packet.id]` from the authority
ledger. The packet author cannot authorize itself by adding an approver name.

The current-state input is a fresh trusted export, not a builder-authored file:

| Map | Key | Required current record |
| --- | --- | --- |
| `objectives` | Objective ID | `kind`, `revision`, `sha256`, `parent_id`, `parent_revision`; root parents are null |
| `artifacts` | Artifact relative path | `revision`, `sha256`, `candidate_sha` |
| `grants` | Grant ID | `revision`, `sha256`, `enabled`, `actors[]`, `actions[]`, `approvers[]`, `expires_at` (zoned date or explicit null) |
| `learning` | Learning ID | `revision`, `sha256`, `status: accepted` |
| `approvals` | Packet ID | Exact `status`, `approver`, `decided_at`, `packet_sha256` |

The export also has `schema_version: 1`. These maps must exist even when empty.
Grant scope uses literal action names; there are no implicit wildcards. Source
authority is external to this checker: protect the current-state export and
ledger with the host application's authentication and access controls. A local
file check does not prove who authored a file, whether a test claim is truthful,
or whether an external provider accepted an action.

Evidence paths must stay inside the explicit evidence root, including after
symlink resolution. Evidence is separate from the candidate artifact. All listed
evidence must pass for the exact artifact revision/candidate; terminal-gate
evidence must have `kind: terminal_outcome`. Hashes are lowercase SHA-256; a
candidate is a full 40- or 64-character Git object ID. Empty goals are invalid.

## Cascading invalidation

The authority registry maintains reverse dependency links for objective parents,
artifact revisions and learning provenance. Revising a project or mission makes
every descendant packet with the old ancestor invalid. Changing artifact bytes,
evidence bytes or candidate revision invalidates that approval. Withdrawing a
grant or lesson invalidates every packet referring to it. Downstream artifacts
derived from a changed lesson or source must receive new current revisions, so
their dependent packets also fail. Preserve old records for the audit trail.

The validator mechanically checks all declared dependencies against current
state. It cannot discover undeclared dependencies or automatically mutate a
remote registry. Learning owner enumerates impacted records; lead updates the
registry and verifier checks the transitive set before resumption.

## Acceptance gates derived from the LST-V study

The local transcript is the source, not a verified benchmark. These gates
operationalize its claims and the owner's extracted requirements:

| Gate | Required evidence | Source segment |
| --- | --- | --- |
| Stable coordination | Lead address survives a controlled occupant handoff; owned work and role remain bound | 05:23–06:16 |
| Outcome ancestry | Packet resolves project, mission and slice with exact parent revisions; changed ancestor refuses acceptance | 07:10–08:09; 18:24–19:36 |
| Terminal completion | Real requested behavior works; one negative case fails correctly; verification names candidate | 07:55–08:09 |
| Informed authority | Approver sees the exact artifact/evidence/action and holds current grant; wrong approver and revoked grant refuse | 15:54–16:43 |
| Learning validity | Evidence-backed lesson revision and provenance survive handoff; withdrawal invalidates dependent acceptance | 06:01–06:16; owner-extracted requirement |
| Refocus | Compaction/handoff/objective change produces a checkpoint showing current intent and a justified next action | 18:24–19:36 |
| Useful throughput | Report accepted outcomes separately from transitions, handoffs and approvals; investigate ceremony without progress | 11:16–12:15; 22:06–23:11 |
| Oracle deliberation | Five validators receive the same objective revision; durable packets preserve every vote, question, answer, condition and dissent through chair synthesis | Carbon6 governance policy |
| Independent delivery review | Delivery verifier exercises the exact candidate and negative cases; no Oracle seat or candidate author can substitute its own approval | Carbon6 governance policy |
| Bounded operation | Twelve declared seats; at most two admitted delivery items, no overlapping writer, no unauthorized growth | Carbon6 operating policy |

The talk calls APM **agent productivity monitoring** at 22:19–22:23. Exported
queue/event telemetry can supply activity counts; acceptance records supply
outcomes. Their ratio is diagnostic, not a productivity score or acceptance
criterion. Unknown coverage stays unknown. No autonomous productivity sensor
or host-enforced delivery quota is installed by this package.
