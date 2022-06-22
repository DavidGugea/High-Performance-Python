def binary_search(needle, haystack):
    imin, imax = 0, len(haystack)

    while True:
        if imin > imax:
            return -1

        midpoint = (imin + imax) // 2

        if haystack[midpoint] > needle:
            imax = midpoint
        elif haystack[midpoint] < needle:
            imin = midpoint + 1
        else:
            return midpoint
