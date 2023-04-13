import pandas as pd
from data_service import data_service

if __name__ == '__main__':
        
    ds = data_service(load_fresh_data=False)
    ds.structure_data()
    ds.calibrate_temperature()
    ds.clean_data_zero() # Option 1
    # ds.clean_data_mean() # Option 2
    ds.check_for_na_values()
    ds.save_data()
    ds.refresh_algorithms_data()
    
    # support : (št vrstic A)/(št vrstic)
    # confidence : (št vrstic z A in B)/(št vrstic A)
    # lift : (Confidence(A->B))/(support(B))
    # ds.algorithms.apriori(min_support=0.1, min_confidence=0.1, min_lift=1, max_length=4)
    
    ds.algorithms.eclat(0.08, 1, 3)

    