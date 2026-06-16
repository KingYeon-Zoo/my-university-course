// #include <iostream>
// #include <chrono>
// #include <iomanip>
// #include <cstdlib>
// #include <ctime>
// #include <cmath>

// using namespace std;

// const int MAX_SIZE = 1000000;
// const int TEST_REPEAT = 3;
// const int ALGORITHM_COUNT = 9;
// const int DATA_TYPE_COUNT = 5;
// const int SIZE_COUNT = 7;

// const int test_sizes[SIZE_COUNT] = {100, 500, 1000, 5000, 10000, 50000, 100000};

// const char* algorithm_names[ALGORITHM_COUNT] = {
//     "冒泡排序", "选择排序", "插入排序", "希尔排序", "快速排序",
//     "归并排序", "堆排序", "计数排序", "基数排序"
// };

// const char* data_type_names[DATA_TYPE_COUNT] = {
//     "随机数据", "已排序", "逆序数据", "部分有序", "重复元素"
// };

// struct PerformanceStats {
//     long long comparisons;
//     long long swaps;
//     double time_ms;
    
//     PerformanceStats() : comparisons(0), swaps(0), time_ms(0.0) {}
    
//     void reset() {
//         comparisons = 0;
//         swaps = 0;
//         time_ms = 0.0;
//     }
// };

// class SimpleRandom {
// private:
//     unsigned long long seed;
//     unsigned long long seed2;  
//     unsigned long long multiplier1;
//     unsigned long long multiplier2;
    
// public:
//     SimpleRandom(unsigned long long s = 1) : seed(s), seed2(s ^ 0x5DEECE66DLL), 
//                                       multiplier1(1103515245ULL), multiplier2(134775813ULL) {}
    
//     void setSeed(unsigned long long s) {
//         seed = s;
//         seed2 = s ^ 0x5DEECE66DLL;
//         // 添加时间因子增强随机性
//         unsigned long long timeFactor = static_cast<unsigned long long>(time(nullptr));
//         seed = (seed ^ timeFactor) | 1;  // 确保奇数
//         seed2 = (seed2 ^ (timeFactor << 16)) | 1;
//     }
    
//     int next() {
//         // 使用双重线性同余生成器提高质量
//         seed = (seed * multiplier1 + 12345) & 0x7fffffffULL;
//         seed2 = (seed2 * multiplier2 + 54321) & 0x7fffffffULL;
//         return (int)((seed ^ seed2) & 0x7fffffffULL);
//     }
    
//     int nextRange(int min, int max) {
//         if (min >= max) return min;
//         unsigned long long range = static_cast<unsigned long long>(max - min + 1);
//         return min + (next() % static_cast<int>(range));
//     }
    
//     // 添加更好的随机分布函数
//     double nextDouble() {
//         return (double)next() / (double)0x7fffffffULL;
//     }
    
//     // 正态分布随机数（Box-Muller变换）
//     int nextGaussian(int mean, int stddev) {
//         static bool hasSpare = false;
//         static double spare;
        
//         if (hasSpare) {
//             hasSpare = false;
//             return (int)(mean + stddev * spare);
//         }
        
//         hasSpare = true;
//         double u = nextDouble();
//         double v = nextDouble();
//         double mag = stddev * sqrt(-2.0 * log(u));
//         spare = mag * cos(2.0 * 3.14159265359 * v);
//         return (int)(mean + mag * sin(2.0 * 3.14159265359 * v));
//     }
// };

// SimpleRandom rng;

// // 函数前向声明
// void copyArray(int* source, int* dest, int size) {
//     for (int i = 0; i < size; i++) {
//         dest[i] = source[i];
//     }
// }

// bool isArraySorted(int* arr, int size) {
//     for (int i = 1; i < size; i++) {
//         if (arr[i] < arr[i-1]) {
//             return false;
//         }
//     }
//     return true;
// }

// void printArray(int* arr, int size, int printCount = 10) {
//     int count = (size < printCount) ? size : printCount;
//     for (int i = 0; i < count; i++) {
//         cout << arr[i] << " ";
//     }
//     if (size > printCount) {
//         cout << "... (总共" << size << "个元素)";
//     }
//     cout << endl;
// }

// enum DataType {
//     RANDOM_DATA = 0,
//     SORTED_DATA = 1,
//     REVERSE_DATA = 2,
//     PARTIAL_SORTED = 3,
//     DUPLICATE_DATA = 4
// };

// void generateRandomData(int* arr, int size) {
//     // 使用更大的数值范围增加多样性
//     int maxRange = size * 5; // 增加到5倍而不是2倍
    
//     // 80%的数据使用正常范围
//     int normalCount = (int)(size * 0.8);
//     for (int i = 0; i < normalCount; i++) {
//         arr[i] = rng.nextRange(1, maxRange);
//     }
    
//     // 10%的数据使用较小值
//     int smallCount = (int)(size * 0.1);
//     for (int i = normalCount; i < normalCount + smallCount; i++) {
//         arr[i] = rng.nextRange(1, size / 10);
//     }
    
//     // 10%的数据使用较大值
//     for (int i = normalCount + smallCount; i < size; i++) {
//         arr[i] = rng.nextRange(maxRange, maxRange * 2);
//     }
    
