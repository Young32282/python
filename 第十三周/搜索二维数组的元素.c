#include<stdio.h>
int search(const int a[][24],int n,int key);
int main(){
    int n;
    scanf("%d",&n);
    int a[n][24];
    for (int i=0;i<n;i++){
        for(int j=0;j<24;j++){
            scanf("%d",&a[i][j]);
        } 
    }
    int key;
    scanf("%d",&key);
    int result=search(a,n,key);
    printf("%d",result);
}
int search(const int a[][24],int n,int key){
    for (int i =0;i<n;i++){
        for(int j=0;j<24;j++){
            if (a[i][j]==key){
                return 1;
            }
        }

    }
    return 0;
}