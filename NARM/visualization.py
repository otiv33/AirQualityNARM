from matplotlib import pyplot as plt

def frequent_itemset_plot(frequent_itemset):
    import numpy as np
    data = frequent_itemset.copy(deep=True)
    itemsets = data['itemsets'].apply(lambda a: ','.join([str(x) for x in a]))
    color = plt.cm.rainbow(np.linspace(0, 1, 40))
    
    plt.barh(list(itemsets), list(data['support']), color = color)
    plt.title('Pogoste množice', fontsize = 20)
    plt.xticks(rotation = 90 )
    plt.xlabel("Support")
    plt.ylabel("Itemset")
    plt.gca().invert_yaxis()
    plt.grid()
    plt.show()
   
def items_total_plot(encoded_data):
    import numpy as np
    data = encoded_data.copy(deep=True)
    
    items_total = data.astype(int).sum(axis=0)
    items_total = items_total.sort_values(ascending=False)
    
    color = plt.cm.rainbow(np.linspace(0, 1, 40))
    items_total.head(50).plot.bar(color = color, figsize=(13,5))
    plt.title('Število elementov', fontsize = 20)
    plt.xticks(rotation = 90 )
    plt.grid()
    plt.show()    
    
def parallel_category_plot(arules):
    import plotly.express as px

    fig = px.parallel_categories(
            arules, 
            dimensions=['antecedents', 'consequents'],
            color="confidence", 
            color_continuous_scale=px.colors.sequential.Inferno,
            labels={'antecedents':'Antecedents', 'consequents':'Consequents'},
            height=1080,
            width=1920,
        )
    
    fig.update_layout(
        margin=dict(l=500, r=500, t=50, b=5),
        font=dict(size=15),
        coloraxis_colorbar_x=1.33
    )

    fig.show()

def parallel_category_plot_nia(arules):
    import plotly.express as px

    fig = px.parallel_categories(
            arules, 
            dimensions=['antecedent', 'consequent'],
            color="confidence", 
            color_continuous_scale=px.colors.sequential.Inferno,
            labels={'antecedents':'Antecedents', 'consequents':'Consequents'},
            height=1080,
            width=1920,
            title='Paralelni kategoprični graf A⇒B'
        )
    
    fig.update_layout(
        margin=dict(l=500, r=500, t=50, b=5),
        font=dict(size=15),
        coloraxis_colorbar_x=1.33
    )

    fig.show()
    
# FOR PLOTS https://goldinlocks.github.io/Market-Basket-Analysis-in-Python/
def heatmap_plot(arules):
    import seaborn as sns
    rules = arules.copy(deep=True)
    # Convert antecedents and consequents into strings
    rules['antecedents'] = rules['antecedents'].apply(lambda a: ','.join(list(a)))
    rules['consequents'] = rules['consequents'].apply(lambda a: ','.join(list(a)))

    # Transform antecedent, consequent, and support columns into matrix
    support_table = rules.pivot(index='consequents', columns='antecedents', values='support')

    plt.figure(figsize=(10,6))
    sns.heatmap(support_table, annot=True, cbar=True)
    b, t = plt.ylim() 
    b += 0.5 
    t -= 0.5 
    plt.ylim(b, t) 
    plt.yticks(rotation=0)
    plt.show()
    
def heatmap_plot_nia(arules):
    import seaborn as sns
    import pandas as pd

    # Transform antecedent, consequent, and support columns into matrix
    support_table = pd.DataFrame(arules).pivot_table(index='consequent', columns='antecedent', values='support')

    plt.figure(figsize=(10,6))
    sns.heatmap(support_table, annot=True, cbar=True)
    b, t = plt.ylim() 
    b += 0.5 
    t -= 0.5 
    plt.ylim(b, t) 
    plt.yticks(rotation=0)
    plt.title('Graf toplotnega zemljevida', fontsize = 20)
    plt.show()

    
def scatterplot(rules):
    # import plotly.express as px
    # fig = px.scatter(rules, x="support", y="confidence", color='lift')
    # fig.show()

    import seaborn as sns
    plt.figure(figsize=(10,6))
    sns.scatterplot(x = "support", y = "confidence", 
                    size = "lift", data = rules)
    plt.margins(0.01,0.01)
    plt.title('Graf raztrosa asociacijskih pravil', fontsize = 20)
    plt.show()
    

def parallel_rule_existence_plot(arules):
    from pandas.plotting import parallel_coordinates
    rules = arules.copy(deep=True)
    # Convert rules into coordinates suitable for use in a parallel coordinates plot
    rules['antecedent'] = rules['antecedents'].apply(lambda antecedent: list(antecedent)[0])
    rules['consequent'] = rules['consequents'].apply(lambda consequent: list(consequent)[0])
    rules['rule'] = rules.index
    coords = rules[['antecedent','consequent','rule']]

    # Generate parallel coordinates plot
    plt.figure(figsize=(15,8))
    parallel_coordinates(coords, 'rule')
    plt.legend([])
    plt.grid(True)
    plt.show()

def parallel_rule_existence_plot_nia(arules):
    from pandas.plotting import parallel_coordinates
    rules = arules.copy(deep=True)
    # Convert rules into coordinates suitable for use in a parallel coordinates plot
    rules['antecedent'] = rules['antecedent'].apply(lambda antecedent: list(antecedent)[0])
    rules['consequent'] = rules['consequent'].apply(lambda consequent: list(consequent)[0])
    rules['rule'] = rules.index
    coords = rules[['antecedent','consequent','rule']]

    # Generate parallel coordinates plot
    plt.figure(figsize=(15,8))
    parallel_coordinates(coords, 'rule')
    plt.legend([])
    plt.grid(True)
    plt.show()