#include<stdio.h>
int digit(int n,int k){
    int i;
    for (i=0;i<k-1;i++){
        n/=10;
    }
    return n%10;   
}
int main (){
    int n,k;
    scanf("%d %d",&n,&k);
    printf("%d\n",digit(n,k));
    return 0;
}