import time
import psutil
import pandas as pd
from mlxtend.frequent_patterns import apriori, fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder
from pyECLAT import ECLAT
from visualization import items_total_plot, parallel_category_plot, heatmap_plot, scatterplot, \
    parallel_rule_existence_plot,frequent_itemset_plot,parallel_category_plot_nia, \
    heatmap_plot_nia, parallel_rule_existence_plot_nia

from niaarm import Dataset, get_rules
from niapy.algorithms.basic import DifferentialEvolution, BatAlgorithm, BeesAlgorithm
from niaarm.visualize import hill_slopes

class algorithms:
    
    def __init__(self, data) -> None:
        self.data = data
    
    def get_onehot_encoded_data(self):
        attrCount = len(self.data.count()) - 1
        fp_data = self.data.astype(str).values[:, :attrCount].tolist()
        my_transactionencoder = TransactionEncoder()
        my_transactionencoder.fit(fp_data)
        # One-hot encode
        encoded_transactions = my_transactionencoder.transform(fp_data)
        encoded_transactions_df = pd.DataFrame(encoded_transactions, columns=my_transactionencoder.columns_)
        return encoded_transactions_df
    
    def sort_and_clean_arules(self, arules):
        arules = arules.sort_values(['confidence', 'lift'], ascending =[False, False])
        arules['antecedents'] = arules['antecedents'].apply(lambda a: list(a))
        arules['consequents'] = arules['consequents'].apply(lambda a: list(a))
        return arules
    
    def sort_and_clean_frequent_itemset(self, frequent_itemset):
        frequent_itemset = frequent_itemset.sort_values(by=['support','itemsets'], ascending=False)
        frequent_itemset['itemsets'] = frequent_itemset['itemsets'].apply(lambda a: list(a))
        return frequent_itemset
    
    # pyECLAT and mlextend association rules fix https://github.com/rasbt/mlxtend/discussions/959
    def eclat_supports_to_df(self, get_ECLAT_supports):
        frequent_itemset = pd.DataFrame(get_ECLAT_supports.items(),columns=['itemsets','support'])
        frequent_itemset = frequent_itemset[['support','itemsets']]
        new_column = []
        for row in frequent_itemset['itemsets']:
            r = row.split('&')
            r = tuple(i.strip() for i in r)
            new_column.append(r)
        frequent_itemset['itemsets'] = pd.Series(new_column)
        return frequent_itemset
       
    def eclat_encode_data(self):
        enc_data = self.data.copy(deep=True)
        attrCount = len(enc_data.count())
        i = 0
        for col in enc_data.columns[:attrCount].tolist():
            enc_data.rename(columns={col : i}, inplace=True)
            i += 1

        return enc_data
            
    # https://www.geeksforgeeks.org/implementing-apriori-algorithm-in-python/
    def apriori(
        self,
        min_support:float,
        min_lift:float,
        show_plots: bool = True,
        save_results: bool = True
    ):
        print("Running apriori algorithm...")
        start = time.time()
        
        # Encode data
        encoded_data = self.get_onehot_encoded_data()
        
        # Run apriori   
        frequent_itemset = apriori(encoded_data, min_support = min_support, use_colnames = True)
        frequent_itemset = self.sort_and_clean_frequent_itemset(frequent_itemset)
    
        # Get association rules 
        arules = association_rules(frequent_itemset, metric="lift", min_threshold = min_lift)
        arules = self.sort_and_clean_arules(arules)
        
        end = time.time() - start
        print(f"Duration for apriori: {end}")
        print(f"Memory used for apriori: {psutil.Process().memory_info().rss / 1024 ** 2} MB")
        
        # Save results
        if(save_results):
            frequent_itemset.to_csv('data/result_apriori_frequent_itemset.csv')
            arules.to_csv('data/result_apriori_association_rules.csv')    
        
        # Show plots
        if show_plots:
            # frequent_itemset_plot(frequent_itemset)
            # items_total_plot(encoded_data)
            parallel_category_plot(arules)
            # heatmap_plot(arules)
            # scatterplot(arules)
            # parallel_rule_existence_plot(arules)
        print("Done")
        
    def eclat(
        self,
        min_support: float = 0.08,
        min_combination: float = 1,
        max_combination: float = 3,
        min_lift:float = 1,
        show_plots: bool = True,
        save_results: bool = True
    ):       
        print("Running eclat algorithm...")
        start = time.time()
            
        # Encode data       
        encoded_data = self.eclat_encode_data()
        
        # Run eclat
        eclat_instance = ECLAT(encoded_data, verbose=True)
        get_ECLAT_indexes, get_ECLAT_supports = eclat_instance.fit(min_support=min_support,
                                                            min_combination=min_combination,
                                                            max_combination=max_combination,
                                                            separator=' & ',
                                                            verbose=True)
        
        # Encode for use in association rules
        frequent_itemset = self.eclat_supports_to_df(get_ECLAT_supports)        
        frequent_itemset = frequent_itemset.sort_values(by=['support','itemsets'], ascending=False)
        

        # Get association rules
        arules = association_rules(frequent_itemset, metric ="lift", min_threshold = min_lift)
        arules = self.sort_and_clean_arules(arules)
        
        end = time.time() - start
        print(f"Duration for eclat: {end}")
        print(f"Memory used for eclat: {psutil.Process().memory_info().rss / 1024 ** 2} MB")
        
        # Save results
        if save_results:
            # TIDset
            tidSet = pd.DataFrame(get_ECLAT_indexes.items(), columns=['Item', 'Indices'])
        
            frequent_itemset.to_csv('data/result_eclat_frequent_itemsets.csv')
            arules.to_csv('data/result_eclat_association_rules.csv')
            tidSet.to_csv('data/result_eclat_TIDset.csv',sep='\t')
        
        # Show plots
        if show_plots:
            items_total_plot(encoded_data)
            parallel_category_plot(arules)
            heatmap_plot(arules)
            scatterplot(arules)
            parallel_rule_existence_plot(arules)


    # https://towardsdatascience.com/the-fp-growth-algorithm-1ffa20e839b8
    def fp_growth(
        self, 
        min_support: float = 0.08,
        min_lift: float = 1,
        show_plots: bool = True,
        save_results: bool = True
    ):      
        print("Running fp-growth algorithm...")
        start = time.time()
        
        # Encode data
        encoded_data = self.get_onehot_encoded_data()

        # Run fp-growth
        frequent_itemset = fpgrowth(encoded_data, min_support=min_support, use_colnames = True)
        frequent_itemset = self.sort_and_clean_frequent_itemset(frequent_itemset)

        # Get association rules
        arules = association_rules(frequent_itemset, metric="lift", min_threshold=min_lift)
        arules = self.sort_and_clean_arules(arules)
        
        end = time.time() - start
        print(f"Duration for fpgrowth: {end}")
        print(f"Memory used for fpgrowth: {psutil.Process().memory_info().rss / 1024 ** 2} MB")
        
        # Save results
        if(save_results):
            frequent_itemset.to_csv('data/result_fp_growth_frequent_itemset.csv')
            arules.to_csv('data/result_fp_growth_association_rules.csv')

        # Show plots
        if show_plots:
            items_total_plot(encoded_data)
            parallel_category_plot(arules)
            heatmap_plot(arules)
            scatterplot(arules)
            parallel_rule_existence_plot(arules)


    # Mulitple filters
    # filtered_rules = arules[(arules['antecedent support'] > 0.002) &
    #                (arules['consequent support'] > 0.01) &
    #                (arules['confidence'] > 0.60) &
    #                (arules['lift'] > 2.50)]

    # NARM****************************************************************************************   
    def filter_min_threshold(self, rules, min_support, min_lift):
        del_rules = []
        for r in rules:
            if(r.support < min_support or r.lift < min_lift):
                del_rules.append(r)
        for r in del_rules:
            rules.remove(r)
        return rules
    
    def niaarm_1(
        self,
        min_support: float = 0.5,
        min_lift: float = 1
    ):
        # Load data
        dataset = Dataset(self.data)
        
        # Set algorithm and metrics
        # algorithm = DifferentialEvolution(population_size=50, differential_weight=0.5, crossover_probability=0.9)
        algorithm = BatAlgorithm()
        metrics = ('support', 'confidence')
        
        # Get association rules
        rules, run_time = get_rules(dataset, algorithm, metrics, max_iters=30, logging=True)
        print(f'Run Time: {run_time}')
        
        # Filter rules with min_support and min_lift
        rules = self.filter_min_threshold(rules, min_support, min_lift)
        
        rules.sort(by='support',reverse=True)
        
        rules.to_csv('data/result_niaarm1_association_rules.csv')
        
        arules = pd.read_csv('data/result_niaarm1_association_rules.csv')
        
        import re
        arules['antecedent'] = arules['antecedent'].apply(lambda a: re.sub(r'[.][0-9]+', '', a))
        arules['consequent'] = arules['consequent'].apply(lambda a: re.sub(r'[.][0-9]+', '', a))

        
        # Show plots
        if True:
            # items_total_plot(encoded_data)
            parallel_category_plot_nia(arules)
            heatmap_plot_nia(arules)
            scatterplot(arules)
            parallel_rule_existence_plot_nia(arules)
        # first_rule = rules[0]
        # hill_slopes(first_rule, dataset.transactions)
        # plt.show()
    
    def niaarm_2(self):
        pass
    
    def niaarm_3(self):
        pass