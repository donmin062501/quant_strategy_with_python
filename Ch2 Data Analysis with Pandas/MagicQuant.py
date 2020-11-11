# -*- coding: utf-8 -*-
import pandas as pd



def magic_by_pd(file_path):
    per_data = pd.read_excel(file_path, sheet_name='PER', index_col=0)
    filtered_per = per_data[per_data['PER']>0]
    sorted_per = filtered_per.sort_values(by = 'PER')
    sorted_per['PER Ranking']=sorted_per['PER'].rank()
    
    roa_data = pd.read_excel(file_path, sheet_name='ROA', index_col=0)
    filtered_roa = roa_data.dropna()
    filtered_roa.columns = ['ROA']
    sorted_roa = filtered_roa.sort_values(by = 'ROA', ascending = False)
    sorted_roa['ROA Ranking'] = sorted_roa['ROA'].rank(ascending = False)
    
    total_df = pd.merge(sorted_per, sorted_roa, how='inner', left_index=True, right_index=True)
    
    total_df['Total Ranking'] = (total_df['PER Ranking'] + total_df['ROA Ranking']).rank()
    return total_df.sort_values(by = 'Total Ranking')