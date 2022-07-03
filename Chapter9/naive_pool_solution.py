import math


def check_prime(n):
    from_i = 3
    to_i = math.sqrt(n) + 1
    ranges_to_check = create_range.create(from_i, to_i, nbr_processes)
    ranges_to_check = zip(len(ranges_to_check) * [n], ranges_to_check)
    assert len(ranges_to_check) == nbr_proceses
    results = pool.map(check_prime_in_range, ranges_to_check)

    if False in results:
        return False

    return True
