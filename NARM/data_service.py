import requests
import time
import json
import pandas as pd

class data_service:
    
    def __init__(self):
        self.data = None
    
    def _air_quality_data_request(self) -> dict:
        url = 'http://20.222.149.200:8080/airQuality/'
        headers = {
            'Authorization': 'sjurzbfg7qlopdz5'
        }
        start_time = time.time()
        response = requests.get(url, headers=headers)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f'Time elapsed for request: {elapsed_time}s')
        return json.loads(response.text)

    def get_data(self, load_fresh_data: bool = True) -> pd.DataFrame:
        data = None
        if(load_fresh_data):
            # Get fresh data
            data = self._air_quality_data_request()
        else:
            # Get data from file
            with open('data/data.json', 'r') as f:
                data = json.load(f)
        # Save data to file
        with open('data/data.json', 'w') as f:
            json.dump(data, f)
        
        self.data = data
    
    def clean_data(self):
        clean_data = []
        for d in self.data:
            j_data = {
                # From local sensor
                'id': d['id'],
                'pm1': d['pm1'],
                'pm25': d['pm25'],
                'pm4': d['pm4'],
                'pm10': d['pm10'],
                'h': d['h'],
                't': d['t'],
                'voc': d['voc'],
                'nox': d['nox'],
                'dateTime': d['dateTime'],
                # From arso
                'so2': None,
                # 'co': None, NO DATA
                'o3': None,
                'no2': None,
                'benzen': None,
                # Merge pm10 from arso
                # Merge pm25 from arso
            } 
            if(len(d['arso_data']) == 2):
                # MB Titova
                ad1 = d['arso_data'][0]
                j_data['so2'] = ad1['so2']
                # j_data['co'] = ad1['co'] NO DATA
                j_data['o3'] = ad1['o3']
                j_data['no2'] = ad1['no2']
                j_data['benzen'] = ad1['benzen']
                self._merge_data(j_data, ad1, 'pm10')
                self._merge_data(j_data, ad1, 'pm25')

                # MB Vrbanski
                ad2 = d['arso_data'][1]
                self._merge_data(j_data, ad2, 'so2')
                # merge_data(j_data, ad2, 'co') NO DATA
                self._merge_data(j_data, ad2, 'o3')
                self._merge_data(j_data, ad2, 'no2')
                self._merge_data(j_data, ad2, 'benzen')
                self._merge_data(j_data, ad2, 'pm10')
                self._merge_data(j_data, ad2, 'pm25')
            
            clean_data.append(j_data)
        
        return clean_data

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