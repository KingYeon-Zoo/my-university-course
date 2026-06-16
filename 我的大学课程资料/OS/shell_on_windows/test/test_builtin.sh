#!/bin/bash
# test_builtin.sh - Test new built-in commands

echo "=== Built-in Commands Test ==="
echo ""

echo "Test 1: help command"
help
echo ""

echo "Test 2: ls command (current directory)"
ls
echo ""

echo "Test 3: mkdir command"
mkdir test_dir_1
mkdir test_dir_2
ls
echo ""

echo "Test 4: touch command"
touch test_file_1.txt
touch test_file_2.txt
ls
echo ""

echo "Test 5: cat command (create file with content first)"
echo "Hello World" > test_content.txt
echo "This is line 2" >> test_content.txt
cat test_content.txt
echo ""

echo "Test 6: cp command"
cp test_content.txt test_copy.txt
cat test_copy.txt
echo ""

echo "Test 7: mv command"
mv test_copy.txt test_moved.txt
ls
echo ""

echo "Test 8: rm command"
rm test_file_1.txt
rm test_file_2.txt
rm test_content.txt
rm test_moved.txt
ls
echo ""

echo "Test 9: rmdir command"
rmdir test_dir_1
rmdir test_dir_2
ls
echo ""

echo "Test 10: ls with path"
mkdir subdir
touch subdir/file1.txt
touch subdir/file2.txt
ls subdir
rm subdir/file1.txt
rm subdir/file2.txt
rmdir subdir
echo ""

echo "Test 11: Error handling - rm on directory"
mkdir error_test_dir
rm error_test_dir
rmdir error_test_dir
echo ""

echo "Test 12: Error handling - cat non-existent file"
cat nonexistent_file.txt
echo ""

echo "Test 13: Error handling - mkdir existing directory"
mkdir duplicate_dir
mkdir duplicate_dir
rmdir duplicate_dir
echo ""

echo "=== Built-in commands test completed ==="

