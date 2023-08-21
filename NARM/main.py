from data_service import data_service
from memory_profiler import memory_usage

def print_mem_usage(mem_usage, alg_name):
    print(f'MIN memory {alg_name}: {min(mem_usage)}')
    print(f'AVG memory {alg_name}: {(sum(mem_usage) / len(mem_usage))}' )
    print(f'MAX memory usage {alg_name}: {max(mem_usage)}')
    
if __name__ == '__main__':
    
    load_fresh_data = False
    clean_data = 'zero' # zero, median
    min_support = 0.9 # default 0.9
    min_lift = 1 # default 1
    show_plots = True
    categorized_alg = False
    save_results = True
    
    ds = data_service(load_fresh_data)
    ds.structure_data()
    ds.calibrate_temperature()
    if clean_data == 'zero':
        ds.clean_data_zero()
    elif clean_data == 'median':
        ds.clean_data_mean()
    ds.check_for_na_values()
    ds.data = ds.data.drop('id', axis=1)
    ds.save_clean_data_to_CSV()
    ds.update_algorithms_data()
    
    if(categorized_alg):
        ds.classify_data()
        aprirori_and_fp_params = {
            "min_support":min_support,
            "min_lift":min_lift,
            "show_plots":show_plots,
            "save_results":save_results
        }
        eclat_params = {
            "min_support":min_support,
            "min_combination":1, 
            "max_combination":3, 
            "min_lift":min_lift, 
            "show_plots":show_plots,
            "save_results":save_results
        }
        
        # APRIORI
        if True:
            mem_usage = memory_usage((ds.algorithms.apriori, (), aprirori_and_fp_params))
            print_mem_usage(mem_usage, 'apriori')
        
        # ECLAT
        if False:
            mem_usage = memory_usage((ds.algorithms.eclat, (), eclat_params))
            print_mem_usage(mem_usage, 'eclat')
        
        # FP-growth
        if False:
            mem_usage = memory_usage((ds.algorithms.fp_growth, (), aprirori_and_fp_params))
            print_mem_usage(mem_usage, 'fp_growth')
    else:
        ds.algorithms.niaarm_1(min_support=min_support, min_lift=min_lift)
        # niaarm_params = {
        #     "min_support":min_support,
        #     "min_lift":min_lift
        # }
        # mem_usage = memory_usage((ds.algorithms.niaarm_1, (), niaarm_params))
        # print_mem_usage(mem_usage, 'niaarm_1')
    