//     // 随机打乱顺序以增加随机性
//     for (int i = size - 1; i > 0; i--) {
//         int j = rng.nextRange(0, i);
//         int temp = arr[i];
//         arr[i] = arr[j];
//         arr[j] = temp;
//     }
// }

// void generateSortedData(int* arr, int size) {
//     for (int i = 0; i < size; i++) {
//         arr[i] = i + 1;
//     }
// }

// void generateReverseData(int* arr, int size) {
//     for (int i = 0; i < size; i++) {
//         arr[i] = size - i;
//     }
// }

// void generatePartialSortedData(int* arr, int size) {
//     // 随机选择有序比例（30%-80%）
//     double sortedRatio = 0.3 + rng.nextDouble() * 0.5;
//     int sortedCount = (int)(size * sortedRatio);
    
//     // 随机选择部分有序的模式
//     int pattern = rng.nextRange(0, 3);
    
//     if (pattern == 0) {
//         // 模式1：前半部分有序，后半部分随机
//         for (int i = 0; i < sortedCount; i++) {
//             arr[i] = i + 1;
//         }
//         for (int i = sortedCount; i < size; i++) {
//             arr[i] = rng.nextRange(1, size * 2);
//         }
//     } else if (pattern == 1) {
//         // 模式2：多个有序块
//         int blockCount = rng.nextRange(3, 6); // 3-5个块
//         int blockSize = sortedCount / blockCount;
//         int currentIndex = 0;
        
//         for (int block = 0; block < blockCount && currentIndex < size; block++) {
//             int thisBlockSize = (block == blockCount - 1) ? 
//                                (sortedCount - currentIndex) : blockSize;
            
//             // 创建有序块
//             int baseValue = rng.nextRange(1, size);
//             for (int i = 0; i < thisBlockSize; i++) {
//                 arr[currentIndex + i] = baseValue + i;
//             }
//             currentIndex += thisBlockSize;
            
//             // 添加一些随机元素作为间隔
//             int gapSize = rng.nextRange(1, 5);
//             for (int i = 0; i < gapSize && currentIndex < size; i++) {
//                 arr[currentIndex++] = rng.nextRange(1, size * 2);
//             }
//         }
        
//         // 填充剩余位置
//         while (currentIndex < size) {
//             arr[currentIndex++] = rng.nextRange(1, size * 2);
//         }
//     } else if (pattern == 2) {
//         // 模式3：大部分有序，少量位置交换
//         for (int i = 0; i < size; i++) {
//             arr[i] = i + 1;
//         }
        
//         // 随机交换一些位置，破坏部分有序性
//         int swapCount = size - sortedCount;
//         for (int i = 0; i < swapCount; i++) {
//             int pos1 = rng.nextRange(0, size - 1);
//             int pos2 = rng.nextRange(0, size - 1);
//             int temp = arr[pos1];
//             arr[pos1] = arr[pos2];
//             arr[pos2] = temp;
//         }
//     } else {
//         // 模式4：近似有序，有小幅波动
//         for (int i = 0; i < size; i++) {
//             int baseValue = i + 1;
//             int variance = rng.nextRange(-5, 5); // 小幅波动
//             arr[i] = baseValue + variance;
//             if (arr[i] < 1) arr[i] = 1;
//         }
//     }
// }

// void generateDuplicateData(int* arr, int size) {
//     // 根据数据大小动态调整唯一值数量
//     int uniqueValues;
//     if (size < 100) {
//         uniqueValues = size / 5;  // 小数据集：20%唯一值
//     } else if (size < 10000) {
//         uniqueValues = size / 10; // 中等数据集：10%唯一值
//     } else {
//         uniqueValues = size / 20; // 大数据集：5%唯一值
//     }
    
//     if (uniqueValues < 3) uniqueValues = 3;
//     if (uniqueValues > size / 2) uniqueValues = size / 2;
    
//     // 创建基础唯一值集合
//     int* uniqueSet = new int[uniqueValues];
//     for (int i = 0; i < uniqueValues; i++) {
//         uniqueSet[i] = rng.nextRange(1, size * 2);
//     }
    
//     // 分配重复模式
//     int pattern = rng.nextRange(0, 2);
    
//     if (pattern == 0) {
//         // 模式1：均匀分布重复
//         for (int i = 0; i < size; i++) {
//             arr[i] = uniqueSet[i % uniqueValues];
//         }
//     } else if (pattern == 1) {
//         // 模式2：某些值重复更多（帕累托分布）
//         int highFreqCount = uniqueValues / 3;
//         int normalFreqCount = uniqueValues - highFreqCount;
        
//         // 60%的数据使用高频值
//         int highFreqElements = (int)(size * 0.6);
//         for (int i = 0; i < highFreqElements; i++) {
//             arr[i] = uniqueSet[rng.nextRange(0, highFreqCount - 1)];
//         }
        
//         // 40%的数据使用其他值
//         for (int i = highFreqElements; i < size; i++) {
//             arr[i] = uniqueSet[rng.nextRange(highFreqCount, uniqueValues - 1)];
//         }
//     } else {
//         // 模式3：块状重复
//         int blockSize = size / uniqueValues;
//         int currentIndex = 0;
        
//         for (int i = 0; i < uniqueValues && currentIndex < size; i++) {
//             int thisBlockSize = (i == uniqueValues - 1) ? (size - currentIndex) : blockSize;
//             for (int j = 0; j < thisBlockSize; j++) {
//                 arr[currentIndex++] = uniqueSet[i];
//             }
//         }
//     }
    
