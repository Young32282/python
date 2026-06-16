#include<stdio.h>
#include<stdlib.h>
#include<string.h>
int main(){
    char**words=malloc(20*sizeof(char*));
    int count =0;
    int capacity=10;

    while(1){
        char input[20+1];
        fgets(input,sizeof(input),stdin);
        input[strcspn(input,"\n")]=0;
        if (strlen(input) == 0) {  
            break;  
        }  
        if (count >= capacity) {  
            capacity *= 2; // 倍增容量  
            words = realloc(words, capacity * sizeof(char *)); 
           
        }  

        // 存储单词  
        words[count] = malloc((strlen(input) + 1) * sizeof(char));  
        if (words[count] == NULL) {  
            printf("内存分配失败！\n");  
            return 1;  
        }  
        
        strcpy(words[count], input); 
        count++; 
     
    }
    //打印单词
    for (int i = 0; i < count; i++) {  
        printf("%s\n", words[i]);  
        free(words[i]);  
    }  

    free(words);  
    return 0;  
}


#include <stdio.h>  
#include <stdlib.h>  
#include <string.h>  

#define MAX_WORD_LENGTH 20  
#define INITIAL_CAPACITY 10  

int main() {  
    char **words = malloc(INITIAL_CAPACITY * sizeof(char *)); // 动态分配指针数组  
    if (words == NULL) { // 检查内存分配是否成功  
        printf("内存分配失败！\n");  
        return 1;  
    }  

    int count = 0; // 存储的单词数量  
    int capacity = INITIAL_CAPACITY; // 当前容量  

    printf("请输入单词（按回车不输入来结束）：\n");  
    
    while (1) {  
        char input[MAX_WORD_LENGTH + 1]; // 输入缓冲区  

        // 读取用户输入并检查是否输入为空  
        fgets(input, sizeof(input), stdin);  
        input[strcspn(input, "\n")] = 0; // 去除输入末尾的换行符  
        
        // 如果输入为空，停止读取  
        if (strlen(input) == 0) {  
            break;  
        }  

        // 如果单词超过最大长度，继续读取  
        if (strlen(input) > MAX_WORD_LENGTH) {  
            printf("单词不能超过 %d 个字符！\n", MAX_WORD_LENGTH);  
            continue;  
        }  

        // 动态调整数组大小  
        if (count >= capacity) {  
            capacity *= 2; // 倍增容量  
            words = realloc(words, capacity * sizeof(char *)); // 重新分配内存  
            if (words == NULL) {  
                printf("内存重新分配失败！\n");  
                return 1;  
            }  
        }  

        // 存储单词  
        words[count] = malloc((strlen(input) + 1) * sizeof(char));  
        if (words[count] == NULL) {  
            printf("内存分配失败！\n");  
            return 1;  
        }  
        
        strcpy(words[count], input); // 复制用户输入的单词  
        count++; // 增加单词计数  
    }  

    // 输出所有存储的单词  
    printf("\n存储的单词：\n");  
    for (int i = 0; i < count; i++) {  
        printf("%s\n", words[i]);  
        free(words[i]); // 释放每个单词的内存  
    }  

    free(words); // 释放指针数组的内存  
    return 0;  
}