 #include<stdio.h>
 #include<stdlib.h>
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
double sum(double** matrix,int M,int N){
    double sum1=0.0;
    for(int i =0;i<M;i++){
        for (int j=0;j<N;j++){
            sum1 +=matrix[i][j];
        }
    }
    return sum1;
}
int main(){
    int N,M;
    scanf("%d",&M);
    scanf("%d",&N);
    double **matrix = random_matrix(M, N);
    double sum2=sum(matrix,M,N);  
    printf("%.4lf",sum2);
    free_matrix(matrix, M);  
    return 0;
}