//     // 随机打乱以增加随机性（保持重复特性）
//     for (int i = 0; i < size / 2; i++) {
//         int pos1 = rng.nextRange(0, size - 1);
//         int pos2 = rng.nextRange(0, size - 1);
//         int temp = arr[pos1];
//         arr[pos1] = arr[pos2];
//         arr[pos2] = temp;
//     }
    
//     delete[] uniqueSet;
// }

// void generateTestData(int* arr, int size, DataType type) {
//     switch (type) {
//         case RANDOM_DATA:
//             generateRandomData(arr, size);
//             break;
//         case SORTED_DATA:
//             generateSortedData(arr, size);
//             break;
//         case REVERSE_DATA:
//             generateReverseData(arr, size);
//             break;
//         case PARTIAL_SORTED:
//             generatePartialSortedData(arr, size);
//             break;
//         case DUPLICATE_DATA:
//             generateDuplicateData(arr, size);
//             break;
//         default:
//             generateRandomData(arr, size);
//             break;
//     }
// }

// long long global_comparisons = 0;
// long long global_swaps = 0;

// void resetGlobalCounters() {
//     global_comparisons = 0;
//     global_swaps = 0;
// }

// void bubbleSort(int* arr, int size) {
//     for (int i = 0; i < size - 1; i++) {
//         bool swapped = false;
        
//         for (int j = 0; j < size - 1 - i; j++) {
//             global_comparisons++;
            
//             if (arr[j] > arr[j + 1]) {
//                 int temp = arr[j];
//                 arr[j] = arr[j + 1];
//                 arr[j + 1] = temp;
                
//                 global_swaps++;
//                 swapped = true;
//             }
//         }
        
//         if (!swapped) {
//             break;
//         }
//     }
// }

// void selectionSort(int* arr, int size) {
//     for (int i = 0; i < size - 1; i++) {
//         int minIndex = i;
        
//         for (int j = i + 1; j < size; j++) {
//             global_comparisons++;
            
//             if (arr[j] < arr[minIndex]) {
//                 minIndex = j;
//             }
//         }
        
//         if (minIndex != i) {
//             int temp = arr[i];
//             arr[i] = arr[minIndex];
//             arr[minIndex] = temp;
            
//             global_swaps++;
//         }
//     }
// }

// void insertionSort(int* arr, int size) {
//     for (int i = 1; i < size; i++) {
//         int key = arr[i];
//         int j = i - 1;
        
//         while (j >= 0) {
//             global_comparisons++;
            
//             if (arr[j] > key) {
//                 arr[j + 1] = arr[j];
//                 global_swaps++;
//                 j--;
//             } else {
//                 break;
//             }
//         }
        
//         arr[j + 1] = key;
//     }
// }

// void shellSort(int* arr, int size) {
//     int gap = 1;
//     while (gap < size / 3) {
//         gap = gap * 3 + 1;
//     }
    
//     while (gap >= 1) {
//         for (int i = gap; i < size; i++) {
//             int key = arr[i];
//             int j = i;
            
//             while (j >= gap) {
//                 global_comparisons++;
                
//                 if (arr[j - gap] > key) {
//                     arr[j] = arr[j - gap];
//                     global_swaps++;
//                     j -= gap;
//                 } else {
//                     break;
//                 }
//             }
            
//             arr[j] = key;
//         }
        
//         gap = gap / 3;
//     }
// }

// void heapify(int* arr, int size, int rootIndex) {
//     int largest = rootIndex;
//     int left = 2 * rootIndex + 1;
//     int right = 2 * rootIndex + 2;
    
//     if (left < size) {
//         global_comparisons++;
//         if (arr[left] > arr[largest]) {
//             largest = left;
//         }
//     }
    
//     if (right < size) {
//         global_comparisons++;
//         if (arr[right] > arr[largest]) {
//             largest = right;
//         }
//     }
    
//     if (largest != rootIndex) {
//         int temp = arr[rootIndex];
//         arr[rootIndex] = arr[largest];
//         arr[largest] = temp;
//         global_swaps++;
        
//         heapify(arr, size, largest);
//     }
// }

// void heapSort(int* arr, int size) {
//     for (int i = size / 2 - 1; i >= 0; i--) {
//         heapify(arr, size, i);
//     }
    
//     for (int i = size - 1; i > 0; i--) {
//         int temp = arr[0];
//         arr[0] = arr[i];
//         arr[i] = temp;
//         global_swaps++;
        
//         heapify(arr, i, 0);
//     }
// }

// void countingSort(int* arr, int size) {
//     if (size <= 1) return;
    
//     int maxVal = arr[0];
//     int minVal = arr[0];
//     for (int i = 1; i < size; i++) {
//         global_comparisons += 2;
//         if (arr[i] > maxVal) maxVal = arr[i];
//         if (arr[i] < minVal) minVal = arr[i];
//     }
    
//     int range = maxVal - minVal + 1;
    
//     // 如果范围太大，使用堆排序而非quickSort避免递归
//     if (range > size * 10 || range > 1000000) {
//         heapSort(arr, size);
//         return;
//     }
    
//     int* count = new int[range];
//     for (int i = 0; i < range; i++) {
//         count[i] = 0;
//     }
    
//     for (int i = 0; i < size; i++) {
//         count[arr[i] - minVal]++;
//     }
    
