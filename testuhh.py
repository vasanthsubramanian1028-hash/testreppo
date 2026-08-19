n = int(input("Enter the age: "))
if n >= 18:
    print("You are above 18 years old and give me a moment let me check your access")
    key = True
    if key:
        print("you have the access")
    else:
        print("you don't have the access")
else:
    print("you are below 18 years old and you don't have the access")
