#!/bin/bash
# test_all.sh - Run all tests

echo "========================================"
echo "Running All Shell Tests"
echo "========================================"
echo ""

echo "Running test_basic.sh..."
./test_basic.sh
echo ""

echo "Running test_builtin.sh..."
./test_builtin.sh
echo ""

echo "Running test_variable.sh..."
./test_variable.sh
echo ""

echo "Running test_if.sh..."
./test_if.sh
echo ""

echo "Running test_while.sh..."
./test_while.sh
echo ""

echo "Running test_for.sh..."
./test_for.sh
echo ""

echo "Running test_pipe.sh..."
./test_pipe.sh
echo ""

echo "Running test_redirect.sh..."
./test_redirect.sh
echo ""

echo "Running test_case.sh..."
./test_case.sh
echo ""

echo "========================================"
echo "All Tests Completed!"
echo "========================================"