//     int index = 0;
//     for (int i = 0; i < range; i++) {
//         while (count[i] > 0) {
//             arr[index] = i + minVal;
//             global_swaps++;
//             index++;
//             count[i]--;
//         }
//     }
    
//     delete[] count;
// }

// int getMaxDigits(int* arr, int size) {
//     int maxVal = arr[0];
//     for (int i = 1; i < size; i++) {
//         global_comparisons++;
//         if (arr[i] > maxVal) {
//             maxVal = arr[i];
//         }
//     }
    
//     int digits = 0;
//     while (maxVal > 0) {
//         digits++;
//         maxVal /= 10;
//     }
//     return digits;
// }

// void countingSortForRadix(int* arr, int size, int exp) {
//     int* output = new int[size];
//     int count[10] = {0};
    
//     for (int i = 0; i < size; i++) {
//         count[(arr[i] / exp) % 10]++;
//     }
    
//     for (int i = 1; i < 10; i++) {
//         count[i] += count[i - 1];
//     }
    
//     for (int i = size - 1; i >= 0; i--) {
//         output[count[(arr[i] / exp) % 10] - 1] = arr[i];
//         count[(arr[i] / exp) % 10]--;
//         global_swaps++;
//     }
    
//     for (int i = 0; i < size; i++) {
//         arr[i] = output[i];
//         global_swaps++;
//     }
    
//     delete[] output;
// }

// void radixSort(int* arr, int size) {
//     if (size <= 1) return;
    
//     // 检查负数，如果有负数使用堆排序而非quickSort避免递归
//     for (int i = 0; i < size; i++) {
//         if (arr[i] < 0) {
//             heapSort(arr, size);
//             return;
//         }
//     }
    
//     int maxDigits = getMaxDigits(arr, size);
    
//     for (int exp = 1; maxDigits > 0; exp *= 10, maxDigits--) {
//         countingSortForRadix(arr, size, exp);
//     }
// }

// // 简单堆排序作为快速排序的fallback
// void simpleHeapSort(int* arr, int size) {
//     // 构建堆
//     for (int i = size / 2 - 1; i >= 0; i--) {
//         heapify(arr, size, i);
//     }
    
//     // 堆排序
//     for (int i = size - 1; i > 0; i--) {
//         int temp = arr[0];
//         arr[0] = arr[i];
//         arr[i] = temp;
//         global_swaps++;
        
//         heapify(arr, i, 0);
//     }
// }

// // 随机化pivot选择
// int choosePivot(int* arr, int low, int high) {
//     // 三数取中法结合随机化
//     int mid = low + (high - low) / 2;
//     int a = low + rng.nextRange(0, high - low);
//     int b = low + rng.nextRange(0, high - low);
//     int c = low + rng.nextRange(0, high - low);
    
//     global_comparisons += 3;
//     if ((arr[a] <= arr[b] && arr[b] <= arr[c]) || (arr[c] <= arr[b] && arr[b] <= arr[a])) {
//         return b;
//     } else if ((arr[b] <= arr[a] && arr[a] <= arr[c]) || (arr[c] <= arr[a] && arr[a] <= arr[b])) {
//         return a;
//     } else {
//         return c;
//     }
// }

// // 三路快排分割
// void partition3way(int* arr, int low, int high, int& lt, int& gt) {
//     int pivotIndex = choosePivot(arr, low, high);
    
//     // 将pivot移到最后
//     int temp = arr[pivotIndex];
//     arr[pivotIndex] = arr[high];
//     arr[high] = temp;
//     if (pivotIndex != high) global_swaps++;
    
//     int pivot = arr[high];
//     int i = low;
//     lt = low;
//     gt = high;
    
//     while (i <= gt) {
//         global_comparisons++;
        
//         if (arr[i] < pivot) {
//             temp = arr[i];
//             arr[i] = arr[lt];
//             arr[lt] = temp;
//             if (i != lt) global_swaps++;
//             i++;
//             lt++;
//         } else if (arr[i] > pivot) {
//             global_comparisons++;
//             temp = arr[i];
//             arr[i] = arr[gt];
//             arr[gt] = temp;
//             if (i != gt) global_swaps++;
//             gt--;
//         } else {
//             i++;
//         }
//     }
// }

// void quickSortRecursive(int* arr, int low, int high, int depth) {
//     if (low >= high) return;
    
//     // 递归深度限制：当深度过大时切换到堆排序
//     int maxDepth = (int)(2 * log2(high - low + 1));
//     if (depth > maxDepth) {
//         simpleHeapSort(arr + low, high - low + 1);
//         return;
//     }
    
//     // 小数组使用插入排序优化
//     if (high - low + 1 <= 10) {
//         for (int i = low + 1; i <= high; i++) {
//             int key = arr[i];
//             int j = i - 1;
            
//             while (j >= low) {
//                 global_comparisons++;
//                 if (arr[j] > key) {
//                     arr[j + 1] = arr[j];
//                     global_swaps++;
//                     j--;
//                 } else {
//                     break;
//                 }
//             }
//             arr[j + 1] = key;
//         }
//         return;
//     }
    
//     int lt, gt;
//     partition3way(arr, low, high, lt, gt);
    
//     quickSortRecursive(arr, low, lt - 1, depth + 1);
//     quickSortRecursive(arr, gt + 1, high, depth + 1);
// }

