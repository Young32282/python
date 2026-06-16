#include<stdio.h>
#include<stdlib.h>
#include<string.h>
char*duplicate(void *p){
    if(p!=NULL){
        char*src = (char *)p; 
    //char*dest=malloc(1*sizeof(*p));
        char *dest = (char *)malloc((strlen(src) + 1) * sizeof(char));
        if (dest==NULL){
            printf("Memory allocation failed");
            return NULL;
        }
    strcpy(dest,src);
    return dest;
    }
}
int main(){
    char str[10000];
    scanf("%s",str);
    char *duplicated_str = duplicate(str);  
    if(duplicated_str!=NULL){
        printf("%s",duplicated_str);
        free(duplicated_str);
    }
    return 0;
}



#include <stdio.h>  
#include <stdlib.h>  
#include <string.h>  

char* duplicate(void *p) {  
    if (p != NULL) {  
        char *src = (char *)p;  

        // 分配内存给 dest  
        char *dest = (char *)malloc((strlen(src) + 1) * sizeof(char));  
        if (dest == NULL) {  
            printf("Memory allocation failed\n");  
            return NULL;  
        }  

        // 复制源字符串到目标字符串  
        strcpy(dest, src);  
        return dest;  // 返回新的字符串  
    }  
    return NULL;  // 如果输入为空，返回 NULL  
}  

int main() {  
    char str[100];  
    printf("Enter a string: ");  
    scanf("%99s", str);  // 读取用户输入，防止溢出  
    
    char *duplicated_str = duplicate(str);  // 复制字符串  

    if (duplicated_str != NULL) {  
        printf("%s\n", duplicated_str);  // 打印复制的字符串  
        free(duplicated_str);  // 释放内存  
    }  

    return 0;  
}