#!/bin/bash
# test_while.sh - While loop test

echo "=== While Loop Test ==="
echo ""

echo "Test 1: Simple counter"
i=1
while [ $i -le 5 ]
do
    echo "Count: $i"
    i=$((i+1))
done
echo ""

echo "Test 2: Countdown"
count=3
while [ $count -gt 0 ]
do
    echo "Countdown: $count"
    count=$((count-1))
done
echo "Liftoff!"
echo ""

echo "Test 3: While with condition"
n=1
while [ $n -le 10 ]
do
    if [ $n -eq 5 ]
    then
        echo "Reached halfway point!"
    fi
    n=$((n+1))
done
echo ""

echo "=== While test completed ==="

