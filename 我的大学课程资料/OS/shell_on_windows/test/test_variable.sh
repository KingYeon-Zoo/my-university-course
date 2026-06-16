#!/bin/bash
# test_variable.sh - Variable test

echo "=== Variable Test ==="
echo ""

echo "Test 1: Simple variable assignment"
name="Alice"
echo "Hello $name"
echo ""

echo "Test 2: Numeric variables"
count=10
echo "Count is $count"
echo ""

echo "Test 3: Variable expansion"
first="John"
last="Doe"
echo "Full name: $first $last"
echo ""

echo "Test 4: Variable in path"
dir="test"
echo "Directory: $dir"
echo ""

echo "Test 5: Exit code variable"
echo "Testing..."
echo "Last exit code: $?"
echo ""

echo "=== Variable test completed ==="

