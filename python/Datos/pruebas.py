def factorial(n):
    if n == 1:
        return 1
    else:
        return n*factorial(n-1)
    
    
uso = factorial(3)
print(uso)