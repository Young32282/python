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
        yushu*=10
        int xiaoshu =yushu/divisor;
        sprintf(&result[p],"%d",xiaoshu);
        yushu=yushu%divisor;
        p++;
    }   
    result[p]='\0';
    return result;
}
