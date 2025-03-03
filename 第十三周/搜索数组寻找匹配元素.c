#include<stdio.h>
int search(const int a[],int n,int key){
    const int *p=a;
    for (int i=0;i<n;i++){
        if (*p==key){
            return 1;
        }
        p++;
    }
    return 0;
}
int main(){
    int search(const int a[],int n,int key);
    int n;
    scanf("%d",&n);
    int a[n];
    int key;
    int b;
    scanf ("%d",&key);
    for (int i;i<n;i++){
        scanf("%d",&a[i]);
    }
    b=search (a,n,key);
    printf("%d\n",b);
    return 0;
}






#include <stdio.h>  

int search(const int a[], int n, int key) {  
    const int *p = a;  // 指针初始位置指向数组的首元素  
    for (int i = 0; i < n; i++) {  
        if (*p == key) {  // 使用指针解引用来访问元素  
            return 1;     // 找到了匹配元素  
        }  
        p++;  // 移动指针到下一个元素  
    }  
    return 0;  // 没有找到匹配元素  
}  

int main() {  
    int n;  
    // 输入数组的大小  
    scanf("%d", &n);  
    
    int a[n];  // 声明数组  

    // 输入数组的元素  
    for (int i = 0; i < n; i++) {  
        scanf("%d", &a[i]);  
    }  

    int key;  
    // 输入要查找的元素  
    scanf("%d", &key);  
    
    // 调用 search 函数并获取返回值  
    int result = search(a, n, key);  

    // 打印结果  
    printf("%d\n", result);  
    
    return 0;  
}