//#include <iostream>
//#include <vector>
//#include <chrono>
//#include <algorithm>
//#include <random>
//
//using namespace std;
//using namespace std::chrono;
//
//int swapCount = 0;
//int compareCount = 0;
//
//struct SortStats {
//    long long time_ms;
//    size_t space_used;
//    int swap_count;
//    int compare_count;
//};
//
//bool compare(int arr[], int i, int j) {
//    compareCount++;
//    return arr[i] > arr[j];
//}
//
//bool compare(vector<int>& arr, int i, int j) {
//    compareCount++;
//    return arr[i] > arr[j];
//}
//
//void swap(int arr[], int i, int j) {
//    swapCount++;
//    std::swap(arr[i], arr[j]);
//}
//
//void swap(vector<int>& arr, int i, int j) {
//    swapCount++;
//    std::swap(arr[i], arr[j]);
//}
//
//// ð����������汾
//SortStats bubble_sort(int arr[], int n) {
//    auto start = high_resolution_clock::now();
//    swapCount = 0;
//    compareCount = 0;
//
//    bool swapped;
//    for (int i = 0; i < n - 1; ++i) {
//        swapped = false;
//        for (int j = 0; j < n - i - 1; ++j) {
//            if (compare(arr, j, j + 1)) {
//                swap(arr, j, j + 1);
//                swapped = true;
//            }
//        }
//        // �����һ��û�з���������˵�������Ѿ�����
//        if (!swapped) {
//            break;
//        }
//    }
//
//    auto end = high_resolution_clock::now();
//    return {
//        duration_cast<milliseconds>(end - start).count(),
//        sizeof(int),
//        swapCount,
//        compareCount
//    };
//}
//
//// ð������vector�汾
//SortStats bubble_sort(vector<int>& arr, int n) {
//    auto start = high_resolution_clock::now();
//    swapCount = 0;
//    compareCount = 0;
//
//    bool swapped;
//    for (int i = 0; i < n - 1; ++i) {
//        swapped = false;
//        for (int j = 0; j < n - i - 1; ++j) {
//            if (compare(arr, j, j + 1)) {
//                swap(arr, j, j + 1);
//                swapped = true;
//            }
//        }
//        // �����һ��û�з���������˵�������Ѿ�����
//        if (!swapped) {
//            break;
//        }
//    }
//
//    auto end = high_resolution_clock::now();
//    return {
//        duration_cast<milliseconds>(end - start).count(),
//        sizeof(int),
//        swapCount,
//        compareCount
//    };
//}
//
//// ������������汾
//SortStats insertion_sort(int arr[], int n) {
//    auto start = high_resolution_clock::now();
//    swapCount = 0;
//    compareCount = 0;
//
//    for (int i = 1; i < n; ++i) {
//        int j = i;
//        while (j > 0) {
//            if (!compare(arr, j - 1, j)) {
//                break;
//            }
//            swap(arr, j - 1, j);
//            j--;
//        }
//    }
//
//    auto end = high_resolution_clock::now();
//    return {
//        duration_cast<milliseconds>(end - start).count(),
//        sizeof(int),
//        swapCount,
//        compareCount
//    };
//}
//
//// ��������vector�汾
//SortStats insertion_sort(vector<int>& arr, int n) {
//    auto start = high_resolution_clock::now();
//    swapCount = 0;
//    compareCount = 0;
//
//    for (int i = 1; i < n; ++i) {
//        int j = i;
//        while (j > 0) {
//            if (!compare(arr, j - 1, j)) {
//                break;
//            }
//            swap(arr, j - 1, j);
//            j--;
//        }
//    }
//
//    auto end = high_resolution_clock::now();
//    return {
//        duration_cast<milliseconds>(end - start).count(),
//        sizeof(int),
//        swapCount,
//        compareCount
//    };
//}
//
//// ���ɲ�������
//void generate_data(int arr[], int size) {
//    random_device rd;
//    mt19937 gen(rd());
//    uniform_int_distribution<> dis(1, 1000000);
//
//    for (int i = 0; i < size; ++i) {
//        arr[i] = dis(gen);
//    }
//}
//
//void generate_data(vector<int>& arr, int size) {
//    random_device rd;
//    mt19937 gen(rd());
//    uniform_int_distribution<> dis(1, 1000000);
//
//    arr.resize(size);
//    for (int i = 0; i < size; ++i) {
//        arr[i] = dis(gen);
//    }
//}
//
//// ��ӡ���
//void print_result(const string& algo, const string& type, const SortStats& stats) {
//    cout << "�㷨: " << algo << " (" << type << ")\n"
//        << "ʱ��: " << stats.time_ms << " ms\n"
//        << "�ռ�: " << stats.space_used << " bytes\n"
//        << "����: " << stats.swap_count << " ��\n"
//        << "�Ƚ�: " << stats.compare_count << " ��\n"
//        << "------------------------\n";
//}
//
//int main() {
//    const int SIZE = 10000;
//
//    // ׼����������
//    vector<int> base_vec;
//    generate_data(base_vec, SIZE);
//
//    int base_arr[SIZE];
//    generate_data(base_arr, SIZE);
//
//    // �����������
//    vector<int> vec_test;
//    int arr_test[SIZE];
//
//    // 1. ð������ vector
//    vec_test = base_vec;
//    auto stats1 = bubble_sort(vec_test, SIZE);
//    print_result("ð������", "vector", stats1);
//
//    // 2. ð������ array
//    copy(base_arr, base_arr + SIZE, arr_test);
//    auto stats2 = bubble_sort(arr_test, SIZE);
//    print_result("ð������", "int[]", stats2);
//
//    // 3. �������� vector
//    vec_test = base_vec;
//    auto stats3 = insertion_sort(vec_test, SIZE);
//    print_result("��������", "vector", stats3);
//
//    // 4. �������� array
//    copy(base_arr, base_arr + SIZE, arr_test);
//    auto stats4 = insertion_sort(arr_test, SIZE);
//    print_result("��������", "int[]", stats4);
//
//    return 0;
//}
