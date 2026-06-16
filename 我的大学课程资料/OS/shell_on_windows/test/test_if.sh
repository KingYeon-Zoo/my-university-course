#!/bin/bash
# test_if.sh - Conditional statement test

echo "=== If Statement Test ==="
echo ""

echo "Test 1: Numeric comparison (greater than)"
x=5
if [ $x -gt 3 ]
then
    echo "x ($x) is greater than 3"
else
    echo "x ($x) is not greater than 3"
fi
echo ""

echo "Test 2: Numeric comparison (equal)"
y=10
if [ $y -eq 10 ]
then
    echo "y equals 10"
fi
echo ""

echo "Test 3: Numeric comparison (less than)"
z=2
if [ $z -lt 5 ]
then
    echo "z ($z) is less than 5"
else
    echo "z ($z) is not less than 5"
fi
echo ""

echo "Test 4: String comparison"
name="test"
if [ $name = "test" ]
then
    echo "Name matches 'test'"
fi
echo ""

echo "Test 5: Nested if"
a=15
if [ $a -gt 10 ]
then
    if [ $a -lt 20 ]
    then
        echo "a is between 10 and 20"
    fi
fi
echo ""

echo "=== If test completed ==="

