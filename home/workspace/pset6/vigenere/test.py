from cs50 import get_string

c = get_string("input: ")

c_ord = ord(c)
numero = ord(c)
print(numero)
a = ord("a")
z = ord("z")

if c_ord >= ord("a") and numero <= ord("z"):
    n = numero -ord("a")
#if c >= ord("A") and ord(c) <= ord("Z"):
#    n = ord(c) - ord("A")