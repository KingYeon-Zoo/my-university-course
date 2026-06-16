#!/bin/bash
# test_basic.sh - Basic command test

echo "=== Basic Command Test ==="
echo ""

echo "Test 1: Echo command"
echo "Hello World"
echo "This is a test"
echo ""

echo "Test 2: Current directory"
pwd
echo ""

echo "Test 3: Change directory"
cd ..
pwd
cd -
echo ""

echo "Test 4: List directory"
ls
echo ""

echo "=== Basic test completed ==="

