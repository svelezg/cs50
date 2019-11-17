from sys import argv
from cs50 import get_string


def main():

    # check number of arguments
    if len(argv) == 2:
        # check for alphabets
        if argv[1].isalpha():
            key = argv[1]
        else:
            print("Usage: ./vigenere key")
            exit(1)
    else:
        print("Usage: ./vigenere key")
        exit(1)

    # key length
    l = len(key)

    s = get_string("plain text: ")

    j = 0
    print("ciphertext: ", end="")
    for i in s:
        upper = i.isupper()
        lower = i.islower()

        k = shift(key[j % l])

        # check if it is uppercase
        if (upper != 0):
            char = chr(ord("A") + (ord(i) - ord("A") + k) % 26)
            print(char, end="")
            j = j + 1

        # check if it is lowercase
        if (lower != 0):

            char = chr(ord("a") + (ord(i) - ord("a") + k) % 26)
            print(char, end="")
            j = j + 1

        if (lower + upper == 0):
            print(i, end="")
    print()


# Prompt user for character
def shift(c):
    if ord(c) >= ord("a") and ord(c) <= ord("z"):
        n = ord(c) - ord("a")
    if ord(c) >= ord("A") and ord(c) <= ord("Z"):
        n = ord(c) - ord("A")
    return n


if __name__ == "__main__":
    main()