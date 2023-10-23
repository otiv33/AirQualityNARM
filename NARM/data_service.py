import requests
import time
import json
import pandas as pd
import pickle
from datetime import datetime
from algorithms import algorithms

class data_service:
    data = pd.DataFrame()
    algorithms = algorithms(data)
    
    def __init__(self, load_fresh_data: bool = True):
        self.data = self._get_data(load_fresh_data)
        self.algorithms.data = self.data
    
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
        # with open('data/data.json', 'w') as f:
        #     json.dump(data, f)
        elapsed_time = time.time() - start_time
        print(f'Time elapsed for aquiring data: {elapsed_time}s\n')
        return data
    
    
    # 2. - Structure data
    def structure_data(self) -> pd.DataFrame:
        clean_data = []
        for d in self.data:
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
                'dateTime': datetime.strptime(d['dateTime'], "%Y-%m-%d %H:%M:%S").hour,
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
                j_data['pm10'] = self._merge_data(j_data['pm10'], ad1['pm10'])
                j_data['pm25'] = self._merge_data(j_data['pm25'], ad1['pm25'])

                # MB Vrbanski
                ad2 = d['arso_data'][1]
                j_data['o3'] = self._merge_data(j_data['o3'], ad2['o3'])
                j_data['no2'] = self._merge_data(j_data['no2'], ad2['no2'])
                j_data['benzen'] = self._merge_data(j_data['benzen'], ad2['benzen'])
                j_data['pm10'] = self._merge_data(j_data['pm10'], ad2['pm10'])
                j_data['pm25'] = self._merge_data(j_data['pm25'], ad2['pm25'])
            
            clean_data.append(j_data)
        
        self.data = pd.DataFrame(clean_data)
    
    def _merge_data(self, data, new_data):
        try:
            if(data is not None):
                if(new_data is not None):
                    n1 = float(data) if not isinstance(data, str) else 1.0 
                    n2 = float(new_data) if not isinstance(new_data, str) else 1.0
                    return (n1 + n2) / 2
            else:
                return float(new_data) if not isinstance(new_data, str) else 1.0
        except Exception as e:
            return None
    
    
    # 3. - Calibrate temperature for housing -6 C
    def calibrate_temperature(self):
        self.data['t'] = self.data['t'].sub(6)    
        
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
    def save_clean_data_to_CSV(self):
        self.data.to_csv('data/cleaned-data.csv', index=False)
        print("[OK] - Data saved to data/cleaned-data.csv\n")
         
    # 7. - Update algorithms data
    def update_algorithms_data(self):
        self.algorithms.data = self.data
        
    #8. - Categorize data
    def classify_data(self):       
        self.data['pm1'] = pd.cut(
                self.data['pm1'],
                include_lowest=True,
                bins=[0,10,20,25,50,75,1000],
                labels= ['pm1-Zelo dobra','pm1-Dobra','pm1-Sprejemljiva','pm1-Slaba','pm1-Zelo slaba','pm1-Izredno slaba']
            )
        self.data['pm25'] = pd.cut(
                self.data['pm25'],
                include_lowest=True,
                bins=[0,10,20,25,50,75,1000],
                labels= ['pm25-Zelo dobra','pm25-Dobra','pm25-Sprejemljiva','pm25-Slaba','pm25-Zelo slaba','pm25-Izredno slaba']
            )
        self.data['pm4'] = pd.cut(
                self.data['pm4'],
                include_lowest=True,
                bins=[0,20,40,50,100,150,1200],
                labels= ['pm4-Zelo dobra','pm4-Dobra','pm4-Sprejemljiva','pm4-Slaba','pm4-Zelo slaba','pm4-Izredno slaba']
            )
        self.data['pm10'] = pd.cut(
                self.data['pm10'],
                include_lowest=True,
                bins=[0,20,40,50,100,150,1200],
                labels= ['pm10-Zelo dobra','pm10-Dobra','pm10-Sprejemljiva','pm10-Slaba','pm10-Zelo slaba','pm10-Izredno slaba']
            )
        self.data['h'] = pd.cut(
            self.data['h'],
            include_lowest=True,
            bins=[0,20,40,60,80,100],
            labels= ['h-Zelo nizka','h-Nizka','h-Srednja','h-Visoka','h-Zelo visoka']
        )
        self.data['t'] = pd.cut(
            self.data['t'],
            include_lowest=True,
            bins=[-15,0,10,20,30,40,50],
            labels= ['t-Zelo hladno','t-Hladno','t-Srednje','t-Toplo','t-Vroče','t-Zelo vroče']
        )
        self.data['voc'] = pd.cut(
            self.data['voc'],
            include_lowest=True,
            bins=[0,100,200,300,400,500], # Index points
            labels= ['h-Zelo nizka','h-Nizka','h-Srednja','h-Visoka','h-Zelo visoka']
        )
        self.data['nox'] = pd.cut(
            self.data['nox'],
            include_lowest=True,
            bins=[0,100,200,300,400,500], # Index points
            labels= ['nox-Zelo nizka','nox-Nizka','nox-Srednja','nox-Visoka','nox-Zelo visoka']
        )
        self.data['o3'] = pd.cut(
            self.data['o3'],
            include_lowest=True,
            bins=[0,50,100,130,240,380,10000], # http://rte.arso.gov.si/zrak/kakovost%20zraka/podatki/ozon.html
            labels= ['o3-Zelo dobra','o3-Dobra','o3-Sprejemljiva','o3-Slaba','o3-Zelo slaba','o3-Izredno slaba']
        )
        self.data['no2'] = pd.cut(
            self.data['no2'],
            include_lowest=True,
            bins=[0,40,90,120,230,340,1000], # https://www.arso.gov.si/zrak/kakovost%20zraka/podatki/amp/razlaga_pojmov.html
            labels= ['no2-Zelo dobra','no2-Dobra','no2-Sprejemljiva','no2-Slaba','no2-Zelo slaba','no2-Izredno slaba']
        )
        self.data['benzen'] = pd.cut(
            self.data['benzen'],
            include_lowest=True,
            bins=[0,5,380],
            labels= ['benzen-Dobro','benzen-Slabo']
        )
        self.data['dateTime'] = pd.cut(
            self.data['dateTime'],
            include_lowest=True,
            bins=[0,6,12,18,24],
            labels= ['dateTime-Noč', 'dateTime-Dopoldne','dateTime-Popoldne','dateTime-Večer']
        )
    

