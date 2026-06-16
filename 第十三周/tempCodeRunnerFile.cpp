
#include <stdio.h>  

void find_two_largest(const int *a, int n, int *largest, int *second_largest) {  
    if (n < 1) return;  // 数组长度小于1，直接返回  

    const int *end = a + n; // 指向数组末尾的指针  
    *largest = *second_largest = *a; // 初始化最大和第二大元素为数组第一个元素  

    for (const int *p = a + 1; p < end; p++) {  
        if (*p > *largest) {  
            // 找到新的最大值  
            *second_largest = *largest; // 更新第二大值  
            *largest = *p; // 更新最大值  
        } else if (*p > *second_largest) {  
            // 找到新的第二大值  
            *second_largest = *p; // 更新第二大值  
        }  
    }  
}  

int main() {  
    int n;  
    scanf("%d", &n); // 输入数组长度  
    int arr[n];  
    
    // 输入数组元素  
    for (int i = 0; i < n; i++) {  
        scanf("%d", &arr[i]);  
    }  

    int largest, second_largest;  
    find_two_largest(arr, n, &largest, &second_largest);  
    
    // 输出最大的元素和第二大的元素  
    printf("%d %d\n", largest, second_largest);  
    
    return 0;  
}