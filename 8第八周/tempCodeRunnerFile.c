#include <stdio.h>
int num_digits(int n) {
    int count = 0;
    while (n > 0) {
        n /= 10;  
        count++;  
    }
    return count;
}

int main() {
    int n;
    scanf("%d",&n);
    printf("%d", num_digits(n));
    return 0;
}