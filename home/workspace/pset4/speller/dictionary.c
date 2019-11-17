// Implements a dictionary's functionality

#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <cs50.h>
#include <strings.h>
#include <string.h>

#include "dictionary.h"

// Represents number of buckets in a hash table
#define N 26

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node;

// Represents a hash table
node *hashtable[N];

// Hashes word to a number between 0 and 25, inclusive, based on its first letter
unsigned int hash(const char *word)
{
    return tolower(word[0]) - 'a';
}

// Loads dictionary into memory, returning true if successful else false
bool load(const char *dictionary)
{
    // Initialize hash table
    for (int i = 0; i < N; i++)
    {
        hashtable[i] = NULL;
    }

    // Open dictionary
    FILE *file = fopen(dictionary, "r");
    if (file == NULL)
    {
        unload();
        return false;
    }

    // Buffer for a word
    char word[LENGTH + 1];

    // Insert words into hash table
    while (fscanf(file, "%s", word) != EOF)
    {
        // TODO
        // Allocate space for word
        node *w = malloc(sizeof(node));
        if (!w)
        {
            return 1;
        }

        // Add word to list
        strcpy(w->word, word);
        w->next = NULL;

        // hash word
        unsigned int h = hash(w->word);

        //if (node *hashtable[h])
        if (hashtable[h])
        {
            for (node *ptr = hashtable[h]; ptr != NULL; ptr = ptr->next)
            {
                if (!ptr->next)
                {
                    ptr->next = w;
                    break;
                }
            }
        }
        else
        {
            hashtable[h] = w;
        }
        int count;
    }

    // Close dictionary
    fclose(file);

    // Indicate success
    return true;
}

// Returns number of words in dictionary if loaded else 0 if not yet loaded
unsigned int size(void)
{
    unsigned int count = 0;
    for (int n = 0; n < N; n++)
    {
        node *cursor = hashtable[n];
        while (cursor != NULL)
        {
            count++;
            node *temp = cursor;
            cursor = cursor->next;
        }
    }
    return count;
}

// Returns true if word is in dictionary else false
bool check(const char *word)
{
    unsigned int h = hash(word);
    node *cursor = hashtable[h];
    while(cursor != NULL)
    {
        if (strcasecmp(word, cursor->word) == 0)
        {
            return true;
            break;
        }
        else
        {
            cursor = cursor->next;
        }
    }
return false;
}

// Unloads dictionary from memory, returning true if successful else false
    // Free memory
bool unload(void)
{
    for (int n = 0; n < N; n++)
    {
        node *cursor = hashtable[n];
        while (cursor != NULL)
        {
            node *temp = cursor;
            cursor = cursor->next;
            free(temp);
        }
    }
    return true;
}
