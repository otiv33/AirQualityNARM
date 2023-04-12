import requests
import time
import json
import pandas as pd
import pickle
from datetime import datetime

class data_service:
    data = pd.DataFrame()
    
    def __init__(self, load_fresh_data: bool = True):
        self.data = self._get_data(load_fresh_data)
    
    # 1. - Get data
    def _air_quality_data_request(self) -> dict:
        url = 'http://20.222.149.200:8080/airQuality/'
        headers = {
            'Authorization': 'sjurzbfg7qlopdz5'
        }
        response = requests.get(url, headers=headers)
        return json.loads(response.text)
    
    def _get_data(self, load_fresh_data: bool = True) -> pd.DataFrame:
        print(f"Getting data... Fresh: {load_fresh_data}")
        start_time = time.time()
        data = None
        if(load_fresh_data):
            # Get fresh data
            data = self._air_quality_data_request()
        else:
            # Get data from file
            with open('data/data.pickle', 'rb') as f:
                data = pickle.load(f)
        # Save data to file
        with open('data/data.pickle', 'wb') as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        with open('data/data.json', 'w') as f:
            json.dump(data, f)
        elapsed_time = time.time() - start_time
        print(f'Time elapsed for aquiring data: {elapsed_time}s')
        return data
    
    
    # 2. - Structure data
    def structure_data(self, data) -> pd.DataFrame:
        clean_data = []
        for d in data:
            if(d['pm1'] is None):
                continue
            j_data = {
                # From local sensor
                'id': int(d['id']),
                'pm1': float(d['pm1']),
                'pm25': float(d['pm25']),
                'pm4': float(d['pm4']),
                'pm10': float(d['pm10']),
                'h': float(d['h']),
                't': float(d['t']),
                'voc': float(d['voc']),
                'nox': float(d['nox']),
                'dateTime': datetime.strptime(d['dateTime'], "%Y-%m-%d %H:%M:%S"),
                # From arso
                'o3': None,
                'no2': None,
                'benzen': None,
                # Merge pm10 from arso
                # Merge pm25 from arso
            } 
            if(len(d['arso_data']) == 2):
                # MB Titova
                ad1 = d['arso_data'][0]
                j_data['o3'] = ad1['o3']
                j_data['no2'] = ad1['no2']
                j_data['benzen'] = ad1['benzen']
                self._merge_data(j_data, ad1, 'pm10')
                self._merge_data(j_data, ad1, 'pm25')

                # MB Vrbanski
                ad2 = d['arso_data'][1]
                self._merge_data(j_data, ad2, 'o3')
                self._merge_data(j_data, ad2, 'no2')
                self._merge_data(j_data, ad2, 'benzen')
                self._merge_data(j_data, ad2, 'pm10')
                self._merge_data(j_data, ad2, 'pm25')
            
            clean_data.append(j_data)
        
        self.data = pd.DataFrame(clean_data)
    
    def _merge_data(self, j_data: dict, new_data: dict, property_name: str):
        try:
            if(j_data[property_name] is not None):
                if(new_data[property_name] is not None):
                    n1 = float(j_data[property_name])
                    n2 = float(new_data[property_name])
                    j_data[property_name] = (n1 + n2) / 2
            else:
                j_data[property_name] = new_data[property_name]
        except Exception as e:
            pass
    
    
    # 3. - Calibrate temperature for housing -3 C
    def calibrate_temperature(self):
        self.data['t'] = self.data['t'].sub(3)
        
        
    # 4. - Clean data - option 1 & 2
    def clean_data_zero(self):
        self.data.fillna(0, inplace=True)
        
    def clean_data_mean(self):
        if self.data['o3'].isna().values.any():
            avg_val = self.data['o3'].mean()
            self.data['o3'].fillna(avg_val, inplace=True)
        if self.data['no2'].isna().values.any():
            avg_val = self.data['no2'].mean()
            self.data['no2'].fillna(avg_val, inplace=True)
        if self.data['benzen'].isna().values.any():
            avg_val = self.data['benzen'].mean()
            self.data['benzen'].fillna(avg_val, inplace=True)
    
    
    # 5. - Check for NA values    
    def check_for_na_values(self):
        if not self.data.isna().values.any() and not self.data.isnull().values.any():
            print("[OK] - self.data has no NA values")
        else:
            print("[WARNING] - More cleaning is needed")
            
    # 6. - Save data to file
    def save_data(self):
        self.data.to_csv('data/data.csv', index=False)
        print("[OK] - Data saved to file")