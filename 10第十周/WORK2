#include <stdio.h>
void pay_amount(int sum,int*twenties,int*tens,int*fives,int*ones){
    int a=sum/20;
    int b=(sum%20)/10;
    int c=((sum%20)%10)/5;
    int d=sum%20%10%5;
    *twenties=a;
    *tens=b;
    *fives=c;
    *ones=d;
    printf("%d %d %d %d\n",*twenties,*tens,*fives,*ones);
}
int main(){
    int sum;
    scanf("%d",&sum);
    int twenties,tens,fives,ones;
    pay_amount(sum,&twenties,&tens,&fives,&ones);
    return 0;
}