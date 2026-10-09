const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');
const OpenRigAdapter = require('../lib/openrig-adapter');
const CommandParser = require('../lib/command-parser');

let dir;
let executable;
let env;
let report;

beforeEach(() => {
  dir = fs.mkdtempSync(path.join(os.tmpdir(), 'carbon-rig-test-'));
  executable = path.join(dir, 'rig');
  fs.writeFileSync(executable, `#!${process.execPath}
const fs = require('fs');
const args = process.argv.slice(2);
const read = flag => args[args.indexOf(flag) + 1];
const body = fs.readFileSync(0, 'utf8');
fs.writeFileSync(process.env.CALL_FILE, JSON.stringify({args, body}));
const id = read('--id');
if (process.env.MODE === 'refuse') { console.error('destination refused'); process.exit(1); }
if (process.env.MODE === 'malformed') { console.log('not JSON'); process.exit(0); }
if (process.env.MODE === 'mismatch') { console.log(JSON.stringify({qitemId:'other'})); process.exit(0); }
const db = fs.existsSync(process.env.DB_FILE) ? JSON.parse(fs.readFileSync(process.env.DB_FILE)) : {};
const entry = {args, body};
if (db[id] && JSON.stringify(db[id]) !== JSON.stringify(entry)) { console.error('request conflict'); process.exit(1); }
db[id] = entry;
fs.writeFileSync(process.env.DB_FILE, JSON.stringify(db));
if (process.env.MODE === 'lost-reply') { console.error('connection lost after commit'); process.exit(2); }
if (process.env.MODE === 'timeout') { setTimeout(() => {}, 5000); }
else console.log(JSON.stringify({qitemId:id, createWarning:process.env.MODE === 'warning' ? {code:'qitem_body_not_saved'} : undefined}));
`, { mode: 0o700 });
  env = { ...process.env, CARBON_OPENRIG_BIN: executable,
    CARBON_OPENRIG_SOURCE: 'operator@carbon6-office',
    CALL_FILE: path.join(dir, 'call.json'), DB_FILE: path.join(dir, 'db.json') };
  for (const key of ['OPENRIG_SESSION_NAME', 'RIGGED_SESSION_NAME', 'CARBON_OPENRIG_ROUTES',
    'CARBON_OPENRIG_DESTINATION', 'CARBON_OPENRIG_REQUEST_ID', 'MODE']) delete env[key];
  report = jest.fn();
});

afterEach(() => fs.rmSync(dir, { recursive: true, force: true }));

function adapter(extra = {}) { return new OpenRigAdapter({ env, report, ...extra }); }
const context = { command: 'techne', tier: 'L3-CONFIDENTIAL', requestId: 'carbon-test-1' };

test('dispatch preserves literal shell syntax through stdin and returns a queue receipt', async () => {
  const task = `Review $(touch ${dir}/injected) and \`uname\`\n--dangerously-interact; $HOME`;
  const result = await adapter().invokeAgent('TECHNE', task, context);
  const call = JSON.parse(fs.readFileSync(env.CALL_FILE));
  expect(call.args).toEqual(['queue', 'create', '--destination', 'delivery-builder@carbon6-office',
    '--body-file', '-', '--id', 'carbon-test-1', '--summary', 'Carbon6 techne', '--json', '--source', 'operator@carbon6-office']);
  expect(JSON.parse(call.body).instruction).toBe(task);
  expect(call.args).not.toContain(task);
  expect(fs.existsSync(path.join(dir, 'injected'))).toBe(false);
  expect(result.status).toBe('queued');
  expect(result.note).toContain('not confirmed');
  expect(report).toHaveBeenCalledWith(expect.stringContaining('persistence not yet confirmed'));
});

test('workflow routes to its owner while preserving canonical workflow intent', async () => {
  const p = new CommandParser(adapter());
  const result = await p.execute('/workflow.code-review Review the change', { requestId: 'review-1' });
  expect(result.success).toBe(true);
  expect(result.result.destination).toBe('delivery-verifier@carbon6-office');
  const body = JSON.parse(JSON.parse(fs.readFileSync(env.CALL_FILE)).body);
  expect(body.agentId).toBe('WORKFLOW_CODE_REVIEW');
  expect(body.kind).toBe('workflow-request');
});

test('parser preserves multiline payloads and resolves existing aliases', () => {
  const p = new CommandParser(adapter());
  const [alias, canonical] = Object.entries(p.registry.aliases)[0];
  const parsed = p.parse(`/${alias} First line\n  Second line with  spaces`);
  expect(parsed.command).toBe(canonical);
  expect(parsed.args).toBe('First line\n  Second line with  spaces');
});

test('managed source wins and declared source is not forwarded', async () => {
  env.OPENRIG_SESSION_NAME = 'delivery-builder@carbon6-office';
  await adapter().invokeAgent('TECHNE', 'Review', context);
  expect(JSON.parse(fs.readFileSync(env.CALL_FILE)).args).not.toContain('--source');
});

test('unmanaged caller must supply an honest declared source', async () => {
  delete env.CARBON_OPENRIG_SOURCE;
  await expect(adapter().invokeAgent('TECHNE', 'Review', context)).rejects.toThrow('declared source');
  expect(fs.existsSync(env.CALL_FILE)).toBe(false);
});

