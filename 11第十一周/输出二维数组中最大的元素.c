#include <stdio.h>  

// 函数原型  
double find_max(double v[][10], int n);  

int main() {  
    double arr[3][10];  
    int n = 3;  

    // 输入三行数据  
    for (int i = 0; i < n; i++) {  
        for (int j = 0; j < 10; j++) {  
            scanf("%lf", &arr[i][j]);  
        }  
    }  

    // 找到最大元素  
    double max_value = find_max(arr, n);  

    // 输出结果，保留两位小数  
    printf("%.2f\n", max_value);  

    return 0;  
}  

// 函数实现  
double find_max(double v[][10], int n) {  
    double max = v[0][0]; // 初始设为第一个元素  

    // 遍历二维数组  
    for (int i = 0; i < n; i++) {  
        for (int j = 0; j < 10; j++) {  
            if (v[i][j] > max) {  
                max = v[i][j]; // 更新最大值  
            }  
        }  
    }  

    return max;  
}
