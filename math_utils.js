const math = require('mathjs');

/**
 * Get factorial of a number using math.factorial
 * @param {number} n - The number to compute the factorial for
 * @returns {number} Factorial of the number
 */
function get_factorial(n) {
  return math.factorial(n);
}

module.exports = {
  get_factorial
};
