# Carbon6 OpenRig package

Twelve stable Codex seats, current official OpenRig **0.6.7** schema, an explicit
delivery contract and a read-only acceptance checker. No models, provider
credentials, real tasks or acceptance records are fabricated. Runtime/model
selection inherits the working Codex account; model availability is a live gate.

| Address | Ownership |
| --- | --- |
| `oracle-chair@carbon6-office` | Governing coordinator; objective framing, council fan-out, dissent ledger, synthesis and delegation |
| `oracle-strategic-validator@carbon6-office` | Strategy, sequencing, stakeholders and measurable outcomes |
| `oracle-financial-validator@carbon6-office` | Cost, capacity, downside and financial return |
| `oracle-legal-validator@carbon6-office` | Legal, privacy, consent, compliance and enforceability |
| `oracle-asset-ip-validator@carbon6-office` | Ownership, provenance, confidentiality, defensibility and asset value |
| `oracle-technology-validator@carbon6-office` | Architecture, security, reliability, rollback and technical evidence |
| `command-lead@carbon6-office` | Delivery coordinator; execution assignments, admission and outcomes |
| `office-front@carbon6-office` | Intake, requirements, customer-facing drafts |
| `office-back@carbon6-office` | Records, reconciliation, operations and dependencies |
| `delivery-builder@carbon6-office` | Assigned implementation and automation |
| `delivery-verifier@carbon6-office` | Independent exact-candidate evidence and acceptance |
| `command-continuity@carbon6-office` | Learning provenance, invalidation and refocus |

`rig.yaml` contains only supported fields. Role authority and the two-item
delivery limit are operating policy, not security isolation or a scheduler
quota. `permission_policy: builtin:yolo` removes native command prompts because
the verified Linux worker cannot initialize the Codex UID-map sandbox. This is
full OS-user access and does not enforce the prose authority contract. Role
files are delivered as seat-specific text, so roles do not
overwrite each other's shared guidance. The rig is named `carbon6-office`, not `kernel`.

## Runtime wrapper

Use `sh openrig/rig.sh` for every daemon and rig command below. It selects
Node 22 on Apple Silicon and an isolated runtime HOME at
`~/.openrig/carbon6-runtime-home`, retaining the original `OPENRIG_HOME`,
`CODEX_HOME` and PATH. The isolated home contains only
minimal skill directories initially; no credentials or user skill collection
are copied. `--environment` prints paths without creating directories.

This is required on this workstation: the root operator measured **41,139**
entries under the real `~/.agents/skills`. OpenRig 0.6.7 scans that global tree
synchronously for each Codex member; the attempted launch stalled daemon
requests. Isolating HOME bounds discovery to the intentionally small catalog.
This is an environment mitigation, not a fix to upstream scanning behavior.

`CODEX_HOME` intentionally remains shared. OpenRig can still write Codex
hooks and trust configuration. The wrapper unsets `CLAUDE_CONFIG_DIR`: this
pilot is Codex-only, and pointing it at the real `.claude` directory caused
a measured Claude authentication failure. Claude support requires a separately
verified auth layout before adding any Claude seats. This wrapper is not an
account sandbox. Back up those configurations before first daemon startup.
Do not add a symlink to the large global skills tree under the runtime home.
The daemon inherits its environment only when started: an existing daemon
started outside the wrapper must be stopped deliberately before restart here;
changing the client environment cannot repair that running process.

Overrides: `CARBON6_REAL_HOME`, `CARBON6_RUNTIME_HOME`, `CARBON6_NODE_BIN`
(directory containing `node`), and standard OpenRig/Codex configuration
variables. All configured paths must be absolute. No installation is automatic.
Inside a managed Codex seat, the wrapper derives the operator home from the
absolute `CODEX_HOME` so the already-isolated `HOME` is not nested again.

## Validate without launching

Run from `/Users/Morpheous/carbon6-openrig`:

```sh
sh openrig/rig.sh --environment
/opt/homebrew/opt/node@22/bin/node openrig/validate-specs.mjs /Users/Morpheous/.npm-global/lib/node_modules/@openrig/cli
/opt/homebrew/opt/node@22/bin/node --test openrig/packet.test.mjs
sh openrig/rig.sh spec validate openrig/rig.yaml --json
sh openrig/rig.sh spec preflight openrig/rig.yaml --rig-root /Users/Morpheous/carbon6-openrig/openrig --json
```

The offline validator uses the installed official 0.6.7 parser, AgentSpec
resolver and schema validator. It also checks startup files, profiles and cwd
existence. It never starts a daemon. Native CLI preflight may require a running
daemon; report that dependency, never silently start one during validation.

## Staged activation

1. **Offline:** validation and packet negative tests pass; inspect wrapper paths
   and provider configuration changes. Verify selected Codex login and Node22
   SQLite ABI. Herdr is optional; tmux is required.
