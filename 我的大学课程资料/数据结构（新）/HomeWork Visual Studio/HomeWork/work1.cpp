//#include <iostream>
//#include <random>
//#include <chrono>
//#include <algorithm>
//#include <climits>
//using namespace std;
//
//// √∞≈›≈≈–Ú
//void bubbleSort(int arr[], int size) {
//    for (bool swapped = true; swapped && size--;) {
//        swapped = false;
//        for (int i = 0; i < size; ++i) {
//            if (arr[i] > arr[i + 1]) {
//                swap(arr[i], arr[i + 1]);
//                swapped = true;
//            }
//        }
//    }
//}
//
//// —°‘Ò≈≈–Ú
//void selectionSort(int arr[], int size) {
//    for (int i = 0; i < size-1; ++i) {
//        int minPos = i;
//        for (int j = i+1; j < size; ++j)
//            if (arr[j] < arr[minPos]) minPos = j;
//        swap(arr[i], arr[minPos]);
//    }
//}
//
//// ≤Â»Î≈≈–Ú
//void insertionSort(int arr[], int size) {
//    for (int i = 1; i < size; ++i) {
//        int key = arr[i], j = i-1;
//        while (j >= 0 && arr[j] > key)
//            arr[j+1] = arr[j--];
//        arr[j+1] = key;
//    }
//}
//
//// øÏÀŸ≈≈–Ú µœ÷
//void quickSortImpl(int arr[], int low, int high) {
//    if (low >= high) return;
//    
//    int pivot = arr[high];
//    int i = low;
//    for (int j = low; j < high; ++j) {
//        if (arr[j] < pivot)
//            swap(arr[i++], arr[j]);
//    }
//    swap(arr[i], arr[high]);
//    
//    quickSortImpl(arr, low, i-1);
//    quickSortImpl(arr, i+1, high);
//}
//
//// øÏÀŸ≈≈–Ú∞¸◊∞∫Ø ˝
//void quickSort(int arr[], int size) {
//    quickSortImpl(arr, 0, size - 1);
//}
//
//// πÈ≤¢≈≈–Ú µœ÷
//void mergeSortImpl(int arr[], int left, int right) {
//    if (left >= right) return;
//    
//    int mid = left + (right - left)/2;
//    mergeSortImpl(arr, left, mid);
//    mergeSortImpl(arr, mid+1, right);
//    
//    int* temp = new int[right-left+1];
//    int i = left, j = mid+1, k = 0;
//    while (i <= mid && j <= right)
//        temp[k++] = (arr[i] < arr[j]) ? arr[i++] : arr[j++];
//    while (i <= mid) temp[k++] = arr[i++];
//    while (j <= right) temp[k++] = arr[j++];
//    copy(temp, temp+k, arr+left);
//    delete[] temp;
//}
//
//// πÈ≤¢≈≈–Ú∞¸◊∞∫Ø ˝
//void mergeSort(int arr[], int size) {
//    mergeSortImpl(arr, 0, size - 1);
//}
//
//// ∂—≈≈–Ú∏®÷˙∫Ø ˝
//void heapify(int arr[], int n, int i) {
//    int largest = i, l = 2*i+1, r = 2*i+2;
//    if (l < n && arr[l] > arr[largest]) largest = l;
//    if (r < n && arr[r] > arr[largest]) largest = r;
//    if (largest != i) {
//        swap(arr[i], arr[largest]);
//        heapify(arr, n, largest);
//    }
//}
//
//// ∂—≈≈–Ú
//void heapSort(int arr[], int size) {
//    for (int i = size/2-1; i >= 0; --i)
//        heapify(arr, size, i);
//    for (int i = size-1; i > 0; --i) {
//        swap(arr[0], arr[i]);
//        heapify(arr, i, 0);
//    }
//}
//
//// œ£∂˚≈≈–Ú
//void shellSort(int arr[], int size) {
//    for (int gap = size/2; gap > 0; gap /= 2) {
//        for (int i = gap; i < size; ++i) {
//            int temp = arr[i], j;
//            for (j = i; j >= gap && arr[j-gap] > temp; j -= gap)
//                arr[j] = arr[j-gap];
//            arr[j] = temp;
//        }
//    }
//}
//
//// º∆ ˝≈≈–Ú
//void countingSort(int arr[], int size) {
//    int maxVal = *max_element(arr, arr+size);
//    int minVal = *min_element(arr, arr+size);
//    int range = maxVal - minVal + 1;
//    
//    int* count = new int[range]();
//    for (int i = 0; i < size; ++i)
//        count[arr[i]-minVal]++;
//    
//    int index = 0;
//    for (int i = 0; i < range; ++i)
//        while (count[i]--) 
//            arr[index++] = i + minVal;
//    
//    delete[] count;
//}
//
//// …˙≥…ÀÊª˙≤‚ ‘ ˝æ›
//int* generateTestData(int size) {
//    int* data = new int[size];
//    random_device rd;
//    mt19937 gen(rd());
//    uniform_int_distribution<> dis(1, 10000);
//
//    for (int i = 0; i < size; ++i) {
//        data[i] = dis(gen);
//    }
//    return data;
//}
//
//// ≤‚ ‘≈≈–ÚÀ„∑®≤¢º∆ ±
//void testSortAlgorithm(void (*sortFunc)(int[], int), const string& algorithmName, int original[], int size) {
//    int* data = new int[size];
//    copy(original, original + size, data);
//
//    auto start = chrono::high_resolution_clock::now();
//    sortFunc(data, size);
//    auto end = chrono::high_resolution_clock::now();
//
//    auto duration = chrono::duration_cast<chrono::microseconds>(end - start);
//    cout << algorithmName << " ∫ƒ ±: " << duration.count() << " Œ¢√Î"
//        << " (" << duration.count() / 1000.0 << " ∫¡√Î)\n";
//
//    delete[] data;
//}
//
//int main() {
//    const int DATA_SIZE = 10000;
//    int* originalData = generateTestData(DATA_SIZE);
//
//    cout << "≤‚ ‘ ˝æ›¡ø: " << DATA_SIZE << " ∏ˆ‘™Àÿ\n\n";
//
//    // ≤‚ ‘∏˜÷÷≈≈–ÚÀ„∑®
//    testSortAlgorithm(bubbleSort, "√∞≈›≈≈–Ú", originalData, DATA_SIZE);
//    testSortAlgorithm(selectionSort, "—°‘Ò≈≈–Ú", originalData, DATA_SIZE);
//    testSortAlgorithm(insertionSort, "≤Â»Î≈≈–Ú", originalData, DATA_SIZE);
//    testSortAlgorithm(quickSort, "øÏÀŸ≈≈–Ú", originalData, DATA_SIZE);
//    testSortAlgorithm(mergeSort, "πÈ≤¢≈≈–Ú", originalData, DATA_SIZE);
//    testSortAlgorithm(heapSort, "∂—≈≈–Ú", originalData, DATA_SIZE);
//    testSortAlgorithm(shellSort, "œ£∂˚≈≈–Ú", originalData, DATA_SIZE);
//    testSortAlgorithm(countingSort, "º∆ ˝≈≈–Ú", originalData, DATA_SIZE);
//    testSortAlgorithm([](int arr[], int size) {sort(arr, arr + size); }, "STL sort", originalData, DATA_SIZE);
//
//    delete[] originalData;
//    return 0;
//}