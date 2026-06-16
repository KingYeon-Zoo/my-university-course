#!/bin/bash
# test_pipe.sh - Pipeline test

echo "=== Pipeline Test ==="
echo ""

echo "Test 1: Simple pipe"
echo "This is a test line" | findstr "test"
echo ""

echo "Test 2: Directory listing with filter"
dir | findstr ".txt"
echo ""

echo "Test 3: Echo and filter"
echo "apple banana cherry" | findstr "banana"
echo ""

echo "=== Pipeline test completed ==="

