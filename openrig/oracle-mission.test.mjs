import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync, symlinkSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';

import {
  buildOracleWorkflow,
  parseArguments,
  run,
  serializeWorkflow,
  validateInputs,
} from './create-oracle-mission.mjs';

const candidate = 'a'.repeat(40);
const evidenceRef = 'openrig/release/v1/acceptance-packet.json';

function withTempDir(callback) {
  const directory = mkdtempSync(join(tmpdir(), 'oracle-mission-'));
  try { return callback(directory); } finally { rmSync(directory, { recursive: true, force: true }); }
}

function build(objective = 'Approve the Carbon6 release') {
  return buildOracleWorkflow({ objective, candidate, evidenceRef });
}

test('builds Oracle chair fan-out, fan-in, independent acceptance, and final consolidation', () => {
  const workflow = build().workflow;
  const steps = new Map(workflow.steps.map(step => [step.id, step]));
  const validators = [
    'oracle_strategic_validation',
    'oracle_financial_validation',
    'oracle_legal_validation',
    'oracle_asset_ip_validation',
    'oracle_technology_validation',
  ];

  assert.equal(workflow.target.rig, 'carbon6-office');
  assert.equal(workflow.entry.role, 'oracle_chair');
  const roleTargets = {
    oracle_chair: 'oracle-chair@carbon6-office',
    strategic_validator: 'oracle-strategic-validator@carbon6-office',
    financial_validator: 'oracle-financial-validator@carbon6-office',
    legal_validator: 'oracle-legal-validator@carbon6-office',
    asset_ip_validator: 'oracle-asset-ip-validator@carbon6-office',
    technology_validator: 'oracle-technology-validator@carbon6-office',
    independent_verifier: 'delivery-verifier@carbon6-office',
  };
  for (const [role, target] of Object.entries(roleTargets)) {
    assert.deepEqual(workflow.roles[role], { preferred_targets: [target] });
  }
  for (const id of validators) assert.deepEqual(steps.get(id).depends_on, ['oracle_intake']);
  assert.deepEqual(steps.get('oracle_synthesis').depends_on, validators);
  assert.deepEqual(steps.get('independent_acceptance').depends_on, ['oracle_synthesis']);
  assert.deepEqual(steps.get('oracle_consolidation').depends_on, ['independent_acceptance']);
});

test('uses native dependency-DAG completion exits', () => {
  const steps = build().workflow.steps;
  for (const step of steps.slice(0, -1)) {
    assert.ok(step.allowed_exits.includes('handoff'), `${step.id} must allow handoff to complete its prerequisite`);
    assert.ok(!step.allowed_exits.includes('done'), `${step.id} must not terminate a dependency branch early`);
  }
  const terminal = steps.at(-1);
  assert.deepEqual(terminal.allowed_exits, ['done', 'waiting', 'failed']);
  assert.deepEqual(terminal.next_hop, { mode: 'forbid' });
});

test('binds acceptance to the exact candidate and evidence reference', () => {
  const acceptance = build().workflow.steps.find(step => step.id === 'independent_acceptance').acceptance;
  assert.deepEqual(acceptance, { candidate, verdicts: ['PASS'], evidence_ref: evidenceRef });
});

test('uses a deterministic, input-sensitive mission id', () => {
  const first = build().workflow;
  const repeat = build().workflow;
  const changedObjective = build('Approve a different release').workflow;
  const changedCandidate = buildOracleWorkflow({ objective: first.objective, candidate: 'b'.repeat(40), evidenceRef }).workflow;

  assert.equal(first.id, repeat.id);
  assert.equal(first.version, repeat.version);
  assert.notEqual(first.id, changedObjective.id);
  assert.notEqual(first.id, changedCandidate.id);
  assert.match(first.id, /^oracle-mission-[a-f0-9]{24}$/);
});

test('rejects empty, malformed, repeated, and unknown CLI inputs', () => {
  assert.throws(() => parseArguments(['--objective', 'x', '--objective', 'y']), /only be supplied once/);
  assert.throws(() => parseArguments(['--unknown', 'x']), /Unknown option/);
  assert.throws(() => parseArguments(['--objective']), /Missing value/);
  withTempDir(directory => {
    const base = { objective: ' ', candidate, 'evidence-ref': evidenceRef, output: join(directory, 'mission.json') };
    assert.throws(() => validateInputs(base), /objective must be non-empty/);
    assert.throws(() => validateInputs({ ...base, objective: 'ok', candidate: '$(malicious)' }), /candidate must be/);
    assert.throws(() => validateInputs({ ...base, objective: 'ok', 'evidence-ref': '../secret' }), /unsafe or invalid/);
    assert.throws(() => validateInputs({ ...base, objective: 'bad\u0000value' }), /unsafe control/);
    assert.throws(() => validateInputs({ ...base, objective: 'ok', output: join(directory, 'mission.txt') }), /must end in/);
  });
});

test('refuses a symlink output and writes JSON atomically', () => withTempDir(directory => {
  const target = join(directory, 'target.json');
  const link = join(directory, 'link.json');
  writeFileSync(target, '{}');
  symlinkSync(target, link);
  assert.throws(() => validateInputs({ objective: 'safe', candidate, 'evidence-ref': evidenceRef, output: link }), /symbolic link/);

  const output = join(directory, 'mission.json');
  const result = run(['--objective', 'safe mission', '--candidate', candidate, '--evidence-ref', evidenceRef, '--output', output]);
  const emitted = JSON.parse(readFileSync(output, 'utf8'));
  assert.equal(emitted.workflow.id, result.workflowId);
  assert.equal(emitted.workflow.steps.at(-2).acceptance.candidate, candidate);
}));

test('emits deterministic YAML with quoted user-controlled scalars', () => withTempDir(directory => {
  const output = join(directory, 'mission.yaml');
  const workflow = buildOracleWorkflow({ objective: 'Review: candidate #1', candidate, evidenceRef });
  const first = serializeWorkflow(workflow, output);
  const second = serializeWorkflow(workflow, output);
  assert.equal(first, second);
  assert.match(first, /^workflow:\n/);
  assert.match(first, /objective: "Review: candidate #1"/);
  assert.match(first, new RegExp(`candidate: "${candidate}"`));
}));

test('CLI writes a parseable workflow without invoking a shell', () => withTempDir(directory => {
  const output = join(directory, 'mission.json');
  const script = join(import.meta.dirname, 'create-oracle-mission.mjs');
  const stdout = execFileSync(process.execPath, [script, '--objective', 'CLI mission', '--candidate', candidate, '--evidence-ref', evidenceRef, '--output', output], { encoding: 'utf8' });
  const summary = JSON.parse(stdout);
  const emitted = JSON.parse(readFileSync(output, 'utf8'));
  assert.equal(summary.workflowId, emitted.workflow.id);
}));
