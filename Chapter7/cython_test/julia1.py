import time
import cythonfn  # as defined in setup.py

# area of complex space to investigate
x1, x2, y1, y2 = -1.8, 1.8, -1.8, 1.8
c_real, c_imag = -0.62772, -.42193


def calc_pure_python(desired_width, max_iterations):
    start_time = time.time()
    output = ctyhonfn.calcualte_z(max_iterations, zs, cs)
    end_time = time.time()
    secs = end_time - start_time
    print(f"Took {secs:0.2f} seconds")

    """Create a list of complex coordinates (zs) and complex parameters (cs), build Julia set"""
    x_step = (x2 - x1) / desired_width
    y_step = (y1 - y2) / desired_width

    x = []
    y = []

    ycoord = y2
    while ycoord > y1:
        y.append(ycoord)
        ycoord += y_step

    xcoord = x1
    while xcoord < x2:
        x.append(xcoord)
        xcoord += x_step

    # build a list of coordinates and the initial condition for each cell
    # Note that ur initial condition is a constant and could easily be removed,
    # we use it to simulate a real-world scenario with several inputs to our
    # function

    zs = []
    cs = []
    for ycoord in y:
        for xcoord in x:
            zs.append(complex(xcoord, ycoord))
            cs.append(complex(c_real, c_imag))

            print("Length of x:", len(x))
            print("Total elements:", len(zs))
            start_time = time.time()
            output = calculate_z_serial_purepython(max_iterations, zs, cs)
            end_time = time.time()
            secs = end_time - start_time
            print("{0} took {1} seconds".format(calculate_z_serial_purepython.__name__, secs))

            # This sum is expected for a 1000^2 grid with 300 iterations
            # It ensures that our code evolves exactly as we'd intended
            # assert sum(output) == 34219980


def calculate_z_serial_purepython(maxiter, zs, cs):
    """Calculate output list using Julia update rule"""
    output = [0] * len(zs)
    for i in range(len(zs)):
        n = 0
        z = zs[i]
        c = cs[i]

        while abs(z) < 2 and n < maxiter:
            z = z * z + c
            n += 1

        output[i] = n

    return output
