# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np


# function to create a neat dataframe for .xlsx files
def get_finance_data(path):
    data_path = path
    raw_data = pd.read_excel(data_path, index_col=0)
    big_col = list(raw_data.columns)
    small_col = list(raw_data.iloc[0])
    
    new_big_col = []
    for num, col in enumerate(big_col):
        if 'Unnamed' in col:
            new_big_col.append(new_big_col[num-1])
        else:
            new_big_col.append(big_col[num])
            
    raw_data.columns = [new_big_col, small_col]
    clean_df = raw_data.loc[raw_data.index.dropna()]
    
    return clean_df


# function to convert 'N/A(IFRS)' to 'NaN'
def check_IFRS(x):
    if x == 'N/A(IFRS)':
        return np.NaN # returning NaN if N/A(IFRS)
    else:
        return x # if not, returning the original numerical value


# function to sort per values in ascending order
def low_per(invest_df, index_date, num):
    invest_df[(index_date, 'PER')] = pd.to_numeric(invest_df[(index_date, 'PER')])
    per_sorted = invest_df.sort_values(by=(index_date, 'PER'))
    return per_sorted[index_date][:num]


# function to sort roa values in descending order
def high_roa(fr_df, index_date, num):
    fr_df[(index_date, 'ROA')] = fr_df[(index_date, 'ROA')].apply(check_IFRS)
    fr_df[(index_date, 'ROA')] = pd.to_numeric(fr_df[(index_date, 'ROA')] )
    roa_sorted = fr_df.sort_values(by=(index_date, 'ROA'), ascending=False)
    return roa_sorted[index_date][:num]


# function to demonstrate magic formula
def magic_formula(fr_df, invest_df, index_date, num):
    per = low_per(invest_df, index_date, None)
    roa = high_roa(fr_df, index_date, None)
    per['per_rank'] = per['PER'].rank()
    roa['roa_rank'] = roa['ROA'].rank(ascending=False)
    magic = pd.merge(per, roa, how='outer', left_index=True, right_index=True)
    magic['magic_rank'] = (magic['per_rank'] + magic['roa_rank']).rank().sort_values()
    magic = magic.sort_values(by='magic_rank')
    return magic[:num]


# function to rank a value
def get_value_rank(invest_df, value_type, index_date, num):
    invest_df[(index_date,  value_type)] = pd.to_numeric(invest_df[(index_date,  value_type)])
    value_sorted = invest_df.sort_values(by=(index_date,  value_type))[index_date]
    value_sorted[value_type + '_rank'] = value_sorted[value_type].rank()
    return value_sorted[[value_type, value_type + '_rank']][:num]


# function for Value Investing Strategy
def make_value_combo(value_list, invest_df, index_date, num):
    
    for idx, value in enumerate(value_list):
        temp_df = get_value_rank(invest_df, value, index_date, None)
        if idx == 0:
            value_combo_df = temp_df
            rank_combo = temp_df[value + '_rank']
        else:
            value_combo_df = pd.merge(value_combo_df, temp_df, how='outer', left_index=True, right_index=True)
            rank_combo = rank_combo + temp_df[value + '_rank']
    
    value_combo_df['total_rank'] = rank_combo.rank()
    value_combo_df = value_combo_df.sort_values(by='total_rank')
    
    return value_combo_df[:num]


# function for F-Score Investing Strategy
def get_fscore(fs_df, index_date, num):
    fscore_df = fs_df[index_date]
    fscore_df['net income score'] = fscore_df['당기순이익'] > 0    # return boolean (True: 1, False: 0)
    fscore_df['cash flow score'] = fscore_df['영업활동으로인한현금흐름'] > 0     # return boolean (True: 1, False: 0)
    fscore_df['greater cash flow score'] = fscore_df['영업활동으로인한현금흐름'] > fscore_df['당기순이익']   # return boolean (True: 1, False: 0)
    fscore_df['total_score'] = fscore_df[['net income score', 'cash flow score', 'greater cash flow score']].sum(axis=1)    # taking sum of rows
    fscore_df = fscore_df[fscore_df['total_score'] == 3]
    return fscore_df[:num]


# function for Momentum Investing Strategy
def get_momentum_rank(price_df, index_date, date_range, num):
    momentum_df = pd.DataFrame(price_df.pct_change(date_range).loc[index_date]) # putting a series in a dataframe structure
    momentum_df.columns = ['momentum'] # naming a column 'momentum'
    momentum_df['momentum_rank'] = momentum_df['momentum'].rank(ascending=False) # ranking in descending manner
    momentum_df = momentum_df.sort_values(by='momentum_rank') # sorting by momentum_rank
    return momentum_df[:num]


# function for Value + Quality Investing Strategy
def get_value_quality(invest_df, fs_df, index_date, num):
    value = make_value_combo(['PER', 'PBR', 'PSR', 'PCR'], invest_df, index_date, None)
    quality = get_fscore(fs_df, index_date, None)
    value_quality = pd.merge(value, quality, how='outer', left_index=True, right_index=True) # merging two df
    value_quality_filtered = value_quality[value_quality['total_score'] == 3] # filtering only those who have a f-score of 3
    vq_df = value_quality_filtered.sort_values(by='total_rank') # sorting by the total_rank, which is based on values_rank
    return vq_df[:num]