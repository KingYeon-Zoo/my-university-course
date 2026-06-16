#!/bin/bash
# test_for.sh - For loop test

echo "=== For Loop Test ==="
echo ""

echo "Test 1: Simple iteration"
for i in 1 2 3 4 5
do
    echo "Number: $i"
done
echo ""

echo "Test 2: String iteration"
for fruit in apple banana orange grape
do
    echo "Fruit: $fruit"
done
echo ""

echo "Test 3: File pattern iteration"
echo "Files in current directory:"
for file in *
do
    echo "  - $file"
done
echo ""

echo "Test 4: Name list"
for name in Alice Bob Charlie
do
    echo "Hello, $name!"
done
echo ""

echo "=== For test completed ==="

