#include <stdio.h>
int main (){
    char n;
    float  num,temp;
    scanf("%f %c",&num,&n);
    if (n=='f'){
        temp=(5.0/9.0)*(num-32.0);
        printf ("%.2f",temp);
           }
    if (n=='c'){
        temp=(9.0/5.0)*num+32.0;
        printf ("%.2f",temp );
    }
    else{
        printf("ERROR");
    }
    return 0;
}