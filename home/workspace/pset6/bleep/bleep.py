# Based on CS50/Week6/Sandbox/speller/speller.py

import re
import sys
import time

from cs50 import get_string

# Words in dictionary
words = set()


def main():

    # Check for correct number of args
    if len(sys.argv) != 2:
        print("Usage: bleep [list]")
        sys.exit(1)

    # Benchmarks
    time_load, time_check, time_size, time_unload = 0.0, 0.0, 0.0, 0.0

    # Determine list to use
    list = sys.argv[1]

    # Load list
    before = time.process_time()
    loaded = load(list)
    after = time.process_time()

    # Exit if list not loaded
    if not loaded:
        print(f"Could not load {list}.")
        sys.exit(1)

    # Calculate time to load list
    time_load = after - before

    # Get text to censor
    print("What message would you like to censor?")
    text = get_string()
    textw = text.split()

    # Prepare to check
    word = ""
    index, bleeps, words = 0, 0, 0

    # Check each word string
    for word in textw:
        # Update counter
        words += 1

        # Check word
        before = time.process_time()
        bleep = check(word)
        after = time.process_time()

        # Update benchmark
        time_check += after - before

        # Print *s if bleep
        if bleep:
            for c in word:
                print("*", end="")
            print(" ", end="")
            bleeps += 1
        # Else print word
        else:
            print(f"{word} ", end="")
    print()

    # Determine list's size
    before = time.process_time()
    n = size()
    after = time.process_time()

    # Calculate time to determine list's size
    time_size = after - before

    # Unload list
    before = time.process_time()
    unloaded = unload()
    after = time.process_time()

    # Abort if list not unloaded
    if not unloaded:
        print(f"Could not load {list}.")
        sys.exit(1)

    # Calculate time to determine list's size
    time_unload = after - before

    # Report benchmarks
    #print(f"\nWORDS DETECTED:       {bleeps}")
    #print(f"WORDS IN DICTIONARY:  {n}")
    #print(f"WORDS IN TEXT:        {words}")
    #print(f"TIME IN load:         {time_load:.2f}")
    #print(f"TIME IN check:        {time_check:.2f}")
    #print(f"TIME IN size:         {time_size:.2f}")
    #print(f"TIME IN unload:       {time_unload:.2f}")
    #print(f"TOTAL TIME:           {time_load + time_check + time_size + time_unload:.2f}\n")

    # Success
    sys.exit(0)


# From CS50/Week6/Sandbox/speller/dictionary.py


def check(word):
    # Return true if word is in dictionary else false"""
    return word.lower() in words


def load(dictionary):
    # Load dictionary into memory, returning true if successful else false"""
    file = open(dictionary, "r")
    for line in file:
        words.add(line.strip("\n"))
    file.close()
    return True


def size():
    # Returns number of words in dictionary if loaded else 0 if not yet loaded"""
    return len(words)


def unload():
    # Unloads dictionary from memory, returning true if successful else false"""
    return True


if __name__ == "__main__":
    main()
