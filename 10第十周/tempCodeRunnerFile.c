#include<stdio.h>
void swap(int *p,int *q){
    int t=*p;
    *p=*q;
    *q= t;
}
int main(){
    int a,b;
    scanf("%d %d",&a,&b);
    swap( &a,&b);
    printf("%d %d\n",a,b);
    return 0;
}