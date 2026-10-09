#!/usr/bin/env node

import { createHash } from 'node:crypto';
import {
  existsSync,
  lstatSync,
  openSync,
  renameSync,
  rmSync,
  statSync,
  writeFileSync,
  closeSync,
} from 'node:fs';
import { basename, dirname, extname, isAbsolute, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const REQUIRED_OPTIONS = ['objective', 'candidate', 'evidence-ref', 'output'];
const CANDIDATE_PATTERN = /^(?:[a-f0-9]{40}|[a-f0-9]{64})$/;
const SAFE_EVIDENCE_SEGMENT = /^[A-Za-z0-9._-]+$/;
const OUTPUT_EXTENSIONS = new Set(['.json', '.yaml', '.yml']);

function fail(message) {
  throw new Error(message);
}

export function parseArguments(argv) {
  const values = new Map();
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (!token.startsWith('--')) fail(`Unexpected positional argument: ${token}`);
    const key = token.slice(2);
    if (!REQUIRED_OPTIONS.includes(key)) fail(`Unknown option: --${key}`);
    if (values.has(key)) fail(`Option may only be supplied once: --${key}`);
    const value = argv[index + 1];
    if (value === undefined || value.startsWith('--')) fail(`Missing value for --${key}`);
    values.set(key, value);
    index += 1;
  }
  for (const key of REQUIRED_OPTIONS) {
    if (!values.has(key)) fail(`Missing required option: --${key}`);
  }
  return Object.fromEntries(values);
}

function validateText(name, value, maximumLength) {
  if (typeof value !== 'string' || value.trim().length === 0) fail(`${name} must be non-empty.`);
  if (value.length > maximumLength) fail(`${name} exceeds ${maximumLength} characters.`);
  if (/\0|[\u0001-\u0008\u000b\u000c\u000e-\u001f\u007f]/u.test(value)) {
    fail(`${name} contains unsafe control characters.`);
  }
  return value.trim();
}

export function validateInputs(input) {
  const objective = validateText('objective', input.objective, 4000);
  const candidate = validateText('candidate', input.candidate, 64);
  if (!CANDIDATE_PATTERN.test(candidate)) {
    fail('candidate must be an exact lowercase 40-character Git SHA or 64-character SHA-256 digest.');
  }

  const evidenceRef = validateText('evidence-ref', input['evidence-ref'], 512);
  if (isAbsolute(evidenceRef) || evidenceRef.includes('\\')) {
    fail('evidence-ref must be a portable workspace-relative path.');
  }
  const evidenceSegments = evidenceRef.split('/');
  if (
    evidenceSegments.length === 0 ||
    evidenceSegments.some(segment => segment === '' || segment === '.' || segment === '..' || !SAFE_EVIDENCE_SEGMENT.test(segment))
  ) {
    fail('evidence-ref contains an unsafe or invalid path segment.');
  }

  const outputValue = validateText('output', input.output, 4096);
  const output = resolve(outputValue);
  if (!OUTPUT_EXTENSIONS.has(extname(output).toLowerCase())) {
    fail('output must end in .json, .yaml, or .yml.');
  }
  const outputParent = dirname(output);
  if (!existsSync(outputParent) || !statSync(outputParent).isDirectory()) {
    fail('output parent directory must already exist.');
  }
  if (existsSync(output) && lstatSync(output).isSymbolicLink()) {
    fail('output may not be a symbolic link.');
  }

  return { objective, candidate, evidenceRef, output };
}

