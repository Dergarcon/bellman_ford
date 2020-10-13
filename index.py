#%%
import data
from typing import Tuple, List
from math import log
import pandas as pd
import numpy as np
import itertools

def negate_logarithm_convertor(graph: Tuple[Tuple[float]]) -> List[List[float]]:
    ''' log of each rate in graph and negate it'''
    result = [[-log(edge) for edge in row] for row in graph]
    return result

def arbitrage(currency_tuple: tuple, rates_matrix: Tuple[Tuple[float, ...]]) -> List[List[str]]:
    ''' Calculates arbitrage situations and prints out the details of this calculations'''

    arb_paths = list()

    trans_graph = negate_logarithm_convertor(rates_matrix)

    # Pick any source vertex -- we can run Bellman-Ford from any vertex and get the right result

    source = 0
    n = len(trans_graph)
    min_dist = [float('inf')] * n

    pre = [-1] * n
    
    min_dist[source] = source

    # 'Relax edges |V-1| times'
    for _ in range(n-1):        
        for source_curr in range(n):
            for dest_curr in range(n):
                if min_dist[dest_curr] > min_dist[source_curr] + trans_graph[source_curr][dest_curr]:
                    min_dist[dest_curr] = min_dist[source_curr] + trans_graph[source_curr][dest_curr]
                    pre[dest_curr] = source_curr

    # if we can still relax edges, then we have a negative cycle
    for source_curr in range(n):
        for dest_curr in range(n):
            if min_dist[dest_curr] > min_dist[source_curr] + trans_graph[source_curr][dest_curr]:
                # negative cycle exists, and use the predecessor chain to print the cycle
                print_cycle = [dest_curr, source_curr]
                # Start from the source and go backwards until you see the source vertex again or any vertex that already exists in print_cycle array
                while pre[source_curr] not in  print_cycle:
                    print_cycle.append(pre[source_curr])
                    source_curr = pre[source_curr]
                print_cycle.append(pre[source_curr])                
                arb_paths.append([tokens[p] for p in print_cycle[::-1]])   
    return arb_paths             

def prepare_data(tokens: List[str]) -> List[List[float]]:

    df = pd.DataFrame(columns=tokens)
    rates = [[],[],[]]  #TODO: improve so it takes any setlenght of tokens

    # MAP-REDUCE: MAP
    for token in tokens:
        df.loc[token] = [[],[],[]]  #TODO: improve so it takes any setlenght of tokens
        df.loc[token, token] = 1       
        for exchange in data:                    
            for price in exchange['prices']:
                if token in price['quoteToken']:
                    df.at[token, price['baseToken']].append((1/price['ask'], 0))
                    
                elif token in price['baseToken']:
                    df.at[token, price['quoteToken']].append((price['bid'], 1))            

    # MAP-REDUCE: REDUCE
    for i, token in enumerate(tokens):
        values = df.loc[token].values      
        for item in values:                
            if type(item) is int:
                rates[i].append(item)            
                continue       
            if item[0][1] == 0:                        
                min_ask = max(item) #already using reciprocal of ask price ( 1/ask - See mapping phase above)
                rates[i].append(min_ask[0])            
                continue
            if item[0][1] == 1:                        
                max_bid = max(item)
                rates[i].append(max_bid[0])            
                continue
            print('SOMETHING WENT WRONG!')
    
    return rates
    
def clean_paths(arb_paths: List[str]):
    for arb in arb_paths:
        if not arb[0] == arb[-1]:
            arb.pop(-1)

def calculate_profits(arb_paths: List[str], rates: List[float]) -> (List[Tuple[float, List[str]]], pd.DataFrame):
    results = list()
    value_matrix = pd.DataFrame(rates, columns=tokens, index=tokens)
    for idx, arb in enumerate(arb_paths):
        prev_token = None
        profit = 1
        for token in arb:
            if prev_token is None:
                prev_token = token
                continue
            profit *= value_matrix.loc[prev_token, token]
            prev_token = token        
        tpl = (profit, arb)
        results.append(tpl)
    return results, value_matrix

def sort_and_print_all_profits(profits: List[List[Tuple[float, List[str]]]]):
    flat_list = [item for sublist in profits for item in sublist]
    flat_list.sort(reverse=True)
    remove_duplicates(flat_list)
    remove_duplicates(flat_list)    
    print('Found following Arbitrage opportunities: ')
    for profit in flat_list:
        formatted_profit = "{:.6f}".format((profit[0]-1)*100)        
        print(f'{formatted_profit} % profit -> path: {profit[1]}')

def remove_duplicates(flat_list: List[Tuple[int, List[str]]]) -> List[str]:
    prev_item = None
    for item in flat_list:                
        if prev_item is None:
                prev_item = item                                
                continue
        elif prev_item[1] == item[1]:            
            flat_list.remove(prev_item)                    
        prev_item = item
    return flat_list

def main(tokens: List[str]):
    rates = prepare_data(tokens)    
    arb_paths = arbitrage(tokens, rates)
    clean_paths(arb_paths)
    profits, value_matrix = calculate_profits(arb_paths, rates)
    all_profits.append(profits)    

ata = data.myPythonDictionary["exchanges"]    
tokens = ['eth', 'rep', 'usdc']
perm_tokens = list(itertools.permutations(tokens))
all_profits = []
for tokens in perm_tokens:
    main(tokens)

sort_and_print_all_profits(all_profits)