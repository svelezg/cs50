#include <cs50.h>
#include <stdio.h>
int main (void)
{
    int i = get_int("i: ");
    int j = get_int("j: ");

    if (i == j)
    {
        printf("same\n");
    }
    else
    {
        printf("different\n");
    }
}