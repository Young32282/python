#include<stdio.h>
double average(double v[],int length){
    double sum=0;
    for (int i=0;i<length;i++){
        sum+=v[i];
    }
    double ave= sum/length;
    return ave;
}
int main(){
    double v[5];
    int length=sizeof(v)/sizeof(v[0]);
    for (int i=0;i<5;i++){
        scanf("%lf",&v[i]);
    }
    printf("%.2f\n",average(v,length));
    return 0;
}
