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
  if (seats.length !== 6 || !seats.includes('command-lead@carbon6-office')) throw new Error('Unexpected topology cardinality or lead address');
  console.log(JSON.stringify({ valid: true, openrig_version: pkg.version, seats, launches: 0, scope: 'official schema, AgentSpec resolution, profiles, required files and cwd existence' }, null, 2));
} catch (err) { console.error(err.message); process.exitCode = 1; }
