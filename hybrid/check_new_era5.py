# check_new_era5.py
import xarray as xr

# Check temperature file
print("=== TEMPERATURE FILE ===")
ds1 = xr.open_dataset(
    r"D:\Predictive_Project\data\c8c14aacc047870d53d008058653b466\data_stream-oper_stepType-instant.nc"
)
print(ds1)
print("\nVariables:", list(ds1.data_vars))
print("Coordinates:", list(ds1.coords))

# Check precipitation file
print("\n=== PRECIPITATION FILE ===")
ds2 = xr.open_dataset(
    r"D:\Predictive_Project\data\c8c14aacc047870d53d008058653b466\data_stream-oper_stepType-accum.nc"
)
print(ds2)
print("\nVariables:", list(ds2.data_vars))
print("Coordinates:", list(ds2.coords))
