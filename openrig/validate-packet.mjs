#!/usr/bin/env node
// Read-only acceptance check. No daemon access, agent launch or file writes.
import { readFileSync, realpathSync, statSync } from 'node:fs';
import { resolve, relative, isAbsolute, sep } from 'node:path';
import { pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';

export const sha256 = value => createHash('sha256').update(value).digest('hex');
export function canonical(value) {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value && typeof value === 'object') return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonical(value[key])}`).join(',')}}`;
  return JSON.stringify(value);
}
export function packetDigest(packet) {
  const { decision: _decision, ...payload } = packet;
  return sha256(canonical(payload));
}

export function loadSchemaValidator(cliRoot) {
  const root = resolve(cliRoot);
  const pkg = JSON.parse(readFileSync(resolve(root, 'package.json'), 'utf8'));
  if (pkg.name !== '@openrig/cli' || pkg.version !== '0.6.7') throw new Error('Validation requires the inspected @openrig/cli 0.6.7 package.');
  const require = createRequire(resolve(root, 'package.json'));
  const Ajv = require('ajv');
  const schema = JSON.parse(readFileSync(new URL('./packet.schema.json', import.meta.url), 'utf8'));
  return new Ajv({ allErrors: true, strict: true }).compile(schema);
}

function record(value) { return value !== null && typeof value === 'object' && !Array.isArray(value); }
function own(object, key) { return record(object) && Object.hasOwn(object, key) ? object[key] : undefined; }
function sameVersion(a, b) { return record(b) && a.revision === b.revision && a.sha256 === b.sha256; }
function within(root, file) {
  const rel = relative(root, file);
  return rel !== '' && rel !== '..' && !rel.startsWith(`..${sep}`) && !isAbsolute(rel);
}
function artifactHash(root, name) {
  if (isAbsolute(name) || name.split(/[\\/]/).includes('..')) throw new Error('path escapes evidence root');
  const file = realpathSync(resolve(root, name));
  if (!within(root, file)) throw new Error('path or symlink escapes evidence root');
  if (!statSync(file).isFile()) throw new Error('evidence must be a regular file');
  return sha256(readFileSync(file));
}

