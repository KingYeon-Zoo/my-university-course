#!/bin/bash
# test_redirect.sh - I/O redirection test

echo "=== I/O Redirection Test ==="
echo ""

echo "Test 1: Output redirection"
echo "This is test output" > test_output.txt
echo "Output written to test_output.txt"
echo ""

echo "Test 2: Read from file"
cat test_output.txt
echo ""

echo "Test 3: Append to file"
echo "This is appended text" >> test_output.txt
echo "Text appended to test_output.txt"
echo ""

echo "Test 4: Display file contents"
cat test_output.txt
echo ""

echo "=== Redirection test completed ==="

