c = -0.62772-0.42193j
z = 0+0j
for n in range(9):
    z = z*z + c
    print(f"{n}: z={z:.5f}, abs(z)={abs(z):0.3f}, c={c:.5f}")