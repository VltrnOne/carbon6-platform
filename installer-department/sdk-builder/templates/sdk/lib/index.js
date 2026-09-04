/**
 * SDK Main Entry Point
 */

class SDK {
  constructor(config = {}) {
    this.config = config;
    this.plugins = [];
    this.agents = new Map();
  }

  /**
   * Use a plugin
   */
  use(plugin) {
    if (typeof plugin.init === 'function') {
      plugin.init(this);
    }
    this.plugins.push(plugin);
    return this;
  }

  /**
   * Remove a plugin by name
   */
  remove(pluginName) {
    this.plugins = this.plugins.filter(plugin => plugin.name !== pluginName);
    return this;
  }

  /**
   * Update a plugin by name with new options
   */
  update(pluginName, options) {
    const plugin = this.plugins.find(plugin => plugin.name === pluginName);
    if (plugin) {
      Object.assign(plugin, options);
    }
    return this;
  }

  /**
   * Get SDK version
   */
  version() {
    return require('../package.json').version;
  }

  /**
   * Invoke an agent by ID with a payload
   */
  invokeAgent(agentId, payload) {
    const agent = this.agents.get(agentId);
    if (!agent) {
      throw new Error(`Agent ${agentId} not found`);
    }
    if (typeof agent.handle === 'function') {
      return agent.handle(payload);
    } else if (typeof agent.run === 'function') {
      return agent.run(payload);
    } else {
      throw new Error(`Agent ${agentId} does not have a handle or run method`);
    }
  }

  /**
   * List all agents
   */
  listAgents() {
    return Array.from(this.agents.keys());
  }
}

module.exports = SDK;
