from cffi import FFI, verifier

grid_shape = (512, 512)

ffi = FFI()

ffi.cdef(
    "void evolve(double **in, double **out, double D, double dt);"
)
lib = ffi.dlopen("../diffusion.so")

def evolve(grid, dt, out, D=1.0):
    pointer_grid = ffi.cast("double**", grid.ctypes.data)
    pointer_out = ffi.cast("double**", out.ctypes.data)

    lib.evolve(pointer_grid, pointer_out, D, dt)