# Independent verifier procedure

Candidate: `f805729506de40bf78bdaace11ec84f4ad61f4e2`

1. Read the project, mission, slice, learning, grant, artifact manifest,
   evidence files, and proposed packet. Confirm the objective chain and literal
   authority action match the current mission.
2. Verify the history bundle checksum from
   `evidence/oracle-candidate-manifest.json`, verify the bundle, fetch its tip
   into a disposable repository, and confirm the candidate is an ancestor of
   the recorded deployment commit.
3. For every path in `artifact/carbon6-oracle-f805729.manifest.json`, extract
   candidate bytes with `git show <candidate>:<path>` and compare byte count and
   SHA-256 to both the manifest and the deployed path. Record extra deployed
   files separately; do not call them candidate files.
4. Re-run the package tests, spec/workflow validation, slash tests and lint.
   Inspect the 12 seats, daemon status, operating mode, workflow trace, council
   fan-out/fan-in, synthesis, and current verifier frontier. Preserve all five
   validator conditions and dissent.
5. Run the proposed packet against `current-state.pending.json`. Confirm it
   refuses because the decision is pending and no approval ledger row exists.
   Retain the negative stale-ancestor, changed-evidence, revoked-grant,
   wrong-approver and self-approval refusals.
6. If every gate passes, record one durable queue decision with packet ID,
   exact packet digest, verifier identity, zoned decision time, candidate,
   artifact revision, evidence hashes and `APPROVED`. Otherwise record
   `REJECTED` with exact reasons. Do not edit product files or invent a grant.
7. The operator mirrors that exact decision into copies named
   `acceptance-packet.json` and `current-state.json`, then reruns
   `validate-packet.mjs`. Approval is established only when that final run exits
   0. Workflow completion, queue closure, and council support do not substitute
   for this step.

Suggested final check from the repository root:

```sh
node openrig/validate-packet.mjs \
  openrig/release/v2/acceptance-packet.json \
  openrig/release/v2/current-state.json \
  openrig/release/v2 \
  /Users/Morpheous/.npm-global/lib/node_modules/@openrig/cli
```
