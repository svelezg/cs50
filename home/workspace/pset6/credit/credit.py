# import get_string from cs50 library
from cs50 import get_string

while True:
    number = get_string("Card Number: ")
    # check for non numeric imput
    if number.isdigit():
        num = int(number)
        # check for valid range
        if num > 0 and num < 10**17:
            break
# initialice variables

suma = 0
senc = 0
s = 0
# initialize  according to string lenght
n = len(number) % 2

# iterate over digits
for d in number:
    n = n + 1

    # switch over digits
    if (n % 2 != 0):
        s = 2 * int(d)

        # for two digists numbers
        if (s > 9):
            suma = suma + (1 + (s - 10))

        # for one digit numbers
        else:
            suma = suma + s

    else:
        senc = senc + int(d)

    # print(f"n: {n}; d: {d}; s: {s}; suma:{suma}")

check = suma + senc
# print("Check", check)

# only if check ends in cero
if (check % 10 == 0):
    testA = num // (10 ** 15)
    testB = num // (10 ** 14)
    testC = num // (10 ** 13)
    testD = num // (10 ** 12)

    # print(f"{testA}, {testB}, {testC}")

    # AMEX test
    if(testC == 34 or testC == 37):
        print("AMEX")

    # MASTERCARD test
    elif ((testB > 50 and testA < 56) or (testB == 22)):
        print("MASTERCARD")

    # VISA test
    elif (testA == 4 or testD == 4):
        print("VISA")

else:
    print("INVALID")

