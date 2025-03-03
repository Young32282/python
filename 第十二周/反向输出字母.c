#include <stdio.h>  
#include <string.h> // 用于字符串处理函数  

// 函数原型  
void reverse(const char* pi, char* pout);  

int main() {  
    char input[100]; // 假设输入的字符串最大长度为99  
    char output[100]; // 用于保存反向字符串  
    printf("请输入一个字符串: ");  
    scanf("%s", input); // 读取字符串  
    reverse(input, output); // 调用函数进行反向操作  
    printf("反向字符串是: %s\n", output); // 输出结果  
    return 0;  
}  

// 函数实现  
void reverse(const char* pi, char* pout) {  
    int length = strlen(pi); // 获取输入字符串的长度  
          for (int i = 0; i < length; i++) {             
        pout[i] = pi[length - 1 - i]; // 反向赋值  
    }  
    pout[length] = '\0'; // 
}  
























#include<stdio.h>
#include<string.h>
void reverse(char*ch){
        int i =0;
        int j=strlen(ch)-1;
        while (i<j){
            char temp=ch[i];
            ch[i]=ch[j];
            ch[j]=temp;
            i++;
            j--;

        }  
    }
int main(){
    char ch[100];
    scanf("%s",ch);
    reverse(ch);
    printf("%s\n",ch);
    return 0;
}