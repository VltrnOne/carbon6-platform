import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, rmSync, symlinkSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { resolve } from 'node:path';
import { validatePacket, loadSchemaValidator, packetDigest, sha256 } from './validate-packet.mjs';

const cliRoot = process.env.OPENRIG_CLI_ROOT || '/Users/Morpheous/.npm-global/lib/node_modules/@openrig/cli';
const schema = loadSchemaValidator(cliRoot);
const now = Date.parse('2026-10-09T00:00:00Z');

// Synthetic records exist only inside disposable tests; no operational ledger is seeded.
function fixture(t) {
  const root = mkdtempSync(resolve(tmpdir(), 'carbon6-packet-test-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  writeFileSync(resolve(root, 'artifact.txt'), 'candidate bytes\n');
  writeFileSync(resolve(root, 'proof.txt'), 'terminal outcome evidence\n');
  const candidate = sha256('test candidate');
  const chain = ['project', 'mission', 'slice'].map((kind, index, all) => ({
    id: kind, kind, revision: 1, sha256: sha256(kind), parent_id: index ? all[index - 1] : null, parent_revision: index ? 1 : null,
  }));
  const packet = {
    schema_version: 1, id: 'isolated-test-packet', objective_chain: chain,
    artifact: { path: 'artifact.txt', revision: 1, sha256: sha256('candidate bytes\n'), candidate_sha: candidate },
    evidence: [{ path: 'proof.txt', sha256: sha256('terminal outcome evidence\n'), candidate_sha: candidate, artifact_revision: 1, verdict: 'PASS', kind: 'terminal_outcome' }],
    authority: { grant_id: 'test-grant', revision: 1, sha256: sha256('grant'), actor: 'test-builder', action: 'internal.change.accept' },
    learning: [{ id: 'test-lesson', revision: 1, sha256: sha256('lesson') }],
    terminal_gate: { outcome: 'Exercise a bounded result', criterion: 'Observed outcome matches acceptance', evidence_paths: ['proof.txt'] },
    decision: { status: 'approved', approver: 'test-reviewer', decided_at: '2026-10-08T23:00:00Z', packet_sha256: '' },
  };
  packet.decision.packet_sha256 = packetDigest(packet);
  const current = {
    schema_version: 1,
    objectives: Object.fromEntries(chain.map(node => [node.id, structuredClone(node)])),
    artifacts: { 'artifact.txt': structuredClone(packet.artifact) },
    grants: { 'test-grant': { revision: 1, sha256: packet.authority.sha256, enabled: true, actors: ['test-builder'], actions: ['internal.change.accept'], approvers: ['test-reviewer'], expires_at: null } },
    learning: { 'test-lesson': { revision: 1, sha256: packet.learning[0].sha256, status: 'accepted' } },
    approvals: { [packet.id]: structuredClone(packet.decision) },
  };
  return { root, packet, current, check: () => validatePacket(packet, current, root, schema, now), resign: () => { packet.decision.packet_sha256 = packetDigest(packet); current.approvals[packet.id] = structuredClone(packet.decision); } };
}

test('accepts an exact candidate with current authority, independent ledger approval and terminal evidence', t => {
  assert.deepEqual(fixture(t).check().errors, []);
});
test('rejects schema drift instead of silently ignoring it', t => {
  const f = fixture(t); f.packet.authority.override = true;
  assert.equal(f.check().accepted, false);
});
test('parent revision change invalidates a descendant packet', t => {
  const f = fixture(t); f.current.objectives.project.revision++;
  assert.match(f.check().errors.join(' '), /Stale or missing objective: project/);
});
test('broken chain is refused even if local records match', t => {
  const f = fixture(t); f.packet.objective_chain[2].parent_id = 'project'; f.current.objectives.slice.parent_id = 'project'; f.resign();
  assert.match(f.check().errors.join(' '), /Broken objective ancestry/);
});
test('changed artifact bytes invalidate approval', t => {
  const f = fixture(t); writeFileSync(resolve(f.root, 'artifact.txt'), 'changed');
  assert.match(f.check().errors.join(' '), /Content changed: artifact/);
});
test('evidence for a different candidate refuses acceptance', t => {
  const f = fixture(t); f.packet.evidence[0].candidate_sha = sha256('different'); f.resign();
  assert.match(f.check().errors.join(' '), /exact candidate/);
});
test('passing unit evidence alone is not terminal completion', t => {
  const f = fixture(t); f.packet.evidence[0].kind = 'test'; f.resign();
  assert.match(f.check().errors.join(' '), /Terminal outcome evidence missing/);
});
test('revocation defeats a previously valid approval', t => {
  const f = fixture(t); f.current.grants['test-grant'].enabled = false;
  assert.match(f.check().errors.join(' '), /revoked/);
});
test('wrong approver is refused even with a matching packet digest and ledger row', t => {
  const f = fixture(t); f.packet.decision.approver = 'unauthorized'; f.resign();
  assert.match(f.check().errors.join(' '), /Authority does not permit approvers/);
});
test('a self-authored approval absent from current ledger is refused', t => {
  const f = fixture(t); delete f.current.approvals[f.packet.id];
  assert.match(f.check().errors.join(' '), /authority ledger/);
});
test('self approval cannot pass an overbroad grant', t => {
  const f = fixture(t); f.packet.decision.approver = 'test-builder'; f.current.grants['test-grant'].approvers.push('test-builder'); f.resign();
  assert.match(f.check().errors.join(' '), /Independent acceptance/);
});
test('expired grant and unknown expiry fail closed', t => {
  const f = fixture(t); f.current.grants['test-grant'].expires_at = '2026-10-08T00:00:00Z';
  assert.match(f.check().errors.join(' '), /expiry/);
  delete f.current.grants['test-grant'].expires_at;
  assert.match(f.check().errors.join(' '), /expiry/);
});
test('withdrawn or revised learning invalidates its dependent packet', t => {
  const f = fixture(t); f.current.learning['test-lesson'].status = 'withdrawn';
  assert.match(f.check().errors.join(' '), /Learning withdrawn/);
  f.current.learning['test-lesson'].status = 'accepted'; f.current.learning['test-lesson'].revision++;
  assert.match(f.check().errors.join(' '), /Learning withdrawn/);
});
test('changing the proposed action without reapproval fails binding', t => {
  const f = fixture(t); f.packet.authority.action = 'external.publish';
  assert.match(f.check().errors.join(' '), /exact packet/);
});
test('path traversal and symlink escape are refused', t => {
  const f = fixture(t); f.packet.evidence[0].path = '../outside.txt'; f.packet.terminal_gate.evidence_paths = ['../outside.txt']; f.resign();
  assert.match(f.check().errors.join(' '), /escapes evidence root/);
  symlinkSync(tmpdir(), resolve(f.root, 'outside'));
  f.packet.evidence[0].path = 'outside'; f.packet.terminal_gate.evidence_paths = ['outside']; f.resign();
  assert.match(f.check().errors.join(' '), /escapes evidence root/);
});
test('missing current maps fail closed', t => {
  const f = fixture(t); delete f.current.objectives;
  assert.equal(f.check().accepted, false);
});
test('whitespace-only outcome is not an acceptance criterion', t => {
  const f = fixture(t); f.packet.terminal_gate.criterion = '   '; f.resign();
  assert.equal(f.check().accepted, false);
});
test('future decision and changed evidence are refused', t => {
  const f = fixture(t); f.packet.decision.decided_at = '2027-01-01T00:00:00Z'; f.resign();
  writeFileSync(resolve(f.root, 'proof.txt'), 'different evidence');
  assert.match(f.check().errors.join(' '), /Decision time/);
  assert.match(f.check().errors.join(' '), /Content changed: proof/);
});