export function validatePacket(packet, current, root, schemaValidate, now = Date.now()) {
  const errors = [];
  if (!schemaValidate(packet)) return { accepted: false, errors: schemaValidate.errors.map(e => `schema ${e.instancePath}: ${e.message}`) };
  if (!record(current) || current.schema_version !== 1 || !['objectives', 'artifacts', 'grants', 'learning', 'approvals'].every(k => record(current[k]))) {
    return { accepted: false, errors: ['Current state must contain schema_version=1 and objective/artifact/grant/learning/approval maps.'] };
  }
  const evidenceRoot = realpathSync(root);
  if (packet.decision.status !== 'approved') errors.push('Decision is not approved.');
  if (packet.decision.packet_sha256 !== packetDigest(packet)) errors.push('Approval does not bind this exact packet.');
  const approval = own(current.approvals, packet.id);
  if (!record(approval) || ['status', 'approver', 'decided_at', 'packet_sha256'].some(key => approval[key] !== packet.decision[key])) errors.push('No matching current approval record from the authority ledger.');
  const decided = Date.parse(packet.decision.decided_at);
  if (!Number.isFinite(decided) || decided > now || !/T.*(?:Z|[+-]\d\d:\d\d)$/.test(packet.decision.decided_at)) errors.push('Decision time must be valid, zoned, and not in the future.');
  const seen = new Set();
  for (const [index, node] of packet.objective_chain.entries()) {
    const live = own(current.objectives, node.id);
    if (seen.has(node.id)) errors.push(`Repeated objective: ${node.id}`);
    seen.add(node.id);
    if (!sameVersion(node, live) || live.kind !== node.kind || live.parent_id !== node.parent_id || live.parent_revision !== node.parent_revision) errors.push(`Stale or missing objective: ${node.id}`);
    const parent = packet.objective_chain[index - 1];
    if (index === 0 ? (node.kind !== 'project' || node.parent_id !== null || node.parent_revision !== null) : (node.parent_id !== parent.id || node.parent_revision !== parent.revision)) errors.push(`Broken objective ancestry: ${node.id}`);
  }
  if (packet.objective_chain.length !== 3 || packet.objective_chain.map(n => n.kind).join('/') !== 'project/mission/slice') errors.push('Ancestry must be exactly project → mission → slice.');
  const artifact = packet.artifact;
  const liveArtifact = own(current.artifacts, artifact.path);
  if (!sameVersion(artifact, liveArtifact) || liveArtifact.candidate_sha !== artifact.candidate_sha) errors.push('Artifact revision/candidate is stale or missing.');
  const checkFile = (file, hash) => {
    try { if (artifactHash(evidenceRoot, file) !== hash) errors.push(`Content changed: ${file}`); }
    catch (err) { errors.push(`Unreadable/unsafe artifact ${file}: ${err.message}`); }
  };
  checkFile(artifact.path, artifact.sha256);
  const evidencePaths = new Set();
  for (const item of packet.evidence) {
    if (evidencePaths.has(item.path) || item.path === artifact.path) errors.push(`Evidence must be distinct: ${item.path}`);
    evidencePaths.add(item.path);
    if (item.candidate_sha !== artifact.candidate_sha || item.artifact_revision !== artifact.revision || item.verdict !== 'PASS') errors.push(`Evidence does not pass for this exact candidate: ${item.path}`);
    checkFile(item.path, item.sha256);
  }
  for (const file of packet.terminal_gate.evidence_paths) {
    if (!packet.evidence.some(e => e.path === file && e.kind === 'terminal_outcome' && e.verdict === 'PASS')) errors.push(`Terminal outcome evidence missing: ${file}`);
  }
  const auth = packet.authority;
  const grant = own(current.grants, auth.grant_id);
  if (!sameVersion(auth, grant) || grant.enabled !== true) errors.push('Authority grant is stale, missing or revoked.');
  else {
    for (const [key, expected] of [['actors', auth.actor], ['actions', auth.action], ['approvers', packet.decision.approver]]) {
      if (!Array.isArray(grant[key]) || !grant[key].includes(expected)) errors.push(`Authority does not permit ${key}: ${expected}`);
    }
    if (auth.actor === packet.decision.approver) errors.push('Independent acceptance requires an approver other than the actor.');
    if (grant.expires_at !== null && (typeof grant.expires_at !== 'string' || !/T.*(?:Z|[+-]\d\d:\d\d)$/.test(grant.expires_at) || !Number.isFinite(Date.parse(grant.expires_at)) || Date.parse(grant.expires_at) <= now)) errors.push('Authority expiry missing, invalid or elapsed.');
  }
  const learned = new Set();
  for (const item of packet.learning) {
    const live = own(current.learning, item.id);
    if (learned.has(item.id)) errors.push(`Repeated learning dependency: ${item.id}`);
    learned.add(item.id);
    if (!sameVersion(item, live) || live.status !== 'accepted') errors.push(`Learning withdrawn, stale or missing: ${item.id}`);
  }
  return { accepted: errors.length === 0, packet_sha256: packetDigest(packet), errors };
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  try {
    const [packetPath, currentPath, evidenceRoot, cliRoot] = process.argv.slice(2);
    if (!packetPath || !currentPath || !evidenceRoot || !cliRoot || process.argv.length !== 6) throw new Error('Usage: node openrig/validate-packet.mjs PACKET CURRENT_STATE EVIDENCE_ROOT OPENRIG_CLI_ROOT');
    const result = validatePacket(JSON.parse(readFileSync(packetPath, 'utf8')), JSON.parse(readFileSync(currentPath, 'utf8')), evidenceRoot, loadSchemaValidator(cliRoot));
    console.log(JSON.stringify(result, null, 2));
    process.exitCode = result.accepted ? 0 : 1;
  } catch (err) { console.error(JSON.stringify({ accepted: false, errors: [err.message] })); process.exitCode = 1; }
}
