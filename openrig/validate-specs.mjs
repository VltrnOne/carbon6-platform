#!/usr/bin/env node
// Pure validation against the installed official 0.6.7 validators; no daemon.
import { readFileSync, existsSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const root = dirname(fileURLToPath(import.meta.url));
try {
  const cliRoot = process.argv[2];
  if (!cliRoot || process.argv.length !== 3) throw new Error('Usage: node openrig/validate-specs.mjs OPENRIG_CLI_ROOT');
  const pkg = JSON.parse(readFileSync(resolve(cliRoot, 'package.json'), 'utf8'));
  if (pkg.name !== '@openrig/cli' || pkg.version !== '0.6.7') throw new Error('Expected inspected @openrig/cli 0.6.7. Revalidate compatibility before upgrading.');
  const require = createRequire(resolve(cliRoot, 'package.json'));
  const { parse } = require('yaml');
  const { validateRigSpecImport, validateAgentSpecFromYaml } = await import(pathToFileURL(resolve(cliRoot, 'daemon/dist/spec-validation-surface.js')).href);
  const { resolveAgentRef } = await import(pathToFileURL(resolve(cliRoot, 'daemon/dist/domain/agent-resolver.js')).href);
  const yaml = readFileSync(resolve(root, 'rig.yaml'), 'utf8');
  const result = validateRigSpecImport(yaml);
  if (!result.valid) throw new Error(JSON.stringify(result));
  const rig = parse(yaml);
  const oraclePod = rig.pods.find(pod => pod.id === 'oracle');
  const oracleFragment = parse(readFileSync(resolve(root, 'oracle-pod.fragment.yaml'), 'utf8'));
  const expansionPod = oraclePod && {
    id: oraclePod.id,
    label: oraclePod.label,
    members: oraclePod.members,
    edges: oraclePod.edges
  };
  const oracleCrossPodEdges = rig.edges.filter(edge => edge.from.startsWith('oracle.') || edge.to.startsWith('oracle.'));
  if (!oraclePod || JSON.stringify(expansionPod) !== JSON.stringify(oracleFragment.pod)
      || JSON.stringify(oracleCrossPodEdges) !== JSON.stringify(oracleFragment.crossPodEdges)) {
    throw new Error('Oracle live-expansion fragment does not match the supported Oracle pod and cross-pod fields');
  }
  if (!existsSync(resolve(root, 'workflows/oracle-supervision.workflow.yaml'))) {
    throw new Error('Missing Oracle supervision workflow');
  }
  const checkFiles = (block, base) => {
    for (const file of block?.files ?? []) if (!existsSync(resolve(base, file.path))) throw new Error(`Missing startup file: ${file.path}`);
  };
  if (!existsSync(resolve(root, rig.culture_file))) throw new Error('Missing culture file');
  checkFiles(rig.startup, root);
  const seats = [];
  for (const pod of rig.pods) {
    checkFiles(pod.startup, root);
    for (const member of pod.members) {
      const agent = resolve(root, member.agent_ref.replace(/^local:/, ''));
      const agentYaml = readFileSync(resolve(agent, 'agent.yaml'), 'utf8');
      const valid = validateAgentSpecFromYaml(agentYaml);
      if (!valid.valid) throw new Error(`${member.id}: ${JSON.stringify(valid)}`);
      const resolution = resolveAgentRef(member.agent_ref, root, { exists: existsSync, readFile: path => readFileSync(path, 'utf8') });
      if (!resolution.ok) throw new Error(`${member.id}: ${JSON.stringify(resolution)}`);
      const spec = parse(agentYaml);
      if (!spec.profiles[member.profile]) throw new Error(`Missing profile for ${member.id}`);
      checkFiles(spec.startup, agent);
      checkFiles(member.startup, root);
      if (!existsSync(resolve(root, member.cwd))) throw new Error(`Missing cwd for ${member.id}`);
      seats.push(`${pod.id}-${member.id}@${rig.name}`);
    }
  }
  const requiredSeats = [
    'oracle-chair@carbon6-office',
    'oracle-strategic-validator@carbon6-office',
    'oracle-financial-validator@carbon6-office',
    'oracle-legal-validator@carbon6-office',
    'oracle-asset-ip-validator@carbon6-office',
    'oracle-technology-validator@carbon6-office',
    'command-lead@carbon6-office',
    'command-continuity@carbon6-office',
    'office-front@carbon6-office',
    'office-back@carbon6-office',
    'delivery-builder@carbon6-office',
    'delivery-verifier@carbon6-office'
  ];
  if (seats.length !== requiredSeats.length || requiredSeats.some(seat => !seats.includes(seat))) {
    throw new Error('Unexpected topology cardinality or required seat address');
  }
  console.log(JSON.stringify({ valid: true, openrig_version: pkg.version, seats, launches: 0, scope: 'official schema, AgentSpec resolution, profiles, required files, cwd existence and supported Oracle expansion fragment parity' }, null, 2));
} catch (err) { console.error(err.message); process.exitCode = 1; }
