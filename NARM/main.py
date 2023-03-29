import pandas as pd
from data_service import data_service

if __name__ == '__main__':
    # Get data
    ds = data_service()
    ds.get_data(load_fresh_data=True)
    ds.clean_data()
    data = ds.data
    
    # Save data to excel
    data = pd.DataFrame(data)
    data.to_excel('data/data.xlsx', index=False)
    print(data)
    
    