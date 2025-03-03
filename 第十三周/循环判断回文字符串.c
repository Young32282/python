#include<stdio.h>
int palindrome_loop(const char*){
    char c;
    int index = 0;
    // 读取字符直到遇到换行符或数组满
    while ((c = getchar()) != '\n' && index < 99) {
        output[index++] = c;
        input[index++]=c;
    }
    // 添加字符串结束符
    output[index] = '\0';
    input[index]='\0';
    // 逆序存储到同一个数组的开始位置
    int len = strlen(output);
    for (int i = 0; i < len / 2; i++) {
        char temp = output[i];
        output[i] = output[len - i - 1];
        output[len - i - 1] = temp;
    }
    for(int i =0;i<index;i++){
        if(input[i]=output[i])
    }
}



#include <stdio.h>
#include <ctype.h> // 用于tolower函数
#include <string.h>
#include <stdbool.h> // 用于bool类型和true/false宏
 
bool is_palindrome(const char* str) {
    int len = strlen(str);
    for (int i = 0; i < len / 2; i++) {
        if (tolower(str[i]) != tolower(str[len - i - 1])) {
            return false;
        }
    }
    return true;
}
 
int palindrome_loop() {
    char input[100];
    char cleaned[100];
    int clean_index = 0;
    
    printf("请输入一个字符串：");
    fgets(input, sizeof(input), stdin); // 使用fgets来读取整行输入，包括空格
 
    // 预处理输入：忽略空格、标点符号，转换为小写
    for (int i = 0; input[i] != '\0'; i++) {
        if (isalnum(input[i])) { // 如果是字母或数字
            cleaned[clean_index++] = tolower(input[i]);
        }
    }
    cleaned[clean_index] = '\0'; // 添加字符串结束符
 
    // 判断是否是回文
    if (is_palindrome(cleaned)) {
        return 1;
    } else {
        return 0;
    }
}
 
int main() {
    int result = palindrome_loop();
    printf("结果：%d\n", result);
    return 0;
}

------------------------------------------------------------------------------


#include <stdio.h>  
#include <ctype.h>  
#include <string.h>  

int palindrome_loop(const char *str) {  
    // 找到字符串长度  
    int len = strlen(str);  
    
    // 使用两个指针，分别指向字符串的开始和结束  
    int left = 0;  
    int right = len - 1;  

    while (left < right) {  
        // 跳过非字母数字字符  
        while (left < right && !isalnum(str[left])) {  
            left++;  
        }  
        while (right > left && !isalnum(str[right])) {  
            right--;  
        }  
        
        // 转换为小写并比较  
        if (tolower(str[left]) != tolower(str[right])) {  
            return 0; // 不是回文  
        }  
        
        // 移动指针  
        left++;  
        right--;  
    }  

    return 1; // 是回文  
}  

int main() {  
    char input[100]; // 假设输入字符串的最大长度为99  
    printf("请输入字符串：");  
    fgets(input, sizeof(input), stdin); // 安全地读取输入字符串  

    // 移除换行符  
    input[strcspn(input, "\n")] = '\0';   

    // 判断是否为回文并输出结果  
    int result = palindrome_loop(input);  
    printf("%d\n", result);  
    
    return 0;  
}  