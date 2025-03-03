#include <stdio.h>  

struct Stock {  
    char name[11];
    double earningsPerShare;
    double priceToEarningsRatio; 
};  

int main() {  
    struct Stock stocks[5]; 
    double predictedPrice;  

    for (int i = 0; i < 5; i++) {  
        scanf("%s %lf %lf", stocks[i].name, &stocks[i].earningsPerShare, &stocks[i].priceToEarningsRatio);  
    }  
    for (int i = 0; i < 5; i++) {  
        predictedPrice = stocks[i].earningsPerShare * stocks[i].priceToEarningsRatio; 
        printf("%s: %.2lf\n", stocks[i].name, predictedPrice); 
    }  

    return 0;  
}