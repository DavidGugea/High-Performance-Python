def fibonacci_naive():
    i, j = 0, 1
    count = 0
    while j <= 5000:
        if j % 2:
            count += 1

        i, j = j, i + j

    return count


def fibonacci_transform():
    count = 0
    for f in fibonacci():
        if f > 50000:
            break

        if f % 2:
            count += 1

    return count


from itertools import takewhile


def fibonacci_succinct():
    first_5000 = takewhile(lambda x: x <= 5000, fibonacci())
    return sum(1 for x in first_5000 if x % 2)
