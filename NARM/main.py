import pandas as pd
from data_service import data_service

if __name__ == '__main__':
    
    fresh = True
    
    ds = data_service(load_fresh_data=fresh)
    ds.structure_data()
    ds.calibrate_temperature()
    ds.clean_data_zero()
    ds.clean_data_mean()
    ds.check_for_na_values()
    
    
    