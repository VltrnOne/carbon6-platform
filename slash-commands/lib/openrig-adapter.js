/** Durable Carbon6 dispatch through the installed OpenRig CLI. */
const fs = require('fs');
const path = require('path');
const { randomUUID } = require('crypto');
const { execFile } = require('child_process');

const DEFAULT_ROUTES = path.join(__dirname, '../openrig-routes.json');
const ADDRESS = /^[A-Za-z0-9_.-]+@[A-Za-z0-9_.-]+(?:@[A-Za-z0-9_.-]+)?$/;
const REQUEST_ID = /^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$/;

function runRig(executable, args, body, { env, timeout }) {
  return new Promise((resolve, reject) => {
    let inputError;
    const child = execFile(executable, args, {
      env, timeout, maxBuffer: 1024 * 1024, encoding: 'utf8', shell: false
    }, (error, stdout, stderr) => {
      if (error || inputError) {
        const cause = error || inputError;
        reject(new Error(`${cause.message}${stderr ? `; ${stderr.trim().slice(0, 1000)}` : ''}`));
      } else {
        resolve(stdout);
      }
    });
    child.stdin.on('error', error => { inputError = error; });
    child.stdin.end(body);
  });
}

class OpenRigAdapter {
  constructor(options = {}) {
    this.env = options.env || process.env;
    this.executable = options.executable || this.env.CARBON_OPENRIG_BIN || 'rig';
    this.routesPath = options.routesPath || this.env.CARBON_OPENRIG_ROUTES || DEFAULT_ROUTES;
    this.transport = options.transport || runRig;
    this.timeout = options.timeout || 30000;
    this.report = options.report || (message => console.error(message));
  }

  async invokeAgent(agentId, payload, context = {}) {
    // Configuration is read only on execution: listing/help works without a daemon.
    let routes;
    try {
      routes = JSON.parse(fs.readFileSync(this.routesPath, 'utf8'));
    } catch (error) {
      throw new Error(`Cannot read OpenRig routes ${this.routesPath}: ${error.message}`);
    }
    const workflow = context.command?.startsWith('workflow.') ? context.command.slice(9) : null;
    const destination = this.env.CARBON_OPENRIG_DESTINATION || (workflow
      ? routes.workflows?.[workflow] : routes.agents?.[agentId]);
    if (typeof destination !== 'string' || !ADDRESS.test(destination)) {
      throw new Error(`No valid OpenRig seat mapping for ${context.command || agentId}. Configure CARBON_OPENRIG_ROUTES or CARBON_OPENRIG_DESTINATION (seat@rig).`);
    }
    const managed = this.env.OPENRIG_SESSION_NAME || this.env.RIGGED_SESSION_NAME;
    const source = this.env.CARBON_OPENRIG_SOURCE;
    if (!managed && (!source || !ADDRESS.test(source))) {
      throw new Error('Outside an OpenRig seat, set CARBON_OPENRIG_SOURCE to a declared source (seat@rig). This does not authenticate a managed seat.');
    }
    if (typeof payload !== 'string' || !payload.trim()) {
      throw new Error('A nonempty task is required for OpenRig dispatch.');
    }
    const requestId = context.requestId || this.env.CARBON_OPENRIG_REQUEST_ID || `carbon-${randomUUID()}`;
    if (!REQUEST_ID.test(requestId)) throw new Error('Invalid OpenRig request ID (1–128 letters, digits, dots, underscores or hyphens).');
    // No timestamps: retrying the same identity must reproduce the same body.
    const body = JSON.stringify({
      schema: 'carbon6.slash-dispatch.v1', requestId,
      command: context.command || null, agentId,
      kind: workflow ? 'workflow-request' : 'agent-request',
      registryTier: context.tier || null,
      instruction: payload,
      authority: 'Registry labels are routing metadata, not permission grants. Use the seat\'s existing authority. Report execution and acceptance separately from queue persistence.'
    });
    if (Buffer.byteLength(body, 'utf8') > 128 * 1024) throw new Error('Task exceeds the 128 KiB dispatch limit.');
    const args = ['queue', 'create', '--destination', destination, '--body-file', '-',
      '--id', requestId, '--summary', `Carbon6 ${context.command || agentId}`, '--json'];
    if (!managed) args.push('--source', source);
    const recovery = `Request ID ${requestId}; reconcile with rig queue show ${requestId} --full --json at the same destination host/endpoint. Retry only with this ID and unchanged task, routing and source.`;
    this.report(`${recovery} Request allocated; persistence not yet confirmed.`);
    let receipt;
    try {
      const stdout = await this.transport(this.executable, args, body, { env: this.env, timeout: this.timeout });
      receipt = JSON.parse(stdout);
      if (!receipt || receipt.error || receipt.ok === false || receipt.qitemId !== requestId || receipt.createWarning) {
        throw new Error(`OpenRig did not confirm an intact queue item: ${JSON.stringify(receipt).slice(0, 1000)}`);
      }
    } catch (error) {
      // A failed process/timeout/malformed reply may follow a committed create.
      // Never automatically resend or allocate a replacement ID.
      throw new Error(`OpenRig dispatch not confirmed: ${error.message}. ${recovery}`);
    }
    return { status: 'queued', requestId, destination, receipt,
      note: 'Queue persistence confirmed. Worker execution and acceptance are not confirmed.' };
  }
}

module.exports = OpenRigAdapter;