// void quickSort(int* arr, int size) {
//     if (size > 1) {
//         quickSortRecursive(arr, 0, size - 1, 0);
//     }
// }

// void merge(int* arr, int left, int mid, int right) {
//     int leftSize = mid - left + 1;
//     int rightSize = right - mid;
    
//     int* leftArr = new int[leftSize];
//     int* rightArr = new int[rightSize];
    
//     for (int i = 0; i < leftSize; i++) {
//         leftArr[i] = arr[left + i];
//     }
//     for (int j = 0; j < rightSize; j++) {
//         rightArr[j] = arr[mid + 1 + j];
//     }
    
//     int i = 0, j = 0, k = left;
    
//     while (i < leftSize && j < rightSize) {
//         global_comparisons++;
        
//         if (leftArr[i] <= rightArr[j]) {
//             arr[k] = leftArr[i];
//             i++;
//         } else {
//             arr[k] = rightArr[j];
//             j++;
//         }
//         global_swaps++;
//         k++;
//     }
    
//     while (i < leftSize) {
//         arr[k] = leftArr[i];
//         global_swaps++;
//         i++;
//         k++;
//     }
    
//     while (j < rightSize) {
//         arr[k] = rightArr[j];
//         global_swaps++;
//         j++;
//         k++;
//     }
    
//     delete[] leftArr;
//     delete[] rightArr;
// }

// void mergeSortRecursive(int* arr, int left, int right) {
//     if (left < right) {
//         int mid = left + (right - left) / 2;
        
//         mergeSortRecursive(arr, left, mid);
//         mergeSortRecursive(arr, mid + 1, right);
        
//         merge(arr, left, mid, right);
//     }
// }

// void mergeSort(int* arr, int size) {
//     if (size > 1) {
//         mergeSortRecursive(arr, 0, size - 1);
//     }
// }

// typedef void (*SortFunction)(int*, int);

// SortFunction sortAlgorithms[ALGORITHM_COUNT] = {
//     bubbleSort,
//     selectionSort,
//     insertionSort,
//     shellSort,
//     quickSort,
//     mergeSort,
//     heapSort,
//     countingSort,
//     radixSort
// };

// double measureTime(SortFunction sortFunc, int* arr, int size) {
//     using namespace std::chrono;
    
//     auto start = high_resolution_clock::now();
//     sortFunc(arr, size);
//     auto end = high_resolution_clock::now();
    
//     auto duration = duration_cast<nanoseconds>(end - start);
//     return duration.count() / 1000000.0;
// }

// PerformanceStats runSingleTest(int algorithmIndex, int size, DataType dataType) {
//     PerformanceStats stats;
    
//     int* testArray = new int[size];
    
//     generateTestData(testArray, size, dataType);
    
//     resetGlobalCounters();
    
//     stats.time_ms = measureTime(sortAlgorithms[algorithmIndex], testArray, size);
    
//     stats.comparisons = global_comparisons;
//     stats.swaps = global_swaps;
    
//     if (!isArraySorted(testArray, size)) {
//         cout << "警告：算法 " << algorithm_names[algorithmIndex] 
//              << " 在数据类型 " << data_type_names[dataType] 
//              << " 规模 " << size << " 的测试中排序失败！" << endl;
//     }
    
//     delete[] testArray;
    
//     return stats;
// }

// PerformanceStats runAverageTest(int algorithmIndex, int size, DataType dataType) {
//     PerformanceStats avgStats;
    
//     for (int i = 0; i < TEST_REPEAT; i++) {
//         PerformanceStats singleStats = runSingleTest(algorithmIndex, size, dataType);
        
//         avgStats.time_ms += singleStats.time_ms;
//         avgStats.comparisons += singleStats.comparisons;
//         avgStats.swaps += singleStats.swaps;
//     }
    
//     avgStats.time_ms /= TEST_REPEAT;
//     avgStats.comparisons /= TEST_REPEAT;
//     avgStats.swaps /= TEST_REPEAT;
    
//     return avgStats;
// }

// struct TestResults {
//     PerformanceStats results[ALGORITHM_COUNT][DATA_TYPE_COUNT][SIZE_COUNT];
    
//     PerformanceStats& getResult(int algorithm, int dataType, int sizeIndex) {
//         return results[algorithm][dataType][sizeIndex];
//     }
// };

// void runAllTests(TestResults& testResults) {
//     cout << "开始排序算法性能测试..." << endl;
//     cout << "测试配置：" << endl;
//     cout << "- 算法数量：" << ALGORITHM_COUNT << endl;
//     cout << "- 数据类型：" << DATA_TYPE_COUNT << endl;
//     cout << "- 数据规模：" << SIZE_COUNT << endl;
//     cout << "- 重复次数：" << TEST_REPEAT << endl;
//     cout << "======================================" << endl;
    
//     int totalTests = ALGORITHM_COUNT * DATA_TYPE_COUNT * SIZE_COUNT;
//     int currentTest = 0;
    
//     auto overallStart = chrono::high_resolution_clock::now();
    
//     for (int alg = 0; alg < ALGORITHM_COUNT; alg++) {
//         cout << endl << "测试算法 [" << (alg + 1) << "/" << ALGORITHM_COUNT << "]：" 
//              << algorithm_names[alg] << endl;
        
//         for (int dt = 0; dt < DATA_TYPE_COUNT; dt++) {
//             cout << "  数据类型：" << data_type_names[dt] << " [";
            
