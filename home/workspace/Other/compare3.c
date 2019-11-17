#include <cs50.h>
#include <stdio.h>
#include <string.h>

bool compare_strings(char *a, char *b);

int main (void)
{
    char *s = get_string("s: ");
    char *t = get_string("t: ");

    if (compare_strings(s , t))
    {
        printf("same\n");
    }
    else
    {
        printf("different\n");
    }
}

bool compare_strings(char *a, char *b)
{
    if (strlen(a) != strlen(b))
    {
        return false;
    }
    for (int i = 0, n = strlen(a); i < n; i++)
    {
        if (a[i] != b[i])
        {
            return false;
        }
    }
    return true;
}