# TEST CASES WITHOUT ERRORS

#------------------------------------------------------
# TEST CASE 1 

player_level = 10
boss_level = 20

if player_level < boss_level:
    level_gap = boss_level - player_level
    print(level_gap)
else:
    print(0)

#------------------------------------------------------
# TEST CASE 2 

piggy_bank = 0

for coins in range(1, 6):
    piggy_bank = piggy_bank + coins

print(piggy_bank)

#------------------------------------------------------
# TEST CASE 3

def count_chocolate_squares(length, width):
    total_squares = length * width
    return total_squares

bar_length = 10
bar_width = 5

deliciousness = count_chocolate_squares(bar_length, bar_width)
print(deliciousness)

#------------------------------------------------------

#===================================================================================================================================

# TEST CASES WITH ERRORS

#------------------------------------------------------
# TEST CASE 1

item_cost = 100
currency = '$'  # replace '$' with $ to test this case

#------------------------------------------------------
# TEST CASE 2

item_price = 10

total_cost = item_price + shipping_fee

#------------------------------------------------------
# TEST CASE 3

def check_username(user):
    return "User found: " + user

status = check_username("admin_user", "1234pass")

#------------------------------------------------------