//             for (int sz = 0; sz < SIZE_COUNT; sz++) {
//                 currentTest++;
                
//                 if (sz > 0) cout << " ";
//                 cout << test_sizes[sz];
//                 cout.flush();
                
//                 PerformanceStats result = runAverageTest(alg, test_sizes[sz], (DataType)dt);
//                 testResults.getResult(alg, dt, sz) = result;
                
//                 if (currentTest % 20 == 0) {
//                     double progress = (double)currentTest / totalTests * 100;
//                     cout << " (" << fixed << setprecision(1) << progress << "%)";
//                 }
//             }
//             cout << "] 完成" << endl;
//         }
        
//         auto currentTime = chrono::high_resolution_clock::now();
//         auto elapsed = chrono::duration_cast<chrono::minutes>(currentTime - overallStart);
//         double alg_progress = (double)(alg + 1) / ALGORITHM_COUNT * 100;
//         cout << "算法 " << algorithm_names[alg] << " 测试完成！总进度：" 
//              << fixed << setprecision(1) << alg_progress << "% (用时 " 
//              << elapsed.count() << " 分钟)" << endl;
//     }
    
//     auto overallEnd = chrono::high_resolution_clock::now();
//     auto totalDuration = chrono::duration_cast<chrono::minutes>(overallEnd - overallStart);
    
//     cout << endl << "======================================" << endl;
//     cout << "所有测试完成！" << endl;
//     cout << "总测试数：" << totalTests << endl;
//     cout << "总用时：" << totalDuration.count() << " 分钟" << endl;
//     cout << "======================================" << endl;
// }

// void printFormattedNumber(long long num) {
//     if (num < 1000) {
//         cout << setw(8) << num;
//     } else if (num < 1000000) {
//         cout << setw(6) << fixed << setprecision(1) << (num / 1000.0) << "K";
//     } else if (num < 1000000000) {
//         cout << setw(6) << fixed << setprecision(1) << (num / 1000000.0) << "M";
//     } else {
//         cout << setw(6) << fixed << setprecision(1) << (num / 1000000000.0) << "G";
//     }
// }

// void printFormattedTime(double timeMs) {
//     if (timeMs < 1.0) {
//         cout << setw(8) << fixed << setprecision(3) << timeMs << "ms";
//     } else if (timeMs < 1000.0) {
//         cout << setw(8) << fixed << setprecision(2) << timeMs << "ms";
//     } else {
//         cout << setw(8) << fixed << setprecision(2) << (timeMs / 1000.0) << "s ";
//     }
// }

// void printDetailedResults(const TestResults& testResults) {
//     cout << endl << "======================================" << endl;
//     cout << "          详细性能测试结果表" << endl;
//     cout << "======================================" << endl;
    
//     for (int alg = 0; alg < ALGORITHM_COUNT; alg++) {
//         cout << endl << "算法：" << algorithm_names[alg] << endl;
//         cout << string(60, '-') << endl;
        
//         cout << setw(12) << "数据规模";
//         for (int dt = 0; dt < DATA_TYPE_COUNT; dt++) {
//             cout << setw(12) << data_type_names[dt];
//         }
//         cout << endl;
        
//         cout << string(12 + 12 * DATA_TYPE_COUNT, '-') << endl;
        
//         cout << "执行时间(ms)：" << endl;
//         for (int sz = 0; sz < SIZE_COUNT; sz++) {
//             cout << setw(12) << test_sizes[sz];
//             for (int dt = 0; dt < DATA_TYPE_COUNT; dt++) {
//                 cout << setw(12) << fixed << setprecision(2) 
//                      << testResults.results[alg][dt][sz].time_ms;
//             }
//             cout << endl;
//         }
        
//         cout << endl << "比较次数：" << endl;
//         for (int sz = 0; sz < SIZE_COUNT; sz++) {
//             cout << setw(12) << test_sizes[sz];
//             for (int dt = 0; dt < DATA_TYPE_COUNT; dt++) {
//                 printFormattedNumber(testResults.results[alg][dt][sz].comparisons);
//                 cout << "    ";
//             }
//             cout << endl;
//         }
        
//         cout << endl << "交换次数：" << endl;
//         for (int sz = 0; sz < SIZE_COUNT; sz++) {
//             cout << setw(12) << test_sizes[sz];
//             for (int dt = 0; dt < DATA_TYPE_COUNT; dt++) {
//                 printFormattedNumber(testResults.results[alg][dt][sz].swaps);
//                 cout << "    ";
//             }
//             cout << endl;
//         }
//     }
// }

// void printAlgorithmComparison(const TestResults& testResults, int sizeIndex) {
//     cout << endl << "======================================" << endl;
//     cout << "   算法性能对比表 (数据规模: " << test_sizes[sizeIndex] << ")" << endl;
//     cout << "======================================" << endl;
    
//     cout << setw(12) << "算法名称";
//     for (int dt = 0; dt < DATA_TYPE_COUNT; dt++) {
//         cout << setw(15) << data_type_names[dt];
//     }
//     cout << endl;
//     cout << string(12 + 15 * DATA_TYPE_COUNT, '-') << endl;
    
