#!/bin/bash
# test_case.sh - Case statement test

echo "=== Case Statement Test ==="
echo ""

echo "Test 1: Fruit selection"
fruit="apple"
case $fruit in
    apple)
        echo "Red fruit"
        ;;
    banana)
        echo "Yellow fruit"
        ;;
    orange)
        echo "Orange fruit"
        ;;
    *)
        echo "Unknown fruit"
        ;;
esac
echo ""

echo "Test 2: Number check"
num=2
case $num in
    1)
        echo "One"
        ;;
    2)
        echo "Two"
        ;;
    3)
        echo "Three"
        ;;
    *)
        echo "Other number"
        ;;
esac
echo ""

echo "Test 3: Command selection"
cmd="start"
case $cmd in
    start)
        echo "Starting service..."
        ;;
    stop)
        echo "Stopping service..."
        ;;
    restart)
        echo "Restarting service..."
        ;;
    *)
        echo "Unknown command"
        ;;
esac
echo ""

echo "=== Case test completed ==="