test('unmapped commands fail unless an explicit destination is selected', async () => {
  await expect(adapter().invokeAgent('LLM_UNKNOWN', 'Review', context)).rejects.toThrow('No valid OpenRig seat mapping');
  env.CARBON_OPENRIG_DESTINATION = 'command-lead@carbon6-office@remote';
  expect((await adapter().invokeAgent('LLM_UNKNOWN', 'Review', context)).destination).toBe(env.CARBON_OPENRIG_DESTINATION);
});

test('custom route files override shipped mappings', async () => {
  env.CARBON_OPENRIG_ROUTES = path.join(dir, 'routes.json');
  fs.writeFileSync(env.CARBON_OPENRIG_ROUTES, JSON.stringify({ agents: { TECHNE: 'reviewer@other' } }));
  expect((await adapter().invokeAgent('TECHNE', 'Review', context)).destination).toBe('reviewer@other');
});

test.each(['refuse', 'malformed', 'mismatch', 'warning'])('%s does not produce a success receipt or auto retry', async mode => {
  env.MODE = mode;
  await expect(adapter().invokeAgent('TECHNE', 'Review', context)).rejects.toThrow('OpenRig dispatch not confirmed');
  expect(report).toHaveBeenCalledTimes(1);
});

test('lost response preserves retry identity and does not duplicate durable work', async () => {
  env.MODE = 'lost-reply';
  await expect(adapter().invokeAgent('TECHNE', 'Review', context)).rejects.toThrow('carbon-test-1');
  expect(Object.keys(JSON.parse(fs.readFileSync(env.DB_FILE)))).toHaveLength(1);
  delete env.MODE;
  await adapter().invokeAgent('TECHNE', 'Review', context);
  expect(Object.keys(JSON.parse(fs.readFileSync(env.DB_FILE)))).toHaveLength(1);
  await expect(adapter().invokeAgent('TECHNE', 'Changed task', context)).rejects.toThrow('request conflict');
});

test('timeout gives an unknown-outcome recovery identity', async () => {
  env.MODE = 'timeout';
  await expect(adapter({ timeout: 150 }).invokeAgent('TECHNE', 'Review', context)).rejects.toThrow('Retry only with this ID');
});

test('missing rig executable is explicit', async () => {
  await expect(adapter({ executable: path.join(dir, 'missing') }).invokeAgent('TECHNE', 'Review', context)).rejects.toThrow('ENOENT');
});

test.each(['', '   '])('empty task rejected before calling rig', async task => {
  await expect(adapter().invokeAgent('TECHNE', task, context)).rejects.toThrow('nonempty task');
  expect(fs.existsSync(env.CALL_FILE)).toBe(false);
});

test('invalid request IDs and malformed route configuration fail locally', async () => {
  await expect(adapter().invokeAgent('TECHNE', 'Review', { ...context, requestId: '--help' })).rejects.toThrow('Invalid OpenRig request ID');
  env.CARBON_OPENRIG_ROUTES = path.join(dir, 'absent.json');
  await expect(adapter().invokeAgent('TECHNE', 'Review', context)).rejects.toThrow('Cannot read OpenRig routes');
});

test('CLI exec and direct modes emit receipts and failure exit codes', () => {
  const cli = path.resolve(__dirname, '../bin/slash');
  let result = spawnSync(process.execPath, [cli, 'exec', '--request-id', 'cli-1', '/techne', 'Review'], { env, encoding: 'utf8' });
  expect(result.status).toBe(0);
  expect(result.stdout).toContain('"status": "queued"');
  env.CARBON_OPENRIG_REQUEST_ID = 'cli-2';
  result = spawnSync(process.execPath, [cli, '/techne', 'Review'], { env, encoding: 'utf8' });
  expect(result.status).toBe(0);
  env.MODE = 'refuse';
  for (const args of [['exec', '/techne', 'Review'], ['/techne', 'Review'], ['/missing', 'Review']]) {
    result = spawnSync(process.execPath, [cli, ...args], { env, encoding: 'utf8' });
    expect(result.status).toBe(1);
  }
});

test('SSH transport preserves stdin and runs the remote rig without shell-interpolating the task', async () => {
  const fakeSsh = path.join(dir, 'ssh');
  const sshCall = path.join(dir, 'ssh-call.json');
  fs.writeFileSync(fakeSsh, `#!${process.execPath}
const fs = require('fs');
const stdin = fs.readFileSync(0, 'utf8');
fs.writeFileSync(process.env.SSH_CALL_FILE, JSON.stringify({args:process.argv.slice(2), stdin}));
const body = JSON.parse(stdin);
console.log(JSON.stringify({qitemId:body.requestId}));
`, { mode: 0o700 });
  env.CARBON_OPENRIG_BIN = path.resolve(__dirname, '../bin/rig-ssh');
  env.CARBON_OPENRIG_SSH_BIN = fakeSsh;
  env.CARBON_OPENRIG_SSH_TARGET = 'vltrn-brain';
  env.CARBON_OPENRIG_DESTINATION = 'command-lead@carbon6-office';
  env.SSH_CALL_FILE = sshCall;
  const task = 'Audit $(touch /tmp/never) and `uname`';
  const result = await adapter().invokeAgent('GENESIS', task, { command: 'genesis', requestId: 'ssh-1' });
  const call = JSON.parse(fs.readFileSync(sshCall));
  expect(call.args).toEqual(expect.arrayContaining(['-o', 'BatchMode=yes', 'vltrn-brain']));
  expect(call.args.join(' ')).not.toContain(task);
  expect(JSON.parse(call.stdin).instruction).toBe(task);
  expect(result.destination).toBe('command-lead@carbon6-office');
});