function stableJson(value) {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(',')}]`;
  if (value && typeof value === 'object') {
    return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

function missionDigest(input) {
  return createHash('sha256').update(stableJson(input)).digest('hex');
}

export function buildOracleWorkflow({ objective, candidate, evidenceRef }) {
  const digest = missionDigest({ objective, candidate, evidenceRef, topologyVersion: 2 });
  const validatorSteps = [
    ['oracle_strategic_validation', 'strategic_validator', 'Assess strategic fit, mission alignment, second-order effects, and operating priorities.'],
    ['oracle_financial_validation', 'financial_validator', 'Assess cost, value, resource constraints, financial exposure, and measurable return.'],
    ['oracle_legal_validation', 'legal_validator', 'Assess legal, contractual, privacy, compliance, and governance obligations.'],
    ['oracle_asset_ip_validation', 'asset_ip_validator', 'Assess ownership, provenance, intellectual property, data rights, and asset protection.'],
    ['oracle_technology_validation', 'technology_validator', 'Assess architecture, security, reliability, operability, and technical acceptance evidence.'],
  ];
  const validatorIds = validatorSteps.map(([id]) => id);

  return {
    workflow: {
      id: `oracle-mission-${digest.slice(0, 24)}`,
      version: `1-${digest.slice(0, 16)}`,
      objective,
      context_refs: [evidenceRef],
      target: { rig: 'carbon6-office' },
      entry: { role: 'oracle_chair' },
      coordination_terminal_turn_rule: 'hot_potato',
      exception_routing: { default: 'orchestrator', orchestrator_role: 'oracle_chair' },
      roles: {
        oracle_chair: { preferred_targets: ['oracle-chair@carbon6-office'] },
        strategic_validator: { preferred_targets: ['oracle-strategic-validator@carbon6-office'] },
        financial_validator: { preferred_targets: ['oracle-financial-validator@carbon6-office'] },
        legal_validator: { preferred_targets: ['oracle-legal-validator@carbon6-office'] },
        asset_ip_validator: { preferred_targets: ['oracle-asset-ip-validator@carbon6-office'] },
        technology_validator: { preferred_targets: ['oracle-technology-validator@carbon6-office'] },
        independent_verifier: { preferred_targets: ['delivery-verifier@carbon6-office'] },
      },
      steps: [
        {
          id: 'oracle_intake',
          actor_role: 'oracle_chair',
          objective: `Frame the mission, preserve the exact release candidate ${candidate}, and dispatch all five Oracle reviews without changing scope.`,
          allowed_exits: ['handoff', 'waiting', 'failed'],
        },
        ...validatorSteps.map(([id, actorRole, stepObjective]) => ({
          id,
          actor_role: actorRole,
          objective: `${stepObjective} Record a clear PASS, REJECT, or BLOCKED recommendation with evidence for candidate ${candidate}.`,
          allowed_exits: ['handoff', 'waiting', 'failed'],
          depends_on: ['oracle_intake'],
        })),
        {
          id: 'oracle_synthesis',
          actor_role: 'oracle_chair',
          objective: 'Synthesize all five validator records, resolve disagreements explicitly, and prepare one evidence-backed recommendation for independent acceptance.',
          allowed_exits: ['handoff', 'waiting', 'failed'],
          depends_on: validatorIds,
        },
        {
          id: 'independent_acceptance',
          actor_role: 'independent_verifier',
          objective: `Independently verify the synthesized decision against exact candidate ${candidate} and evidence ${evidenceRef}. Do not accept delivery, liveness, or unsupported claims as proof.`,
          allowed_exits: ['handoff', 'waiting', 'failed'],
          depends_on: ['oracle_synthesis'],
          acceptance: {
            candidate,
            verdicts: ['PASS'],
            evidence_ref: evidenceRef,
          },
        },
        {
          id: 'oracle_consolidation',
          actor_role: 'oracle_chair',
          objective: `Issue the final Oracle record for candidate ${candidate}, incorporating the independent verdict and citing ${evidenceRef}.`,
          allowed_exits: ['done', 'waiting', 'failed'],
          depends_on: ['independent_acceptance'],
          next_hop: { mode: 'forbid' },
        },
      ],
      invariants: {
        allowed_exits: ['handoff', 'waiting', 'done', 'failed'],
      },
      loop_guards: { max_hops: 20 },
    },
  };
}

function yamlScalar(value) {
  if (value === null) return 'null';
  if (typeof value === 'boolean' || typeof value === 'number') return String(value);
  return JSON.stringify(value);
}

function toYaml(value, indent = 0) {
  const prefix = ' '.repeat(indent);
  if (Array.isArray(value)) {
    return value.map(item => {
      if (item && typeof item === 'object') return `${prefix}-\n${toYaml(item, indent + 2)}`;
      return `${prefix}- ${yamlScalar(item)}`;
    }).join('\n');
  }
  return Object.entries(value).map(([key, item]) => {
    if (item && typeof item === 'object') return `${prefix}${key}:\n${toYaml(item, indent + 2)}`;
    return `${prefix}${key}: ${yamlScalar(item)}`;
  }).join('\n');
}

export function serializeWorkflow(workflow, outputPath) {
  return extname(outputPath).toLowerCase() === '.json'
    ? `${JSON.stringify(workflow, null, 2)}\n`
    : `${toYaml(workflow)}\n`;
}

export function writeWorkflowAtomic(outputPath, content) {
  const parent = dirname(outputPath);
  const temporary = resolve(parent, `.${basename(outputPath)}.${process.pid}.tmp`);
  let descriptor;
  try {
    descriptor = openSync(temporary, 'wx', 0o600);
    writeFileSync(descriptor, content, 'utf8');
    closeSync(descriptor);
    descriptor = undefined;
    renameSync(temporary, outputPath);
  } finally {
    if (descriptor !== undefined) closeSync(descriptor);
    rmSync(temporary, { force: true });
  }
}

export function run(argv) {
  const input = validateInputs(parseArguments(argv));
  const workflow = buildOracleWorkflow(input);
  writeWorkflowAtomic(input.output, serializeWorkflow(workflow, input.output));
  return { output: input.output, workflowId: workflow.workflow.id, version: workflow.workflow.version };
}

const invokedDirectly = process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href;
if (invokedDirectly) {
  try {
    const result = run(process.argv.slice(2));
    process.stdout.write(`${JSON.stringify(result)}\n`);
  } catch (error) {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    process.exitCode = 1;
  }
}

