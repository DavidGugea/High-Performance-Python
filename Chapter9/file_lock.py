def work(filename, max_count):
    for n in range(max_count):
        f = open(filename, "r")

        try:
            nbr = int(f.read())
        except ValueError as err:
            print("File is empty, starting to count from 0, error: {0}".format(err))
            nbr = 0

        f = open(filename, "w")
        f.write(str(nbr + 1) + "\n")
        f.close()
