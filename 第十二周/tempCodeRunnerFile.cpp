#include <stdio.h>  
#include <string.h>  

void delChar(char* str, int num_to_delete, int start_position) {  
    int length = strlen(str);  

    // 如果起始位置超出字符串长度，或者要删除的字符数为0  
    if (start_position >= length || num_to_delete <= 0) {  
        return; // 不做任何操作  
    }  

    // 计算实际删除的字符数，确保不超过剩余字符  
    int end_position = start_position + num_to_delete;  
    if (end_position > length) {  
        end_position = length; // 确保不越界  
    }  
    
    // 计算删除后的新字符串起始位置  
    int new_length = length - (end_position - start_position);  
    
    // 将需要删除的部分后的字符串移到 start_position 处  
    memmove(&str[start_position], &str[end_position], new_length - start_position + 1);  

    // 截断字符串  
    str[new_length] = '\0'; // 添加字符串结束符  
}  

int main() {  
    char str[100]; // 用于存储输入的字符串  

    // 接收用户输入  
    printf("请输入字符串: ");  
    fgets(str, sizeof(str), stdin);  
    
    // 去掉输入字符串末尾的换行符  
    str[strcspn(str, "\n")] = 0;  

    int num_to_delete;      // 要删除的字符数量  
    int start_position;     // 删除的起始位置  
    
    printf("请输入要删除的字符数量: ");  
    scanf("%d", &num_to_delete);  
    
    printf("请输入开始删除的位置: ");  
    scanf("%d", &start_position);  

    // 调用删除字符的函数  
    delChar(str, num_to_delete, start_position);  

    // 输出新的字符串  
    printf("结果字符串: %s\n", str);  

    return 0;  
}  