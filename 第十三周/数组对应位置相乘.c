#include<stdio.h>
double inner_product(const double*a,const double*b,int n);
int main(){
    int n;
    scanf("%d",&n);
    double a[n],b[n];
    const double *p1=a;
    const double *p2=b;
    for (int i=0;i<n;i++){
        scanf("%lf",&*p1);
        p1++;
    }
    for (int i=0;i<n;i++){
        scanf("%lf",&*p2);
        p2++;
    }
    double result =inner_product(a,b,n);
    printf("%.2lf",result);
    return 0;
    }
double inner_product(const double*a,const double*b,int n){
    double result;
    const double *p1=a;
    const double *p2=b; 
    for(int i=0;i<n;i++){
        result+=(*p1)*(*p2);
        p1++;
        p2++;
    }
    return result;
}







#include <stdio.h>  

double inner_product(const double* a, const double* b, int n);  

int main() {  
    int n;  
    scanf("%d", &n);  
    
    double a[n], b[n];  

    double* p1 = a;  
    double* p2 = b;  

    // 输入数组 a  
    for (int i = 0; i < n; i++) {  
        scanf("%lf", p1);  // 使用 %lf 读取 double 类型  
        p1++;               // 移动指针  
    }  

    // 输入数组 b  
    for (int i = 0; i < n; i++) {  
        scanf("%lf", p2);  // 使用 %lf 读取 double 类型  
        p2++;               // 移动指针  
    }  

    // 调用内积函数并保存返回值  
    double result = inner_product(a, b, n);  
    // 打印结果，保留两位小数  
    printf("%.2lf\n", result);  

    return 0;  
}  

double inner_product(const double* a, const double* b, int n) {  
    double result = 0.0;  // 初始化 result 为 0  
    const double* p1 = a;  
    const double* p2 = b;   

    for (int i = 0; i < n; i++) {  
        result += (*p1) * (*p2); // 指针解引用来获取元素值  
        p1++; // 移动指针  
        p2++; // 移动指针  
    }  

    return result; // 返回内积结果  
}