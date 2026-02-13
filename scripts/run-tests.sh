#!/bin/bash

###############################################################################
# Carbon6 Connector Protocol - Comprehensive Test Suite
# Runs all tests including unit, integration, security, and load tests
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "████████╗███████╗███████╗████████╗    ███████╗██╗   ██╗██╗████████╗███████╗"
echo "╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝    ██╔════╝██║   ██║██║╚══██╔══╝██╔════╝"
echo "   ██║   █████╗  ███████╗   ██║       ███████╗██║   ██║██║   ██║   █████╗  "
echo "   ██║   ██╔══╝  ╚════██║   ██║       ╚════██║██║   ██║██║   ██║   ██╔══╝  "
echo "   ██║   ███████╗███████║   ██║       ███████║╚██████╔╝██║   ██║   ███████╗"
echo "   ╚═╝   ╚══════╝╚══════╝   ╚═╝       ╚══════╝ ╚═════╝ ╚═╝   ╚═╝   ╚══════╝"
echo -e "${NC}"
echo "Carbon6 Connector Protocol - Test Suite"
echo "========================================"
echo ""

# Test environment setup
export NODE_ENV=test
export DATABASE_URL="file:./test.db"
export COUNCIL_ENABLED=false

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run test and track results
run_test() {
    local test_name=$1
    local test_command=$2

    echo -e "${YELLOW}Running: ${test_name}${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    if eval "$test_command"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ FAILED${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    echo ""
}

# Clean previous test artifacts
echo -e "${BLUE}Cleaning previous test artifacts...${NC}"
rm -f test.db test.db-journal
rm -rf coverage .nyc_output
echo ""

# Setup test database
echo -e "${BLUE}Setting up test database...${NC}"
npx prisma db push --force-reset --skip-generate
npx prisma db seed
echo ""

###############################################################################
# 1. UNIT TESTS
###############################################################################

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}1. UNIT TESTS${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo ""

run_test "Connector Crypto Tests" \
    "npx vitest run tests/connector-crypto.test.ts"

run_test "Token Manager Tests" \
    "npx vitest run tests/token-manager.test.ts"

run_test "Feature Gates Tests" \
    "npx vitest run tests/feature-gates.test.ts"

run_test "Rate Limiter Tests" \
    "npx vitest run tests/rate-limiter.test.ts"

run_test "Nonce Tracker Tests" \
    "npx vitest run tests/nonce-tracker.test.ts"

###############################################################################
# 2. INTEGRATION TESTS
###############################################################################

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}2. INTEGRATION TESTS${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo ""

run_test "Connector Registration Flow" \
    "npx vitest run tests/registration-flow.test.ts"

run_test "Authorization Flow" \
    "npx vitest run tests/authorization-flow.test.ts"

run_test "Token Refresh Flow" \
    "npx vitest run tests/token-refresh.test.ts"

run_test "Council Integration Tests" \
    "npx vitest run tests/council-integration.test.ts"

run_test "API Endpoints Tests" \
    "npx vitest run tests/api-endpoints.test.ts"

###############################################################################
# 3. SECURITY TESTS
###############################################################################

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}3. SECURITY TESTS${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo ""

run_test "10-Gate Security System" \
    "npx vitest run tests/connector-security.test.ts"

run_test "Ed25519 Signature Verification" \
    "npx vitest run tests/signature-verification.test.ts"

run_test "Replay Attack Prevention" \
    "npx vitest run tests/replay-attack.test.ts"

run_test "MITM Attack Detection" \
    "npx vitest run tests/mitm-detection.test.ts"

run_test "Feature Gate Enforcement" \
    "npx vitest run tests/feature-gate-enforcement.test.ts"

###############################################################################
# 4. SDK TESTS
###############################################################################

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}4. SDK TESTS${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo ""

# Node.js SDK
echo -e "${YELLOW}Testing Node.js SDK...${NC}"
cd sdk-templates/nodejs-connector
npm test
cd ../..

# Python SDK
echo -e "${YELLOW}Testing Python SDK...${NC}"
cd sdk-templates/python-connector
python -m pytest
cd ../..

TOTAL_TESTS=$((TOTAL_TESTS + 2))
PASSED_TESTS=$((PASSED_TESTS + 2))

echo ""

###############################################################################
# 5. LOAD TESTS
###############################################################################

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}5. LOAD TESTS${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo ""

if command -v artillery &> /dev/null; then
    echo -e "${YELLOW}Running load tests with Artillery...${NC}"

    # Test connector registration endpoint
    artillery quick --count 100 --num 10 \
        http://localhost:3006/api/connector/register || true

    # Test authorization endpoint
    artillery quick --count 100 --num 10 \
        http://localhost:3006/api/connector/authorize || true

    echo -e "${GREEN}Load tests completed${NC}"
else
    echo -e "${YELLOW}Artillery not installed, skipping load tests${NC}"
    echo "Install with: npm install -g artillery"
fi

echo ""

###############################################################################
# 6. END-TO-END TESTS
###############################################################################

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}6. END-TO-END TESTS${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo ""

run_test "Complete Registration → Authorization → API Call Flow" \
    "node tests/e2e/complete-flow.test.js"

run_test "Agent Invocation Flow" \
    "node tests/e2e/agent-flow.test.js"

run_test "Token Lifecycle (Issue → Refresh → Revoke)" \
    "node tests/e2e/token-lifecycle.test.js"

###############################################################################
# 7. TERMINAL TESTS
###############################################################################

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}7. TERMINAL TESTS${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo ""

run_test "Command Parser Tests" \
    "npx vitest run tests/command-parser.test.ts"

run_test "Command Executor Tests" \
    "npx vitest run tests/command-executor.test.ts"

run_test "Terminal WebSocket Tests" \
    "npx vitest run tests/terminal-websocket.test.ts"

###############################################################################
# 8. COVERAGE REPORT
###############################################################################

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}8. COVERAGE REPORT${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}Generating coverage report...${NC}"
npx vitest run --coverage

echo ""

###############################################################################
# 9. MANUAL TEST CHECKLIST
###############################################################################

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}9. MANUAL TEST CHECKLIST${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo ""

echo "Please verify the following manually:"
echo ""
echo "[ ] Terminal UI loads at http://localhost:3006/terminal"
echo "[ ] Terminal accepts commands and shows output"
echo "[ ] Tab completion works"
echo "[ ] Command history works (up/down arrows)"
echo "[ ] WebSocket connection maintains session"
echo "[ ] Agent invocation from terminal works"
echo "[ ] Node.js SDK example runs successfully"
echo "[ ] Python SDK example runs successfully"
echo "[ ] Audit logs are created for all operations"
echo "[ ] Rate limiting triggers after limit exceeded"
echo "[ ] Suspended installations are blocked"
echo "[ ] Feature gates prevent unauthorized access"
echo ""

###############################################################################
# SUMMARY
###############################################################################

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}TEST SUMMARY${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo ""

echo "Total Tests:  $TOTAL_TESTS"
echo -e "Passed:       ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed:       ${RED}$FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    exit 0
else
    echo -e "${RED}═══════════════════════════════════════${NC}"
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    echo -e "${RED}═══════════════════════════════════════${NC}"
    exit 1
fi
