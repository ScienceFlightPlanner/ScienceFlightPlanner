from netCDF4 import Dataset
import numpy as np
import os

dataset_dir = os.path.join(os.getcwd(), "datasets")
os.makedirs(dataset_dir, exist_ok=True)

width, height = 7585, 13700
origin_x, origin_y = -659100, -639100
pixel_size = 200

x = np.arange(origin_x, origin_x + width * pixel_size, pixel_size)
y = np.arange(origin_y, origin_y - height * pixel_size, -pixel_size)

z = np.linspace(-8078.105, 8963.600, width * height).reshape((height, width))

output_file = os.path.join(dataset_dir, "GL_vel_mosaic_simulated.grd")
with Dataset(output_file, "w", format="NETCDF4") as nc:
    nc.createDimension("x", width)
    nc.createDimension("y", height)
    
    x_var = nc.createVariable("x", "f4", ("x",))
    y_var = nc.createVariable("y", "f4", ("y",))
    z_var = nc.createVariable("z", "f4", ("y", "x"))
    
    x_var[:] = x
    y_var[:] = y
    z_var[:, :] = z
    
    x_var.units = "meters"
    y_var.units = "meters"
    z_var.units = "simulated velocity"
    nc.description = "Simulated .grd file similar to the provided GeoTIFF example"
    nc.origin = f"Upper-left corner: ({origin_x}, {origin_y})"
    nc.pixel_size = pixel_size
    nc.crs = "EPSG:3413"

print(f"Created: {output_file}")
