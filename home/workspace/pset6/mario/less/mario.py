# import get_string from cs50 library
from cs50 import get_int

while True:
    height = get_int("Height: ")
    if height > 0 and height < 9:
        break

# Iterate over height
for i in range(height):

    # leave spaces
    print(" " * (height-i-1), end="")

    # print one more # than in the line before
    print("#"*(i+1))

