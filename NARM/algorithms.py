import pandas as pd
from mlxtend.frequent_patterns import apriori, fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder
from pyECLAT import ECLAT

class algorithms:
    
    def __init__(self, data) -> None:
        self.data = data
    
    def get_mlx_encoded_data(self):
        attrCount = len(self.data.count()) - 1
        fp_data = self.data.astype(str).values[:, :attrCount].tolist()
        my_transactionencoder = TransactionEncoder()
        my_transactionencoder.fit(fp_data)
        encoded_transactions = my_transactionencoder.transform(fp_data)
        encoded_transactions_df = pd.DataFrame(encoded_transactions, columns=my_transactionencoder.columns_)
        return encoded_transactions_df
       
    # https://www.geeksforgeeks.org/implementing-apriori-algorithm-in-python/
    def apriori(
        self,
        min_support:float,
        min_lift:float,
    ):
        print("\nRunning apriori algorithm...")
        
        # Encode data
        encoded_data = self.get_mlx_encoded_data()
        
        # Run apriori   
        frequent_itemset = apriori(encoded_data, min_support = min_support, use_colnames = True)
        frequent_itemset = frequent_itemset.sort_values(by=['support'], ascending=False)
        frequent_itemset.to_csv('data/result_apriori_frequent_itemset.csv')
    
        # Get association rules 
        arules = association_rules(frequent_itemset, metric ="lift", min_threshold = min_lift)
        arules = arules.sort_values(['confidence', 'lift'], ascending =[False, False])
        arules.to_csv('data/result_apriori_association_rules.csv')
        
        # # https://analyticsindiamag.com/how-to-visualize-different-ml-models-using-pycaret-for-optimization/
        # from pycaret.classification import plot_model, setup
        # s = setup(self.data, transaction_id = 'pm1', item_id = 'pm25')
        # plot_model(arules, plot = '2d')
        # print("hol up")
        
        print('Apriori new algorithm finished.\n')    
    
    # pyECLAT and mlextend association rules fix https://github.com/rasbt/mlxtend/discussions/959
    def eclat(
        self,
        min_support: float = 0.08,
        min_combination: float = 1,
        max_combination: float = 3,
        min_lift:float = 1
    ):       
        print("Running eclat algorithm...")
        eclat_instance = None
         
        # Encode data       
        attrCount = len(self.data.count())
        i = 0
        for col in self.data.columns[:attrCount].tolist():
            self.data.rename(columns={col : i}, inplace=True)
            i += 1
        
        # Run eclat
        eclat_instance = ECLAT(self.data, verbose=False)
        get_ECLAT_indexes, get_ECLAT_supports = eclat_instance.fit(min_support=min_support,
                                                           min_combination=min_combination,
                                                           max_combination=max_combination,
                                                           separator=' & ',
                                                           verbose=False)
        
        # Item count
        items_total = eclat_instance.df_bin.astype(int).sum(axis=0)
        items_total.to_csv('data/result_eclat_item_count.csv')
        
        # Encode for use in association rules
        frequent_itemset = pd.DataFrame(get_ECLAT_supports.items(),columns=['itemsets','support'])
        frequent_itemset = frequent_itemset[['support','itemsets']]
        new_column = []
        for row in frequent_itemset['itemsets']:
            r = row.split('&')
            r = tuple(i.strip() for i in r)
            new_column.append(r)
        frequent_itemset['itemsets'] = pd.Series(new_column)
        
        frequent_itemset = frequent_itemset.sort_values(by=['support'], ascending=False)
        frequent_itemset.to_csv('data/result_eclat_frequent_itemsets.csv')

        # Get association rules
        arules = association_rules(frequent_itemset, metric ="lift", min_threshold = min_lift)
        arules = arules.sort_values(['confidence', 'lift'], ascending =[False, False])
        arules.to_csv('data/result_eclat_association_rules.csv')
        
        print('Eclat new algorithm finished.\n')    
           
    # https://towardsdatascience.com/the-fp-growth-algorithm-1ffa20e839b8
    def fp_growth(
        self, 
        min_support: float = 0.08,
        min_lift: float = 1
    ):      
        print("Running fp-growth algorithm...")
        
        # Encode data
        encoded_data = self.get_mlx_encoded_data()

        # Run fp-growth
        frequent_itemset = fpgrowth(encoded_data, min_support=min_support, use_colnames = True)
        frequent_itemset = frequent_itemset.sort_values(by=['support'], ascending=False)
        frequent_itemset.to_csv('data/result_fp_growth_frequent_itemset.csv')

        # Get asspciation rules
        arules = association_rules(frequent_itemset, metric="lift", min_threshold=min_lift)
        arules = arules.sort_values(['confidence', 'lift'], ascending =[False, False])
        arules.to_csv('data/result_fp_growth_association_rules.csv')

        print("Fp-growth algorithm finished.\n")
    
    def nia_alogrithm(self):
        pass
    
    
    # # APRIORI        
    # def apriori(
    #     self, 
    #     min_support: float,
    #     min_confidence: float,
    #     min_lift: float,
    #     max_length: int = 3
    # ):
    #     from apyori import apriori
    #     print("Running apriori algorithm...")
        
    #     # Modify data to fit apriori algorithm
    #     attrCount = len(self.data.count()) - 1
    #     apriori_data = self.data.astype(str).values[:, :attrCount].tolist()

    #     res = list(
    #         apriori(
    #             apriori_data, 
    #             min_support=min_support, 
    #             min_confidence=min_confidence, 
    #             min_lift=min_lift, 
    #             max_length = max_length
    #         )
    #     )
        
    #     apr_data = {
    #         'Rule' : [],
    #         'Support' : [],
    #         'Confidence' : [],
    #         'Lift' :  []
    #     }
        
    #     for item in res:
    #         pair = item[0] 
    #         items = [x for x in pair]
    #         rule = ""
    #         for i in items:
    #             rule += str(i)+", "
    #         rule = rule[:-2]

    #         support = item.support
    #         confidence = item[2][0].confidence
    #         lift = item[2][0].lift
                
    #         apr_data['Rule'].append(rule)
    #         apr_data['Support'].append(support)
    #         apr_data['Confidence'].append(confidence)
    #         apr_data['Lift'].append(lift)
                
    #     pd.DataFrame(apr_data).to_csv('data/result_apriori.csv')
        
    #     print("Apriori algorithm finished.")
    
    # # ECLAT - https://hands-on.cloud/implementation-of-eclat-algorithm-using-python/
    # def eclat(
    #     self, 
    #     min_support: float = 0.08,
    #     min_combination: float = 1,
    #     max_combination: float = 3,
    # ):
    #     from pyECLAT import ECLAT
        
    #     print("Running eclat algorithm...")
    #     eclat_instance = None
                
    #     attrCount = len(self.data.count())
    #     i = 0
    #     for col in self.data.columns[:attrCount].tolist():
    #         self.data.rename(columns={col : i}, inplace=True)
    #         i += 1
        
    #     eclat_instance = ECLAT(self.data, verbose=True)
        
    #     # Eclat result
    #     eclat_instance.df_bin.to_csv('data/result_eclat.csv')
        
    #     # Item count
    #     items_total = eclat_instance.df_bin.astype(int).sum(axis=0)
    #     items_total.to_csv('data/result_eclat_item_count.csv')
        
    #     #  Top 10 most common items     
    #     df = pd.DataFrame({'Items': items_total.index, 'Measurement': items_total.values}) 
    #     df_table = df.sort_values("Measurement", ascending=False)
    #     df_table.head(10).to_csv('data/result_eclat_top10.csv')
        
    #     rule_indexes, rule_supports = eclat_instance.fit(min_support=min_support,
    #                                                     min_combination=min_combination,
    #                                                     max_combination=max_combination,
    #                                                     separator=' & ',
    #                                                     verbose=True)
    #     # Rule indices
    #     indexes = pd.DataFrame(rule_indexes.items(), columns=['Item', 'Indices'])
    #     indexes.to_csv('data/result_eclat_indexes.csv',sep='\t')
    #     # Rule support
    #     supports = pd.DataFrame(rule_supports.items(),columns=['Item', 'Support'])
    #     supports = supports.sort_values(by=['Support'], ascending=False)
    #     supports.to_csv('data/result_eclat_support.csv')