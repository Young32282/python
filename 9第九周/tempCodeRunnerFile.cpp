#include<stdio.h>
void daoxu(int x){
    if(x==0){
      return ;
    }
    printf("%d",x%10);
    daoxu(x/10);
}
int main(){
    int x;
    scanf("%d",&x);
    daoxu(x);
    return 0;
}