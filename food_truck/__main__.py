import sys

from food_truck.food_truck import fib

if __name__ == "__main__":
    n = int(sys.argv[1])
    print(fib(n))
