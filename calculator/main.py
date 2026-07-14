import sys
from pkg.calculator import Calculator


def main():
    if len(sys.argv) <= 1:
        print("Usage: python main.py '<expression>'")
        return
    expression = " ".join(sys.argv[1:])
    calculator = Calculator()
    result = calculator.evaluate(expression)
    print(f"{expression} = {result}")


if __name__ == "__main__":
    main()
