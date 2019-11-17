#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
    // ensure proper usage
    if (argc != 2)
    {
        fprintf(stderr, "Usage: raw_file\n");
        return 1;
    }

    // remember filename
    char *raw_file = argv[1];

    // open input file
    FILE *file = fopen(raw_file, "r");
    if (file == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", raw_file);
        return 2;
    }

    unsigned char buffer[512];
    char filename[8];
    FILE *img = {0};
    int n = 0;

    //while not the end of the memory card read a block of 512 bytes
    while (fread(buffer, sizeof(buffer), 1, file) == 1)
    {
        //checking for the start of a new jpg
        if (buffer[0] == 0xff &&
            buffer[1] == 0xd8 &&
            buffer[2] == 0xff &&
            (buffer[3] & 0xf0) == 0xe0)
        {
            if (n == 0)
            {
                sprintf(filename, "%03i.jpg", n);
                img = fopen(filename, "w");
            }
            else
            {
                fclose(img);
                sprintf(filename, "%03i.jpg", n);
                img = fopen(filename, "w");
            }
        n++;
        }
        if (n > 0)
        {
            fwrite(buffer, sizeof(buffer), 1, img);
        }
    }
    fclose(img);

    // success
    return 0;
}
