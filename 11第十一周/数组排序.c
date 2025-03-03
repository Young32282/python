#include<stdio.h>
#include<stdlib.h>
double  suijishu(){
    return (double)rand()/(double)RAND_MAX;
}
int main(){
    srand(1024);
    double raw[10];
    for (int i =0;i<10;i++){
         double randnum=suijishu();
        raw[i]=randnum;
    }
    for(int i=0;i<10;i++){
        for (int j=0;j<10;j++){
            if (raw[j]>raw[j+1]){
                double temp=raw[j];
                raw[j]=raw[j+1];
                raw[j+1]=temp;
            }
        }
    }
    for (int i=0;i<10;i++){
        printf("%.4f",raw[i]);
        if (i < 9) {  
            printf(" "); // 在每两个数字之间用空格分隔 1、2区别没排序 
        }  
    }
    return 0;
}