//#include <iostream>
//#include <vector>
//#include <list>
//#include <algorithm>
//#include <iterator>
//
//using namespace std;
//
//template <typename Container>
//void printContainer(const Container& container, const char* label) {
//    cout << label << ": ";
//    for (const auto& element : container) {
//        cout << element << " ";
//    }
//    cout << endl;
//}
//
//vector<int> mergeVectorsTwoPointers(const vector<int>& v1, const vector<int>& v2) {
//    vector<int> result;
//    result.reserve(v1.size() + v2.size());
//    merge(v1.begin(), v1.end(), v2.begin(), v2.end(), back_inserter(result));
//    return result;
//}
//
//vector<int> concatenateAndSortVectors(const vector<int>& v1, const vector<int>& v2) {
//    vector<int> result = v1;
//    result.insert(result.end(), v2.begin(), v2.end());
//    sort(result.begin(), result.end());
//    return result;
//}
//
//list<int> mergeListsTwoPointers(const list<int>& l1, const list<int>& l2) {
//    list<int> result;
//    merge(l1.begin(), l1.end(), l2.begin(), l2.end(), back_inserter(result));
//    return result;
//}
//
//list<int> concatenateAndSortLists(const list<int>& l1, const list<int>& l2) {
//    list<int> result = l1;
//    result.insert(result.end(), l2.begin(), l2.end());
//    result.sort();
//    return result;
//}
//
//int main() {
//    vector<int> arr1_vec = { 1, 3, 5, 7, 9 };
//    vector<int> arr2_vec = { 2, 4, 6, 8, 10 };
//    list<int> arr1_list(arr1_vec.begin(), arr1_vec.end());
//    list<int> arr2_list(arr2_vec.begin(), arr2_vec.end());
//
//    cout << "--- 原始数据 (有序) ---" << endl;
//    printContainer(arr1_vec, "Vector 1");
//    printContainer(arr2_vec, "Vector 2");
//    printContainer(arr1_list, "List   1");
//    printContainer(arr2_list, "List   2");
//    cout << endl;
//
//    cout << "--- 使用 std::vector 合并 (STL 实现) ---" << endl;
//    cout << "方法一: 双指针法 (std::merge)" << endl;
//    vector<int> merged_vec1 = mergeVectorsTwoPointers(arr1_vec, arr2_vec);
//    printContainer(merged_vec1, "合并结果");
//    cout << endl;
//
//    cout << "方法二: 先连接后排序" << endl;
//    vector<int> merged_vec2 = concatenateAndSortVectors(arr1_vec, arr2_vec);
//    printContainer(merged_vec2, "合并结果");
//    cout << endl;
//
//    cout << "--- 使用 std::list 合并 (STL 实现) ---" << endl;
//    cout << "方法一: 双指针法 (std::merge)" << endl;
//    list<int> merged_list1 = mergeListsTwoPointers(arr1_list, arr2_list);
//    printContainer(merged_list1, "合并结果");
//    cout << endl;
//
//    cout << "方法二: 先连接后排序" << endl;
//    list<int> merged_list2 = concatenateAndSortLists(arr1_list, arr2_list);
//    printContainer(merged_list2, "合并结果");
//    cout << endl;
//
//    return 0;
//}
