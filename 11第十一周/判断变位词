#include <stdio.h>  
#include <string.h>  

int anagram(char w1[], char w2[], int n) {  
    int count1[26] = {0}; // 用于记录 w1 中每个字母的出现次数  
    int count2[26] = {0}; // 用于记录 w2 中每个字母的出现次数  

    // 遍历第一个单词，统计每个字母的出现次数  
    for (int i = 0; i < n; i++) {  
        count1[w1[i] - 'a']++; // 将字符转为对应的数组索引  
    }  

    // 遍历第二个单词，统计每个字母的出现次数  
    for (int i = 0; i < n; i++) {  
        count2[w2[i] - 'a']++;  
    }  

    // 比较两个字符计数数组  
    for (int i = 0; i < 26; i++) {  
        if (count1[i] != count2[i]) { // 如果不同，返回0  
            return 0;  
        }  
    }  
    
    return 1; // 如果所有字符出现次数相同，返回1  
}  

int main() {  
    char w1[101]; // 假设单词长度不超过100  
    char w2[101]; // 假设单词长度不超过100  

    // 输入两个单词  
    printf("请输入两个单词：\n");  
    scanf("%s", w1);  
    scanf("%s", w2);  

    // 检查单词长度是否相等  
    if (strlen(w1) != strlen(w2)) {  
        printf("0\n"); // 长度不同，必定不是变位词  
        return 0;  
    }  

    // 调用 anagram 函数并输出结果  
    int result = anagram(w1, w2, strlen(w1));  
    printf("%d\n", result);  

    return 0;  
}  
