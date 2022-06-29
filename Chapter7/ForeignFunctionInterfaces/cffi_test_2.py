from cffi import FFI, verifier

grid_shape = (512, 512)

ffi = FFI()

ffi.cdef(
    "void evolve(double **in, double **out, double D, double dt);"
)
lib = ffi.dlopen("../diffusion.so")

lib = ffi.verify(
    r"""
        void evolve(double in[][512], double out[][512], double D, double dt) {
            int i, j;
            double laplacian;

            for(i = 1 ; i < 511; i++) {
                for (j = 1 ; j < 511;j++) {
                    laplacian = in[i+1][j] + in[i-1][j] + in[i][j+1] + in[i][j-1] - 4 * in[i][j];
                    out[i][j] = in[i][j] + D * dt * laplacian;
                }
            }
        }
    """,
    extra_compile_args = ["-03"]
)