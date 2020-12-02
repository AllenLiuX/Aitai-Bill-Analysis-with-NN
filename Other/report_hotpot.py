# -- coding:UTF-8 --
import numpy as np
import pandas as pd
import os, sys
import seaborn as sns
import time


input_file = '锅圈_jxhwmx_data.xlsx'

def get_items(df, col):
    vals = df[col].values
    items = list(set(vals))
    return items

if __name__ == '__main__':
    start_time = time.time()
    pd.set_option('display.float_format', lambda x: '%.3f' % x)
    df = pd.read_excel(input_file)
    df = df[df['kprq'].str.contains('2020')]
    types = get_items(df, 'goods_l1')
    # print(types)

    # 年度报告
    info_by_year = {}
    for type in types:
        df_type = df[df['goods_l1'] == type]
        je_sum = np.sum(df_type['je'].values)
        info_by_year[type] = {'total': round(je_sum, 2)}
        providers = get_items(df_type, 'xfmc')
        second_info = {}
        for provider in providers:
            df_provide = df[df['xfmc'] == provider]
            je_sum = np.sum(df_provide['je'].values)
            second_info[provider] = je_sum
        info_by_year[type].update(second_info)
    print(info_by_year)

    # 月度报告
    info_by_month = {}
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    for month in months:
        df_month = df[df['kprq'].str.contains('2020-'+month)]
        month_info = {}
        for type in types:
            df_type = df_month[df_month['goods_l1'] == type]
            je_sum = np.sum(df_type['je'].values)
            month_info[type] = {'total': round(je_sum, 2)}
        info_by_month[month] = month_info
    print(info_by_month)

    # 交易对手
    info_by_provider = {}
    providers = get_items(df, 'xfmc')
    for provider in providers:
        df_provide = df[df['xfmc'] == provider]
        je_sum = np.sum(df_provide['je'].values)
        info_by_provider[provider] = {'total': round(je_sum, 2)}
        for month in months:
            df_month = df_provide[df_provide['kprq'].str.contains('2020-' + month)]
            je_sum = np.sum(df_month['je'].values)
            info_by_provider[provider].update({month: round(je_sum, 2)})
    print(info_by_provider)

    provider_df = pd.DataFrame(info_by_provider)
    provider_df = provider_df.stack().unstack(0)
    print(provider_df)
    writer = pd.ExcelWriter('provider summary.xlsx')
    provider_df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    print('DataFrame is written successfully to the Excel File.')



    end_time = time.time()
    print('======= Time taken: %f =======' %(end_time - start_time))
