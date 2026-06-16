#include<stdio.h>
#include<stdlib.h>
#include<string.h>
char*division(int dividend,int divisor,int resolution);
int main(){
    int dividend,divisor,resolution;
    scanf("%d",&dividend);
    scanf("%d",&divisor );
    scanf("%d",&resolution);
    char*D= division(dividend,divisor,resolution);
    printf("%s",D);
    free(D);
    return 0;



}
char*division(int dividend,int divisor,int resolution){
    char*result=malloc(resolution+10);
    int zhengshu =dividend/divisor;
    int yushu =dividend%divisor;
    //整数
    sprintf(result,"%d.",zhengshu);
    int p=strlen(result);
    //小数
    for (int i=0;i<resolution;i++){
        yushu*=10;
        int xiaoshu =yushu/divisor;
        sprintf(&result[p],"%d",xiaoshu);
        yushu=yushu%divisor;
        p++;
    }   
    result[p]='\0';
    return result;
}

#include <stdio.h>  
#include <stdlib.h>  
#include<string.h>

char* division(int dividend, int divisor, int resolution) {  
    // 分配结果字符串，最多需要 `resolution + 2` 位（整数部分 + 小数点 + 小数部分）  
    char* result = malloc(resolution + 3); // +3 for "0." and '\0'  
    // 计算整数部分  
    int integerPart = dividend / divisor;  
    int remainder = dividend % divisor;  
    // 格式化结果的整数部分到字符串  
    sprintf(result, "%d.", integerPart); // write integer part + "."
    int pos=strlen(result); 

    // 计算小数部分并填写到结果字符串  
    for (int i = 0; i < resolution; i++) {  
        remainder *= 10; // 乘以 10 来计算下一个小数位  
        int decimalDigit = remainder / divisor; // 当前小数位  
        remainder = remainder % divisor; // 新的余数  

        // 将小数位添加到结果字符串  
        result[pos++] = decimalDigit + '0'; // 转为字符并写入结果字符串  
    }  
    
    result[pos] = '\0'; // 结束字符串  
    return result; // 返回结果字符串  
}  

int main() {  
    int dividend, divisor, resolution;  
    
    // 输入被除数、除数和精度  
    printf("请输入被除数：");  
    scanf("%d", &dividend);  
    
    printf("请输入除数：");  
    scanf("%d", &divisor);  
    
    printf("请输入小数位数：");  
    scanf("%d", &resolution);  
    
    // 调用 division 函数  
    char* result = division(dividend, divisor, resolution);  
    if (result != NULL) {  
        // 打印结果  
        printf("%s\n", result);  
        free(result); // 释放分配的内存  
    }  
    
    return 0;  
}