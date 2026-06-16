#include<stdio.h>
#include<string.h>
void read_and_reverse(const char* str,char *output);
int main(){
    char str[100];
    scanf("%s",str);
    char output[100];
    read_and_reverse(str,output);
    printf("%s\n",output);
    return 0;
}
void read_and_reverse(const char* str,char *output){
    int len =strlen(str);    
    int j=0;
    for (int i=len-1;i>=0;i--){
        output[j++]=str[i];
    }
    output[j]='\0';
}

