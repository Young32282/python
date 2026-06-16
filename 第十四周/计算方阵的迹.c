#include <stdio.h>  
#include <stdlib.h>  

double **random_matrix(int M, int N) {  
    double **matrix = malloc(M * sizeof(double *));   
    for (int i = 0; i < M; i++) {  
        matrix[i] = malloc(N * sizeof(double));  
    }
    srand(1024);  
    for (int i = 0; i < M; i++) {  
        for (int j = 0; j < N; j++) {  
            matrix[i][j] = (double)rand() / RAND_MAX; 
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
 
double tr(double **matrix, int N) {  
    double trace = 0.0;
    for (int i = 0; i < N; i++) {  
        trace += matrix[i][i]; 
    }  
    return trace;  
}  

int main() {  
    int N;  
    scanf("%d", &N);  
    double **matrix = random_matrix(N, N);  
    if (matrix == NULL) {  
        return 1; 
    }  
    double trace = tr(matrix, N);  
    printf("%.4f\n", trace);  
    free_matrix(matrix, N);  
    return 0;  
}