int main() {
    int a, b, c;
    char *p = 0;
    int *q = 0;
    double *r = 0;
    
    a = (int)(p + 1);
    b = (int)(q + 1);
    c = (int)(r + 1);
    
    printf("%d %d %d", a, b, c);
    
    return 0;
}