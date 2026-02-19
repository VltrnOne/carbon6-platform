/**
 * VLTRN Council Slash Command Parser
 * Routes slash commands to appropriate agents
 */

const registry = require('../command-registry.json');
const chalk = require('chalk');

class CommandParser {
  constructor() {
    this.registry = registry;
    this.commandMap = this.buildCommandMap();
    this.aliasMap = this.buildAliasMap();
  }

  /**
   * Build flat command map from registry
   */
  buildCommandMap() {
    const map = new Map();

    // Add all tier commands
    Object.entries(this.registry.tiers).forEach(([tierKey, tier]) => {
      Object.entries(tier.commands).forEach(([command, config]) => {
        map.set(command, {
          ...config,
          tier: tier.clearance
        });
      });
    });

    // Add workflow commands
    Object.entries(this.registry.workflows).forEach(([category, workflows]) => {
      workflows.forEach(workflow => {
        map.set(`workflow.${workflow}`, {
          agent: `WORKFLOW_${workflow.toUpperCase().replace(/-/g, '_')}`,
          description: `Execute ${workflow} workflow`,
          tier: 'L3-CONFIDENTIAL',
          category
        });
      });
    });

    // Add NVIDIA commands
    Object.entries(this.registry.nvidia).forEach(([backend, description]) => {
      map.set(`nvidia.${backend}`, {
        agent: `NVIDIA_${backend.toUpperCase()}`,
        description,
        tier: 'L3-CONFIDENTIAL',
        backend
      });
    });

    // Add LLM commands
    Object.entries(this.registry.llm).forEach(([provider, description]) => {
      map.set(`llm.${provider}`, {
        agent: `LLM_${provider.toUpperCase()}`,
        description,
        tier: 'L3-CONFIDENTIAL',
        provider
      });
    });

    // Add Oracle commands
    Object.entries(this.registry.oracle).forEach(([validator, description]) => {
      map.set(`oracle.${validator}`, {
        agent: `ORACLE_${validator.toUpperCase()}`,
        description,
        tier: 'L4-RESTRICTED',
        validator
      });
    });

    return map;
  }

  /**
   * Build alias map
   */
  buildAliasMap() {
    const map = new Map();
    Object.entries(this.registry.aliases).forEach(([alias, command]) => {
      map.set(alias, command);
    });
    return map;
  }

  /**
   * Parse slash command
   * @param {string} input - Command string (e.g., "/aurum analyze Q4 P&L")
   * @returns {Object} Parsed command
   */
  parse(input) {
    // Remove leading slash if present
    const cleanInput = input.startsWith('/') ? input.slice(1) : input;

    // Split command and arguments
    const parts = cleanInput.split(/\s+/);
    const commandPart = parts[0];
    const args = parts.slice(1).join(' ');

    // Check for alias
    const resolvedCommand = this.aliasMap.get(commandPart) || commandPart;

    // Look up command in registry
    const commandConfig = this.commandMap.get(resolvedCommand);

    if (!commandConfig) {
      return {
        valid: false,
        error: `Unknown command: ${commandPart}`,
        suggestions: this.getSuggestions(commandPart)
      };
    }

    return {
      valid: true,
      command: resolvedCommand,
      originalCommand: commandPart,
      agent: commandConfig.agent,
      description: commandConfig.description,
      tier: commandConfig.tier,
      args,
      config: commandConfig
    };
  }

  /**
   * Get command suggestions based on partial input
   * @param {string} partial - Partial command
   * @returns {Array} Suggested commands
   */
  getSuggestions(partial) {
    const suggestions = [];

    // Check aliases
    for (const [alias, command] of this.aliasMap.entries()) {
      if (alias.startsWith(partial) || command.startsWith(partial)) {
        suggestions.push({
          command: alias,
          resolves: command,
          type: 'alias'
        });
      }
    }

    // Check direct commands
    for (const [command, config] of this.commandMap.entries()) {
      if (command.startsWith(partial)) {
        suggestions.push({
          command,
          agent: config.agent,
          description: config.description,
          type: 'command'
        });
      }
    }

    return suggestions.slice(0, 5); // Limit to 5 suggestions
  }

  /**
   * List all commands
   * @param {Object} options - Filtering options
   * @returns {Array} Commands
   */
  listCommands(options = {}) {
    const { tier, domain, search } = options;
    const commands = [];

    for (const [command, config] of this.commandMap.entries()) {
      // Apply filters
      if (tier && config.tier !== tier) continue;
      if (domain && config.domain !== domain) continue;
      if (search && !command.includes(search) && !config.description.toLowerCase().includes(search.toLowerCase())) continue;

      commands.push({
        command,
        ...config
      });
    }

    return commands;
  }

  /**
   * Get command info
   * @param {string} command - Command name
   * @returns {Object} Command info
   */
  getInfo(command) {
    const resolvedCommand = this.aliasMap.get(command) || command;
    const config = this.commandMap.get(resolvedCommand);

    if (!config) {
      return null;
    }

    // Find aliases for this command
    const aliases = [];
    for (const [alias, target] of this.aliasMap.entries()) {
      if (target === resolvedCommand) {
        aliases.push(alias);
      }
    }

    return {
      command: resolvedCommand,
      ...config,
      aliases
    };
  }

