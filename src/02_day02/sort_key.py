from operator import itemgetter
from random import randint

numbers = [(i, randint(1, 10))
           for i in range(1, 11)]
print(sorted(numbers, key=itemgetter(1, 0)))
