```python
while True:
    try:
        a = float(input("Enter first number: "))
        op = input("Choose operation (+, -, *, /): ").strip()
        b = float(input("Enter second number: "))
        if op == '+':
            print(f"{a} + {b} = {a + b}")
        elif op == '-':
            print(f"{a} - {b} = {a - b}")
        elif op == '*':
            print(f"{a} * {b} = {a * b}")
        elif op == '/':
            if b == 0:
                print("Error: Division by zero")
            else:
                print(f"{a} / {b} = {a / b}")
        else:
            print("Invalid operation")
        again = input("Calculate again? (y/n): ").strip()
        if again.lower() != 'y':
            break
    except ValueError:
        print("Error: Invalid input")
```