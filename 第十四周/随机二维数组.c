#include <stdio.h>  
#include <stdlib.h>  
#include <time.h>  
double ** random_matrix(int M, int N);
int main() {  
    int M, N;  
    scanf("%d", &M);  
    scanf("%d", &N);  
    double **matrix = random_matrix(M, N);  
    for (int i = 0; i < M; i++) {  
        for (int j = 0; j < N; j++) {  
            printf("%.4f ", matrix[i][j]);  
        }  
        printf("\n");  
    }  
    free_matrix(matrix, M);  

    return 0;  
}  
double ** random_matrix(int M, int N) {  
    double **matrix = malloc(M * sizeof(double *));  
    // 为每行分配列的内存  
    for (int i = 0; i < M; i++) {  
        matrix[i] = malloc(N * sizeof(double));  
    }  

    // 设置随机数种子  
    srand(1024);  

    // 填充二维数组  
    for (int i = 0; i < M; i++) {  
        for (int j = 0; j < N; j++) {  
            matrix[i][j] = (double) rand() / RAND_MAX; // 生成 0 到 1 之间的随机数  
        }  
    }  

    return matrix;  
}  

void free_matrix(double **matrix, int M) {  
    for (int i = 0; i < M; i++) {  
        free(matrix[i]); 
    }  
    free(matrix); 
}  