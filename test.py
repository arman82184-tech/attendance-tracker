n = int(input('Enter a number :'))
i = 2
count = 0
while i<n :
    if n%i == 0 :
        count += 1
    i += 1

if count == 0 :
    print(f'{n} is a prime number.')
else :
    print(f'{n} is not a prime number.')