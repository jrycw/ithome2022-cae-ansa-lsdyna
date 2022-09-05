from random import randint

min_ = min(randint(1, 100)
           for _ in range(10))
print(f'{min_=}')


min1 = (randint(1, 100)
        for _ in range(10))
print(f'{type(min1)=}')