2. **Control plane:** start the daemon through the wrapper only when authorized,
   then check health and preview. `OPENRIG_NO_KERNEL=1` prevents an unrelated
   automatically launched kernel team. Retain it for this bounded topology.

   ```sh
   OPENRIG_NO_KERNEL=1 sh openrig/rig.sh daemon start
   sh openrig/rig.sh doctor --json
   sh openrig/rig.sh up openrig/rig.yaml --plan --json
   ```

3. **Seat readiness:** `up` starts all twelve declared seats; it is not a subset
   launch. Seats acknowledge identity/context and wait for owned work. Inspect
   readiness and provider acceptance before assigning a task.

   ```sh
   sh openrig/rig.sh up openrig/rig.yaml --json
   sh openrig/rig.sh ps --nodes --rig carbon6-office --json
   sh openrig/rig.sh terminal open carbon6-office --window --json
   sh openrig/rig.sh send command-lead@carbon6-office "Verify seat identities and required context; report readiness and wait for an assigned objective."
   ```

4. **One real slice:** lead admits one bounded authorized item, exact ownership,
   independent verifier and a terminal gate. Demonstrate the packet and stale
   approval refusal. A message alone is not a queue row.
5. **Bounded parallel work:** after that result is accepted, lead may admit a
   second nonconflicting delivery item. Twelve seated conversations do not imply
   twelve simultaneous implementation jobs. No nested spawning or automatic growth.
6. **Continuity:** write checkpoints; exercise controlled handoff/recovery and
   confirm stable addresses, retained ownership and current objective refocus.
   Failed/partial restore remains visible. Do not expand throughput until these
   acceptance gates pass.

To stop the team with a snapshot attempt:

```sh
sh openrig/rig.sh down carbon6-office --snapshot
sh openrig/rig.sh restore-check --rig carbon6-office
```

Snapshot failure does not block OpenRig teardown. Inspect its actual result.
Do not stop the shared daemon merely to stop this team.

## Server persistence

`server-daemon.sh` monitors the detached OpenRig daemon and exits if its health
check fails, allowing `carbon6-openrig.service` to restart the control plane.
Install the unit as a user service on the designated worker and enable user
linger so it starts without an interactive SSH login. The unit assumes the
verified server layout under `~/carbon6-openrig`, Node 22 under `~/.local/opt`
and the dedicated authenticated `~/.codex-openrig` home. Inspect and adjust the
unit when those paths change.

## Evidence and acceptance

See [ACCEPTANCE.md](ACCEPTANCE.md) and [REFOCUS.md](REFOCUS.md). Invoke the
packet checker with four actual paths, in order: packet JSON, trusted current
state JSON, artifact/evidence root, installed `@openrig/cli` directory. It exits
0 only for accepted current evidence, 1 on refusal/error. The exported
`packetDigest` helper computes the digest to place in an authorized ledger.
No packet is provided because no live work has yet been accepted.

The checker can be called as a normal tool at review time. OpenRig startup
actions do not support shell commands; none is injected into RigSpec. A
successful checker run is an advisory until the caller wires it to the real
decision/execution boundary. It does not install a policy engine, authenticate
an approver, verify evidence semantics or make external actions atomic.

## Official references and provenance

- [RigSpec reference, pinned 0.6.7](https://github.com/mvschwarz/openrig/blob/v0.6.7/docs/reference/rig-spec.md)
- [AgentSpec reference, pinned 0.6.7](https://github.com/mvschwarz/openrig/blob/v0.6.7/docs/reference/agent-spec.md)
- [Refocus channel](https://github.com/mvschwarz/openrig/blob/v0.6.7/docs/reference/refocus-channel.md)
- [Work tree and proof](https://openrig.dev/docs/work-tree)
- [Queue coordination](https://openrig.dev/docs/coordination)
- [Provider configuration side effects](https://github.com/mvschwarz/openrig/blob/v0.6.7/README.md#what-openrig-changes-on-your-machine)
- LST-V source: local transcript `/tmp/lstv-herdr.xe9mGr/transcript.txt`; acceptance
  mapping includes timestamps in ACCEPTANCE.md. Temporary source availability
  is not guaranteed; no private source URL is embedded.

## Oracle supervision

`ORACLE.md` defines the council's authority boundary and durable deliberation
rules. `workflows/oracle-supervision.workflow.yaml` is the supported dependency
DAG: the chair frames one revision, five validators fan out, the chair fans in
their preserved votes and dissent, then command lead routes delivery through the
builder and independent verifier. The final workflow step assembles the exact
mission packet but cannot approve it. A current independent approver named by the
authority ledger remains mandatory.

The standalone `oracle-pod.fragment.yaml` mirrors the expansion-supported pod
fields and Oracle cross-pod edges in `rig.yaml`; live `rig expand` adds the six
Oracle seats without restarting the existing office pods. OpenRig 0.6.7's
expansion ingress does not carry `continuity_policy`, so the full spec retains
that policy for clean launches while each expanded seat still has its explicit
`restore_policy`. The workflow provides runtime chair-to-office routing.

Package validation is distinct from live operation. Record actual launch,
provider acceptance, terminal outcome and recovery results before claiming
the twelve-seat team is operational or production accepted.