  /**
   * Execute command
   * @param {string} input - Full command input
   * @returns {Promise} Execution result
   */
  async execute(input) {
    const parsed = this.parse(input);

    if (!parsed.valid) {
      console.error(chalk.red(`Error: ${parsed.error}`));

      if (parsed.suggestions.length > 0) {
        console.log(chalk.gray('\nDid you mean:'));
        parsed.suggestions.forEach(suggestion => {
          console.log(chalk.blue(`  /${suggestion.command}`) + chalk.gray(` - ${suggestion.description || ''}`));
        });
      }

      return {
        success: false,
        error: parsed.error
      };
    }

    console.log(chalk.blue(`\n╔═══════════════════════════════════════════════════════════╗`));
    console.log(chalk.blue(`║`) + chalk.white(`  Invoking: ${parsed.agent}`.padEnd(57)) + chalk.blue(`║`));
    console.log(chalk.blue(`║`) + chalk.gray(`  Tier: ${parsed.tier}`.padEnd(57)) + chalk.blue(`║`));
    console.log(chalk.blue(`╚═══════════════════════════════════════════════════════════╝\n`));

    // TODO: Actual agent invocation via OiS or Council API
    // For now, return placeholder
    return {
      success: true,
      agent: parsed.agent,
      command: parsed.command,
      args: parsed.args,
      tier: parsed.tier,
      message: `Command would be executed: ${parsed.agent} - ${parsed.args}`
    };
  }

  /**
   * Display help
   * @param {string} topic - Optional help topic
   */
  displayHelp(topic = null) {
    if (!topic) {
      console.log(chalk.blue(`\n╔═══════════════════════════════════════════════════════════╗`));
      console.log(chalk.blue(`║                                                           ║`));
      console.log(chalk.blue(`║`) + chalk.white(`     VLTRN COUNCIL SLASH COMMANDS`.padEnd(57)) + chalk.blue(`║`));
      console.log(chalk.blue(`║                                                           ║`));
      console.log(chalk.blue(`║`) + chalk.gray(`     462 Agents × 172 Workflows × 12 NVIDIA Backends`.padEnd(57)) + chalk.blue(`║`));
      console.log(chalk.blue(`║                                                           ║`));
      console.log(chalk.blue(`╚═══════════════════════════════════════════════════════════╝\n`));

      console.log(chalk.white('Usage:'));
      console.log(chalk.gray('  /command <task>              Execute command'));
      console.log(chalk.gray('  /agent.subagent <task>       Invoke sub-agent'));
      console.log(chalk.gray('  /workflow.name               Execute workflow'));
      console.log(chalk.gray('  /nvidia.backend <task>       Use NVIDIA backend'));
      console.log(chalk.gray('  /llm.provider <task>         Route to LLM provider\n'));

      console.log(chalk.white('Common Commands:'));
      console.log(chalk.blue('  /genesis') + chalk.gray(' <task>             Divine Orchestrator'));
      console.log(chalk.blue('  /aurum') + chalk.gray(' <task>               Finance & Treasury'));
      console.log(chalk.blue('  /techne') + chalk.gray(' <task>              Technology & Development'));
      console.log(chalk.blue('  /sophia') + chalk.gray(' <task>              Research & Intelligence'));
      console.log(chalk.blue('  /mercator') + chalk.gray(' <task>            Marketing & Growth'));
      console.log(chalk.blue('  /aegis') + chalk.gray(' <task>               Security Guardian\n'));

      console.log(chalk.white('Help Topics:'));
      console.log(chalk.gray('  /help tier0                  Tier 0 commands (L5-BLACK)'));
      console.log(chalk.gray('  /help tier1                  Tier 1 commands (L4-RESTRICTED)'));
      console.log(chalk.gray('  /help tier2                  Tier 2 commands (L3-CONFIDENTIAL)'));
      console.log(chalk.gray('  /help workflows              Available workflows'));
      console.log(chalk.gray('  /help nvidia                 NVIDIA backends'));
      console.log(chalk.gray('  /help llm                    LLM providers\n'));

    } else {
      // Topic-specific help
      const tier = this.registry.tiers[topic];
      if (tier) {
        console.log(chalk.blue(`\n${topic.toUpperCase()} - ${tier.clearance}\n`));
        Object.entries(tier.commands).forEach(([command, config]) => {
          console.log(chalk.blue(`  /${command}`) + chalk.gray(` - ${config.description}`));
          if (config.subAgents) {
            console.log(chalk.gray(`    Sub-agents: ${Array.isArray(config.subAgents) ? config.subAgents.join(', ') : `${config.subAgents} total`}`));
          }
        });
      }
    }
  }

  /**
   * Get statistics
   * @returns {Object} Statistics
   */
  getStats() {
    const stats = {
      totalCommands: this.commandMap.size,
      totalAliases: this.aliasMap.size,
      byTier: {},
      workflows: Object.keys(this.registry.workflows).length,
      nvidiaBackends: Object.keys(this.registry.nvidia).length,
      llmProviders: Object.keys(this.registry.llm).length
    };

    // Count by tier
    for (const [command, config] of this.commandMap.entries()) {
      const tier = config.tier || 'unknown';
      stats.byTier[tier] = (stats.byTier[tier] || 0) + 1;
    }

    return stats;
  }
}

module.exports = CommandParser;