//     for (int alg = 0; alg < ALGORITHM_COUNT; alg++) {
//         cout << setw(12) << algorithm_names[alg];
//         for (int dt = 0; dt < DATA_TYPE_COUNT; dt++) {
//             cout << setw(12);
//             printFormattedTime(testResults.results[alg][dt][sizeIndex].time_ms);
//             cout << "   ";
//         }
//         cout << endl;
//     }
// }

// void printSimpleBarChart(const TestResults& testResults, int sizeIndex, int dataType) {
//     cout << endl << "======================================" << endl;
//     cout << "  ASCII性能条形图" << endl;
//     cout << "  数据规模: " << test_sizes[sizeIndex] 
//          << ", 数据类型: " << data_type_names[dataType] << endl;
//     cout << "======================================" << endl;
    
//     double maxTime = 0.0;
//     for (int alg = 0; alg < ALGORITHM_COUNT; alg++) {
//         double time = testResults.results[alg][dataType][sizeIndex].time_ms;
//         if (time > maxTime) {
//             maxTime = time;
//         }
//     }
    
//     const int maxBarLength = 50;
    
//     for (int alg = 0; alg < ALGORITHM_COUNT; alg++) {
//         double time = testResults.results[alg][dataType][sizeIndex].time_ms;
//         int barLength = (int)((time / maxTime) * maxBarLength);
        
//         cout << setw(12) << algorithm_names[alg] << " |";
//         for (int i = 0; i < barLength; i++) {
//             cout << "█";
//         }
//         cout << " " << fixed << setprecision(2) << time << "ms" << endl;
//     }
// }

// void analyzeBestWorstCases(const TestResults& testResults) {
//     cout << endl << "======================================" << endl;
//     cout << "           最佳/最差情况分析" << endl;
//     cout << "======================================" << endl;
    
//     for (int alg = 0; alg < ALGORITHM_COUNT; alg++) {
//         cout << endl << "算法：" << algorithm_names[alg] << endl;
//         cout << string(40, '-') << endl;
        
//         for (int sz = 0; sz < SIZE_COUNT; sz++) {
//             double minTime = 1e9, maxTime = 0.0;
//             int bestDataType = -1, worstDataType = -1;
            
//             for (int dt = 0; dt < DATA_TYPE_COUNT; dt++) {
//                 double time = testResults.results[alg][dt][sz].time_ms;
//                 if (time < minTime) {
//                     minTime = time;
//                     bestDataType = dt;
//                 }
//                 if (time > maxTime) {
//                     maxTime = time;
//                     worstDataType = dt;
//                 }
//             }
            
//             cout << "规模 " << setw(8) << test_sizes[sz] << ": "
//                  << "最佳(" << data_type_names[bestDataType] << ") " 
//                  << fixed << setprecision(2) << minTime << "ms, "
//                  << "最差(" << data_type_names[worstDataType] << ") " 
//                  << fixed << setprecision(2) << maxTime << "ms, "
//                  << "比率 " << fixed << setprecision(1) << (maxTime / minTime) << ":1" << endl;
//         }
//     }
// }

// void initializeSystem() {
//     rng.setSeed((unsigned long long)time(nullptr));
    
//     cout << fixed << setprecision(2);
    
//     cout << "========================================" << endl;
//     cout << "     九种排序算法时间复杂度测试程序" << endl;
//     cout << "========================================" << endl;
//     cout << "程序功能：" << endl;
//     cout << "1. 测试9种经典排序算法的性能" << endl;
//     cout << "2. 支持5种不同特性的测试数据" << endl;
//     cout << "3. 涵盖从100到100,000的数据规模" << endl;
//     cout << "4. 统计执行时间、比较次数、交换次数" << endl;
//     cout << "5. 提供详细的性能分析和可视化结果" << endl;
//     cout << "========================================" << endl;
//     cout << endl;
    
//     cout << "测试算法列表：" << endl;
//     for (int i = 0; i < ALGORITHM_COUNT; i++) {
//         cout << (i + 1) << ". " << algorithm_names[i] << endl;
//     }
//     cout << endl;
    
//     cout << "测试数据类型：" << endl;
//     for (int i = 0; i < DATA_TYPE_COUNT; i++) {
//         cout << (i + 1) << ". " << data_type_names[i] << endl;
//     }
//     cout << endl;
    
//     cout << "测试数据规模：";
//     for (int i = 0; i < SIZE_COUNT; i++) {
//         cout << test_sizes[i];
//         if (i < SIZE_COUNT - 1) cout << ", ";
//     }
//     cout << endl << endl;
// }

// void showMenu() {
//     cout << "======================================" << endl;
//     cout << "               操作菜单" << endl;
//     cout << "======================================" << endl;
//     cout << "1. 运行完整测试" << endl;
//     cout << "2. 查看详细结果表格" << endl;
//     cout << "3. 查看算法性能对比" << endl;
//     cout << "4. 查看ASCII性能图表" << endl;
//     cout << "5. 查看最佳/最差情况分析" << endl;
//     cout << "6. 测试单个算法" << endl;
//     cout << "0. 退出程序" << endl;
//     cout << "======================================" << endl;
//     cout << "请选择操作 (0-6): ";
// }

// void testSingleAlgorithm() {
//     cout << endl << "选择要测试的算法：" << endl;
//     for (int i = 0; i < ALGORITHM_COUNT; i++) {
//         cout << i << ". " << algorithm_names[i] << endl;
//     }
//     cout << "请输入算法编号 (0-" << (ALGORITHM_COUNT-1) << "): ";
    
