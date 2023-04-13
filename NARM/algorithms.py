import numpy as np
import pandas as pd
import pickle
from pyECLAT import ECLAT

class algorithms:
    
    def __init__(self, data) -> None:
        self.data = data
    
    # APRIORI        
    def apriori(
        self, 
        min_support: float,
        min_confidence: float,
        min_lift: float,
        max_length: int = 3
    ):
        from apyori import apriori
        print("Running apriori algorithm...")
        
        # Modify data to fit apriori algorithm
        attrCount = len(self.data.count()) - 1
        apriori_data = self.data.astype(str).values[:, :attrCount].tolist()

        res = list(
            apriori(
                apriori_data, 
                min_support=min_support, 
                min_confidence=min_confidence, 
                min_lift=min_lift, 
                max_length = max_length
            )
        )
        for item in res:
            pair = item[0] 
            items = [x for x in pair]
            msg = "Rule : "
            for i in items:
                msg += "("+str(i)+") "
            print(msg)

            support = item.support
            confidence = item[2][0].confidence
            lift = item[2][0].lift
            
            print("Support: " + str(support))
            print("Confidence: " + str(confidence))
            print("Lift: " + str(lift))
            print("=====================================")
        print("Apriori algorithm finished.")
        
    def eclat(
        self, 
        min_support: float = 0.08,
        min_combination: float = 1,
        max_combination: float = 3,
    ):
        print("Running eclat algorithm...")        
        eclat_instance = None
        
        if(False): # FOR TESTING PURPOSES
            attrCount = len(self.data.count())
            i = 0
            for col in self.data.columns[:attrCount].tolist():
                self.data.rename(columns={col : i}, inplace=True)
                i += 1
            
            self.data = self.data.astype(str)
            eclat_instance = ECLAT(self.data, verbose=True)
        
            with open('eclat_instance.pickle', 'wb') as f:
                pickle.dump(eclat_instance, f)
        else:
            with open('eclat_instance.pickle', 'rb') as f:
                eclat_instance = pickle.load(f)
        
        items_total = eclat_instance.df_bin
        rule_indices, rule_supports = eclat_instance.fit(min_support=min_support,
                                                        min_combination=min_combination,
                                                        max_combination=max_combination,
                                                        separator=' & ',
                                                        verbose=True)
        
        # help(eclat_instance.fit)
        # help(eclat_instance.fit_all)
        # help(eclat_instance.support)

        print("Rule indices: ", rule_indices)
        print("Rule supports: ", rule_supports)
    
    def fp_growth(self):
        pass
    
    def nia_alogrithm(self):
        pass