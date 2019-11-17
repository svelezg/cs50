# import get_float from cs50 library
from cs50 import get_float

# Prompt user for positive float
while True:
    dollars = get_float("Change owed: ")
    if dollars > 0 and dollars < 20000000:
        break

cents = round(dollars * 100)

# Calculate coins of each type and print
quarters = cents // 25
dimes = (cents % 25) // 10
nikels = ((cents % 25) % 10) // 5
pennies = ((cents % 25) % 10) % 5

# Add coins and print
print(f"{quarters + dimes + nikels + pennies}")