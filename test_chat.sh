#!/bin/bash

# Test script for TCP Chat Server
# This script helps verify all functionality

echo "================================"
echo "TCP Chat Server - Test Suite"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if server is running
echo -e "${YELLOW}[1] Checking if server is running...${NC}"
nc -z localhost 4000 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Server is running on port 4000${NC}"
else
    echo -e "${RED}✗ Server is not running!${NC}"
    echo "Start the server with: python3 server.py"
    exit 1
fi
echo ""

# Test 1: Basic Login
echo -e "${YELLOW}[2] Testing basic login...${NC}"
(echo "LOGIN TestUser1"; sleep 1) | nc localhost 4000 | grep -q "OK"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Login successful${NC}"
else
    echo -e "${RED}✗ Login failed${NC}"
fi
echo ""

# Test 2: Duplicate username
echo -e "${YELLOW}[3] Testing duplicate username rejection...${NC}"
{
    (echo "LOGIN Alice"; sleep 30) | nc localhost 4000 &
    PID1=$!
    sleep 2
    (echo "LOGIN Alice"; sleep 1) | nc localhost 4000 | grep -q "username-taken"
    RESULT=$?
    kill $PID1 2>/dev/null
    if [ $RESULT -eq 0 ]; then
        echo -e "${GREEN}✓ Duplicate username correctly rejected${NC}"
    else
        echo -e "${RED}✗ Duplicate username test failed${NC}"
    fi
}
echo ""

# Test 3: WHO command
echo -e "${YELLOW}[4] Testing WHO command...${NC}"
{
    (echo "LOGIN Bob"; sleep 2; echo "WHO"; sleep 2) | nc localhost 4000 | grep -q "USER Bob"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ WHO command works${NC}"
    else
        echo -e "${RED}✗ WHO command failed${NC}"
    fi
}
echo ""

# Test 4: PING/PONG
echo -e "${YELLOW}[5] Testing PING/PONG...${NC}"
(echo "LOGIN Charlie"; sleep 1; echo "PING"; sleep 1) | nc localhost 4000 | grep -q "PONG"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PING/PONG works${NC}"
else
    echo -e "${RED}✗ PING/PONG failed${NC}"
fi
echo ""

# Test 5: Message broadcasting
echo -e "${YELLOW}[6] Testing message broadcasting...${NC}"
echo "   Starting two clients to test messaging..."
{
    # Start client 1
    (echo "LOGIN Dave"; sleep 2; echo "MSG Hello from Dave"; sleep 2) | nc localhost 4000 &
    PID1=$!
    
    # Start client 2 and check if it receives Dave's message
    sleep 1
    (echo "LOGIN Eve"; sleep 3) | nc localhost 4000 | grep -q "MSG Dave Hello from Dave"
    RESULT=$?
    
    kill $PID1 2>/dev/null
    
    if [ $RESULT -eq 0 ]; then
        echo -e "${GREEN}✓ Message broadcasting works${NC}"
    else
        echo -e "${RED}✗ Message broadcasting failed${NC}"
    fi
}
echo ""

# Summary
echo "================================"
echo -e "${GREEN}Test Suite Complete!${NC}"
echo "================================"
echo ""
echo "Manual tests to perform:"
echo "  1. Open 3+ terminals and connect with: nc localhost 4000"
echo "  2. Test DM command: DM <username> <message>"
echo "  3. Test idle timeout: connect and wait 60+ seconds"
echo "  4. Test graceful disconnect: Ctrl+C a client"
echo ""
echo "Recording checklist:"
echo "  □ Show server starting"
echo "  □ Show 2-3 clients connecting"
echo "  □ Show chat messages"
echo "  □ Show WHO command output"
echo "  □ Show DM (private message)"
echo "  □ Show graceful disconnect"
echo ""