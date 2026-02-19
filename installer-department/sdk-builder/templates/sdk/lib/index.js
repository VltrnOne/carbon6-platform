/**
 * SDK Main Entry Point
 */

class SDK {
  constructor(config = {}) {
    this.config = config;
    this.plugins = [];
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
   * Get SDK version
   */
  version() {
    return require('../package.json').version;
  }
}

module.exports = SDK;
