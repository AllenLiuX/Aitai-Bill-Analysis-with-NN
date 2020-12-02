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
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    df = pd.read_excel(input_file)
    df = df[df['kprq'].str.contains('2020')]
    types = get_items(df, 'goods_l1')
    # print(types)

    # # 年度报告
    # info_by_year = {}
    # for type in types:
    #     type_df = df[df['goods_l1'] == type]
    #     je_sum = np.sum(type_df['je'].values)
    #     info_by_year[type] = {'total': round(je_sum, 2)}
    #     providers = get_items(type_df, 'xfmc')
    #     second_info = {}
    #     for provider in providers:
    #         provide_df = df[df['xfmc'] == provider]
    #         je_sum = np.sum(provide_df['je'].values)
    #         second_info[provider] = je_sum
    #     info_by_year[type].update(second_info)
    # # print(info_by_year)
    # 
    # # 月度报告
    # info_by_month = {}
    # for month in months:
    #     month_df = df[df['kprq'].str.contains('2020-'+month)]
    #     month_info = {}
    #     for type in types:
    #         type_df = month_df[month_df['goods_l1'] == type]
    #         je_sum = np.sum(type_df['je'].values)
    #         month_info[type] = {'total': round(je_sum, 2)}
    #     info_by_month[month] = month_info
    # print(info_by_month)

    # 大类分析
    info_by_type = {}
    types = get_items(df, 'goods_l1')
    for type in types:
        type_df = df[df['goods_l1'] == type]
        je_sum = np.sum(type_df['je'].values)
        info_by_type[type + '-合计'] = {'total': round(je_sum, 2)}
        cur_providers = get_items(type_df, 'xfmc')
        for provider in cur_providers:
            provide_df = type_df[type_df['xfmc'] == provider]
            je_sum = np.sum(provide_df['je'].values)
            info_by_type[type + '-' + provider] = {'total': round(je_sum, 2)}
            for month in months:
                # calculate total row
                month_df = type_df[type_df['kprq'].str.contains('2020-' + month)]
                je_sum = np.sum(month_df['je'].values)
                info_by_type[type + '-合计'].update({month: round(je_sum, 2)})
                # calculate type row
                df_provider_month = provide_df[provide_df['kprq'].str.contains('2020-' + month)]
                je_sum = np.sum(df_provider_month['je'].values)
                info_by_type[type + '-' + provider].update({month: round(je_sum, 2)})

    type_all_df = pd.DataFrame(info_by_type)
    type_all_df = type_all_df.stack().unstack(0)
    ids = type_all_df.index.ravel()
    type = [i.split('-')[0] for i in ids]
    company = [i.split('-')[1] for i in ids]
    type_all_df['type'] = type
    type_all_df['company'] = company
    type_all_df.index = pd.Series([i for i in range(type_all_df.shape[0])])
    print(type_all_df)
    type_all_df.to_excel('type summary.xlsx', sheet_name='Sheet1')
    print('DataFrame is written successfully to the Excel File.')

    # 交易对手
    info_by_provider = {}
    providers = get_items(df, 'xfmc')
    for provider in providers:
        provide_df = df[df['xfmc'] == provider]
        je_sum = np.sum(provide_df['je'].values)
        info_by_provider[provider+'-合计'] = {'total': round(je_sum, 2)}
        cur_types = get_items(provide_df, 'goods_l1')
        for type in cur_types:
            type_df = provide_df[provide_df['goods_l1'] == type]
            je_sum = np.sum(type_df['je'].values)
            info_by_provider[provider + '-'+type] = {'total': round(je_sum, 2)}
            for month in months:
                # calculate total row
                month_df = provide_df[provide_df['kprq'].str.contains('2020-' + month)]
                je_sum = np.sum(month_df['je'].values)
                info_by_provider[provider+'-合计'].update({month: round(je_sum, 2)})
                # calculate type row
                df_type_month = type_df[type_df['kprq'].str.contains('2020-' + month)]
                je_sum = np.sum(df_type_month['je'].values)
                info_by_provider[provider + '-'+type].update({month: round(je_sum, 2)})

    # print(info_by_provider)

    provider_df = pd.DataFrame(info_by_provider)
    provider_df = provider_df.stack().unstack(0)
    ids = provider_df.index.ravel()
    company = [i.split('-')[0] for i in ids]
    type = [i.split('-')[1] for i in ids]
    provider_df['company'] = company
    provider_df['type'] = type
    provider_df.index = pd.Series([i for i in range(provider_df.shape[0])])
    print(provider_df)
    provider_df.to_excel('provider summary.xlsx', sheet_name='Sheet1')
    print('DataFrame is written successfully to the Excel File.')

    # # count provider frequency
    # provider_all_df = provider_df[provider_df['type'] == '合计']
    # for index in provider_all_df.index:
    #

    end_time = time.time()
    print('======= Time taken: %f =======' %(end_time - start_time))
