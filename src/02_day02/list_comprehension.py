numbers = []
for i in range(10):
    if i % 2:
        numbers.append(i)
print(f'{numbers=}')

numbers = [i
           for i in range(10)
           if i % 2]
print(f'{numbers=}')