//     int algChoice;
//     cin >> algChoice;
    
//     if (algChoice < 0 || algChoice >= ALGORITHM_COUNT) {
//         cout << "无效的算法编号！" << endl;
//         return;
//     }
    
//     cout << "选择数据规模：" << endl;
//     for (int i = 0; i < SIZE_COUNT; i++) {
//         cout << i << ". " << test_sizes[i] << endl;
//     }
//     cout << "请输入规模编号 (0-" << (SIZE_COUNT-1) << "): ";
    
//     int sizeChoice;
//     cin >> sizeChoice;
    
//     if (sizeChoice < 0 || sizeChoice >= SIZE_COUNT) {
//         cout << "无效的规模编号！" << endl;
//         return;
//     }
    
//     cout << endl << "测试算法：" << algorithm_names[algChoice] 
//          << "，数据规模：" << test_sizes[sizeChoice] << endl;
//     cout << string(50, '-') << endl;
    
//     for (int dt = 0; dt < DATA_TYPE_COUNT; dt++) {
//         PerformanceStats stats = runAverageTest(algChoice, test_sizes[sizeChoice], (DataType)dt);
        
//         cout << data_type_names[dt] << "：" << endl;
//         cout << "  执行时间：" << fixed << setprecision(3) << stats.time_ms << " ms" << endl;
//         cout << "  比较次数：" << stats.comparisons << endl;
//         cout << "  交换次数：" << stats.swaps << endl;
//         cout << endl;
//     }
// }

// int main() {
//     initializeSystem();
    
//     TestResults testResults;
//     bool hasTestResults = false;
    
//     int choice;
//     do {
//         showMenu();
//         cin >> choice;
        
//         switch (choice) {
//             case 1: {
//                 cout << endl << "准备运行完整性能测试..." << endl;
//                 cout << "注意：大数据量测试可能需要较长时间，请耐心等待。" << endl;
//                 cout << "是否继续？(y/n): ";
//                 char confirm;
//                 cin >> confirm;
                
//                 if (confirm == 'y' || confirm == 'Y') {
//                     auto start = chrono::high_resolution_clock::now();
//                     runAllTests(testResults);
//                     auto end = chrono::high_resolution_clock::now();
                    
//                     auto duration = chrono::duration_cast<chrono::seconds>(end - start);
//                     cout << "测试完成！总耗时：" << duration.count() << " 秒" << endl;
//                     hasTestResults = true;
//                 }
//                 break;
//             }
            
//             case 2: {
//                 if (!hasTestResults) {
//                     cout << "请先运行完整测试！" << endl;
//                 } else {
//                     printDetailedResults(testResults);
//                 }
//                 break;
//             }
            
//             case 3: {
//                 if (!hasTestResults) {
//                     cout << "请先运行完整测试！" << endl;
//                 } else {
//                     cout << "选择数据规模进行对比：" << endl;
//                     for (int i = 0; i < SIZE_COUNT; i++) {
//                         cout << i << ". " << test_sizes[i] << endl;
//                     }
//                     cout << "请输入规模编号 (0-" << (SIZE_COUNT-1) << "): ";
//                     int sizeChoice;
//                     cin >> sizeChoice;
                    
//                     if (sizeChoice >= 0 && sizeChoice < SIZE_COUNT) {
//                         printAlgorithmComparison(testResults, sizeChoice);
//                     } else {
//                         cout << "无效的规模编号！" << endl;
//                     }
//                 }
//                 break;
//             }
            
//             case 4: {
//                 if (!hasTestResults) {
//                     cout << "请先运行完整测试！" << endl;
//                 } else {
//                     cout << "选择数据规模：" << endl;
//                     for (int i = 0; i < SIZE_COUNT; i++) {
//                         cout << i << ". " << test_sizes[i] << endl;
//                     }
//                     cout << "请输入规模编号: ";
//                     int sizeChoice;
//                     cin >> sizeChoice;
                    
//                     cout << "选择数据类型：" << endl;
//                     for (int i = 0; i < DATA_TYPE_COUNT; i++) {
//                         cout << i << ". " << data_type_names[i] << endl;
//                     }
//                     cout << "请输入类型编号: ";
//                     int typeChoice;
//                     cin >> typeChoice;
                    
//                     if (sizeChoice >= 0 && sizeChoice < SIZE_COUNT && 
//                         typeChoice >= 0 && typeChoice < DATA_TYPE_COUNT) {
//                         printSimpleBarChart(testResults, sizeChoice, typeChoice);
//                     } else {
//                         cout << "无效的编号！" << endl;
//                     }
//                 }
//                 break;
//             }
            
//             case 5: {
//                 if (!hasTestResults) {
//                     cout << "请先运行完整测试！" << endl;
//                 } else {
//                     analyzeBestWorstCases(testResults);
//                 }
//                 break;
//             }
            
//             case 6: {
//                 testSingleAlgorithm();
//                 break;
//             }
            
//             case 0: {
//                 cout << "程序退出。感谢使用！" << endl;
//                 break;
//             }
            
//             default: {
//                 cout << "无效的选择，请重新输入！" << endl;
//                 break;
//             }
//         }
        
//         if (choice != 0) {
//             cout << endl << "按回车键继续...";
//             cin.ignore();
//             cin.get();
//         }
        
//     } while (choice != 0);
    
//     return 0;
// }
