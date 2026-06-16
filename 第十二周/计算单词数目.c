#include <string.h>
#include <stdio.h>

int count_words(char* sentence) {
    if (sentence == NULL) {
        return 0; // 如果传入的指针为空，返回0
    }

    int num = 0; // 初始化单词计数为0
    char *space = strchr(sentence, ' ');

    while (space != NULL) {
        // 如果空格后不是字符串的结尾，并且空格后不是另一个空格，则增加单词计数
        if (*(space + 1) != ' ' && *(space + 1) != '\0') {
            num++;
        }
        // 更新 space 指针，确保不会超出字符串边界
        space = strchr(space + 1, ' ');
    }

    // 如果句子不是空的，或者不以空格开头，则至少有一个单词
    if (sentence[0] != ' ' && sentence[0] != '\0') {
        num++;
    }

    return num;
}

int main() {
    char sentence[50];
    if (fgets(sentence, sizeof(sentence), stdin) == NULL) {
        return 1; // 如果读取失败，退出程序
    }
    // 移除可能的换行符
    sentence[strcspn(sentence, "\n")] = '\0';
    printf("%d\n", count_words(sentence));
    return 0;
}
