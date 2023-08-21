import pandas as pd
from data_service import data_service

if __name__ == '__main__':
        
    ds = data_service(load_fresh_data=False)
    ds.structure_data()
    ds.calibrate_temperature()
    ds.clean_data_zero() # Option 1
    # ds.clean_data_mean() # Option 2
    ds.check_for_na_values()
    ds.data = ds.data.drop('id', axis=1)
    ds.save_clean_data_to_CSV()
    ds.update_algorithms_data()
    
    ds.categorize_data()
    
    # support : (št vrstic A)/(št vrstic)
    # confidence : (št vrstic z A in B)/(št vrstic A)
    # lift : (Confidence(A->B))/(support(B))
    
    ds.algorithms.apriori(min_support=0.5, min_lift=1)
    
    ds.algorithms.eclat(min_support=0.5, min_combination=1, max_combination=11, min_lift=1)
    
    ds.algorithms.fp_growth(min_support=0.5, min_lift=1)