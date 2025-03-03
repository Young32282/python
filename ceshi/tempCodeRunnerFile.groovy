#include <stdio.h>
int gcd(int m, int n) {
    int temp;
    while (n != 0) {
        temp = m % n;
        m = n;
        n = temp;
    }
    return m;
}

int main() {
    int num1, num2, result;
    scanf("%d %d", &num1, &num2);
    result = gcd(num1, num2);
    printf("%d\n", result);

    return 0;
}