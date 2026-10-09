# Carbon6 OpenRig release candidate 5cf9a39

This directory contains the proposal and final acceptance record for candidate
`5cf9a39f92c884c98a36e496c2f213906af8042f`. It binds the release to one
project, one mission, one slice, the exact package file bytes, recorded package
checks, a narrowly scoped authority proposal, and the runtime lesson that this
candidate depends on.

The `.proposed.json` files preserve the fail-closed preapproval state. The final
`acceptance-packet.json` and `current-state.json` mirror the independent
approval recorded by `delivery-verifier@carbon6-office` in OpenRig queue item
`carbon6-release-5cf9a39-r1-approval`, transition 26. The final packet validates
with digest `1f3ceeaa6669d20bdd74afb5f8ff565ee07193dce0c9b1eb52b3c73d1ec76e75`.
The earlier denial caused by four one-byte deployment mismatches remains in the
queue audit trail; acceptance followed a fresh re-verification after correction.

## Record map

- `objectives/`: immutable project, mission and slice source records.
- `artifact/`: SHA-256 manifest for every candidate file under `openrig/**` and
  `slash-commands/**`.
- `evidence/`: local package checks, the preserved unfulfilled placeholder, and
  the final live terminal outcome sourced from queue transition 23.
- `learning/`: the accepted Node, HOME and SSH runtime boundary for this
  candidate.
- `authority/grant.proposed.json`: one candidate, one packet, one literal
  internal acceptance action, one builder and one independent verifier. It
  expires on `2026-10-16T23:59:59Z`.
- `current-state.proposed.json`: proposed registry import. Its empty approvals
  map must stay empty until the protected ledger records the verifier decision.
- `acceptance-packet.proposed.json`: exact preapproval packet.
- `current-state.json`: operator export that mirrors the bounded grant, terminal
  evidence source, and the verifier's exact decision record.
- `acceptance-packet.json`: accepted packet bound to the final evidence and
  independent approval.
- `release-record.json`: operator index of the principal digests.

## Independent completion record

1. Import or recreate the objective, artifact, learning and grant records in
   the protected authority ledger. Confirm their revisions and hashes are still
   current. Do not treat this builder-authored export as authoritative.
2. Dispatch the slice to `command-lead@carbon6-office` on `vltrn-brain`, naming
   all three objective IDs/revisions, the artifact revision, the full candidate
   SHA and the terminal criterion from the packet.
3. `delivery-verifier@carbon6-office` independently checks the deployed commit,
   six-seat readiness, queue terminal outcome and required negative refusal.
4. Replace `evidence/live-terminal-outcome.pending.json` with the verifier's
   observed PASS or FAIL record. Recalculate its SHA-256 in the packet.
5. Recalculate the packet digest with the exported `packetDigest` function from
   `openrig/validate-packet.mjs`. Record the exact approved/rejected decision in
   the protected ledger, then mirror that row into a fresh current-state export.
6. Run from the repository root:

   ```sh
   /opt/homebrew/opt/node@22/bin/node openrig/validate-packet.mjs \
     openrig/release/v1/acceptance-packet.proposed.json \
     openrig/release/v1/current-state.proposed.json \
     openrig/release/v1 \
     /Users/Morpheous/.npm-global/lib/node_modules/@openrig/cli
   ```

The proposal refuses before steps 2 through 5. The final packet exits 0 against
the current operator export and unchanged artifact/evidence bytes. Re-run the
same command with `acceptance-packet.json` and `current-state.json` before any
future use; ancestor, artifact, evidence, grant or learning revision changes
invalidate this decision.
