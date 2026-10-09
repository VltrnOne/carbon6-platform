# Oracle governance protocol

The Oracle council supervises the delivery office. Morpheous supplies direction;
`oracle-chair@carbon6-office` frames it as a versioned objective and fans the same
question to five domain validators. Each validator returns a durable workflow or
queue packet with evidence, assumptions, confidence, risks and a recommendation.
Chat and terminal text are coordination aids and never the decision record.

## Deliberation and delegation

1. Chair records the exact project, mission and slice revisions, requested action,
   decision deadline and authority boundary before fan-out.
2. Strategic, financial, legal, asset/IP and technology validators work from that
   same revision. They may send targeted questions to peers, but every answer used
   in a decision is cited in their durable packet. Each validator writes its full
   signed review to one unique shared workspace file:
   `openrig/shared-state/oracle/<workflow-instance-id>/reviews/<domain>-review.md`. The signature block
   records the validator seat, workflow instance, objective revisions, UTC time and
   explicit vote.
3. Validators explicitly state `support`, `support-with-conditions`, `dissent` or
   `abstain`. Each validator projects its workflow step with its own review path as
   `--evidence-ref`. Reusing the frame packet, council base file or another
   validator's evidence reference is invalid. A result-note body is helpful but is
   not the review record. Chair preserves every dissent and unresolved condition
   verbatim in the synthesis; silence is never a vote.
4. Before synthesis, chair reads `rig workflow trace` and all five unique evidence
   references. Chair verifies that every review file exists, is readable, names the
   expected validator and current objective revisions, and contains a vote. A
   missing, duplicated or shared-base reference blocks synthesis; chair routes or
   resumes the affected packet and records recovery. Only after all five reviews
   pass does chair produce one recommendation with the vote ledger, competing
   options and named conditions, then delegate the authorized delivery slice to
   `command-lead@carbon6-office`. Command lead owns execution routing.
5. `delivery-verifier@carbon6-office` independently tests the exact candidate and
   negative cases. It must not edit the candidate it reviews.

## Authority boundary

Oracle guidance does not itself grant provider access, spending authority,
publishing permission, legal approval or acceptance of an artifact. No Oracle
seat may approve its own work, a peer Oracle's synthesis, or a delivery candidate
merely because the council recommended it. Formal acceptance requires the exact
mission packet defined in ACCEPTANCE.md, a current external authority grant, an
approver independent of the candidate author, and delivery-verifier evidence.

For each mission, command lead creates a mission-specific acceptance packet from
the actual objective ancestry, candidate commit, artifact hashes, evidence hashes,
learning revisions and current grant. The generic workflow never supplies those
values. A successful workflow run records coordination completion only; the packet
validator and authority ledger establish acceptance.

## Escalation and recovery

Disagreement is useful evidence. Chair resolves ordinary tradeoffs by recording
the selected option and why the dissent did not control. Missing authority,
conflicting legal constraints, an unbounded risk or an inconclusive independent
verification becomes a named blocker for Morpheous. On handoff or recovery retain
the objective revision, all validator packets, dissent ledger, delivery owner,
candidate identity and literal next action.
