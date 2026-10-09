# Carbon6 Oracle coordination candidate f805729

This directory is the authority and acceptance packet for the bounded Oracle
coordination proof built from candidate
`f805729506de40bf78bdaace11ec84f4ad61f4e2` and operated on `vltrn-brain`.
The deployed source tree is identified separately as
`de40ea72e206bed3ac58a02341a36af396d178cd` because that descendant added the
mission-specific workflow and proof binding.

The user directive on 2026-10-09 authorized getting the Oracle-led agent
collaboration operating. That direct directive is the authority source for the
narrow internal action in `authority/grant.json`. OpenRig delegated mode is
recorded as `grants_authority=false`; it is an operating posture and is not the
grant source. Oracle votes and chair synthesis are advisory inputs and cannot
approve their own result.

## Current state

- The project, mission, slice, learning, artifact manifest, and bounded active
  grant are represented in `current-state.pending.json`.
- `acceptance-packet.proposed.json` is intentionally pending. Its packet digest
  is stable because `decision` is excluded from the digest.
- `delivery-verifier@carbon6-office` must independently verify the exact files,
  evidence, current grant, negative cases, and terminal criterion before it can
  issue an approval or rejection.
- The workflow reaching the independent verifier boundary proves the Oracle
  coordination path. It does not itself prove formal acceptance, external
  delivery, provider acceptance, or authority to mutate infrastructure.

Follow `verifier-instructions.md`. An operator may create final
`acceptance-packet.json`, `current-state.json`, and `release-record.json` only
from the verifier's durable decision. Until then, no accepted v2 record exists.
