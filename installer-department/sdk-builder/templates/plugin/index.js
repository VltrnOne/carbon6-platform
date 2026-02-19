/**
 * Plugin Entry Point
 */

module.exports = {
  name: 'my-plugin',
  version: '1.0.0',

  /**
   * Initialize plugin
   * @param {Object} sdk - Parent SDK instance
   */
  init: (sdk) => {
    console.log('Plugin initialized!');

    // Add plugin functionality to SDK
    sdk.myPluginMethod = () => {
      console.log('Plugin method called!');
    };
  }
};
