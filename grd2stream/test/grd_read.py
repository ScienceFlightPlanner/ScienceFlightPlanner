import ctypes
import os

# Load shared library
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
lib_path = os.path.join(base_dir, "grd2stream", "bin", "linux", "grd2stream.so")
if not os.path.exists(lib_path):
    raise FileNotFoundError(f"Shared library not found at: {lib_path}")
grd2stream = ctypes.CDLL(lib_path)
print(f"Loaded shared library from: {lib_path}")

# grdread function signature
grd2stream.grdread.argtypes = [
    ctypes.c_char_p,  # filename
    ctypes.POINTER(ctypes.c_size_t),  # nx (number of x points)
    ctypes.POINTER(ctypes.c_size_t),  # ny (number of y points)
    ctypes.POINTER(ctypes.POINTER(ctypes.c_double)),  # x-coordinates
    ctypes.POINTER(ctypes.POINTER(ctypes.c_double)),  # y-coordinates
    ctypes.POINTER(ctypes.POINTER(ctypes.c_double))   # grid data (z)
]
grd2stream.grdread.restype = ctypes.c_int  # Return code

dataset_file = os.path.join(os.getcwd(), "datasets", "GL_vel_mosaic_simulated.grd")  # SET PATH HERE

# Output variables
nx = ctypes.c_size_t()  # Number of x points
ny = ctypes.c_size_t()  # Number of y points
pp_x = ctypes.POINTER(ctypes.c_double)()  # Pointer to x coordinates
pp_y = ctypes.POINTER(ctypes.c_double)()  # Pointer to y coordinates
pp_z = ctypes.POINTER(ctypes.c_double)()  # Pointer to grid data

# grdread function call
result = grd2stream.grdread(dataset_file.encode('utf-8'), ctypes.byref(nx), ctypes.byref(ny), ctypes.byref(pp_x), ctypes.byref(pp_y), ctypes.byref(pp_z))

# Check
if result == 0:
    print(f"\ngrdread successful! Dimensions: {nx.value} x {ny.value}")
    
    # Convert pointers to Python lists
    x = [pp_x[i] for i in range(nx.value)]
    y = [pp_y[i] for i in range(ny.value)]
    z = [pp_z[i] for i in range(nx.value * ny.value)]

    # Print a preview of the grid data
    print(f"x: {x[:5]} ...")  # First 5 x-coordinates
    print(f"y: {y[:5]} ...")  # First 5 y-coordinates
    print(f"z: {z[:5]} ...")  # First 5 grid values
else:
    print(f"grdread failed! {result}")
