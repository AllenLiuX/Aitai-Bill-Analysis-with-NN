# -- coding:UTF-8 --
import numpy as np
import pandas as pd
import os, sys
import seaborn as sns
import matplotlib.pyplot as plt
import time
import re


input_file = '锅圈_jxhwmx_data.xlsx'
months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

def get_items(df, col):
    vals = df[col].values
    items = list(set(vals))
    return items


def year_analysis(df):
    info_by_year = {}
    types = get_items(df, 'goods_l1')
    for type in types:
        type_df = df[df['goods_l1'] == type]
        je_sum = np.sum(type_df['je'].values)
        info_by_year[type] = {'total': round(je_sum, 2)}
        providers = get_items(type_df, 'xfmc')
        second_info = {}
        for provider in providers:
            provide_df = df[df['xfmc'] == provider]
            je_sum = np.sum(provide_df['je'].values)
            second_info[provider] = je_sum
        info_by_year[type].update(second_info)
    # print(info_by_year)


def month_analysis(df):
    info_by_month = {}
    types = get_items(df, 'goods_l1')
    for month in months:
        month_df = df[df['kprq'].str.contains('2020-'+month)]
        month_info = {}
        for type in types:
            type_df = month_df[month_df['goods_l1'] == type]
            je_sum = np.sum(type_df['je'].values)
            month_info[type] = {'total': round(je_sum, 2)}
        info_by_month[month] = month_info
    print(info_by_month)


def type_analysis(df):
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


def  provider_analysis(df):
    info_by_provider = {}
    providers = get_items(df, 'xfmc')
    for provider in providers:
        provide_df = df[df['xfmc'] == provider]
        je_sum = np.sum(provide_df['je'].values)
        info_by_provider[provider + '-合计'] = {'total': round(je_sum, 2)}
        cur_types = get_items(provide_df, 'goods_l1')
        for type in cur_types:
            type_df = provide_df[provide_df['goods_l1'] == type]
            je_sum = np.sum(type_df['je'].values)
            info_by_provider[provider + '-' + type] = {'total': round(je_sum, 2)}
            for month in months:
                # calculate total row
                month_df = provide_df[provide_df['kprq'].str.contains('2020-' + month)]
                je_sum = np.sum(month_df['je'].values)
                info_by_provider[provider + '-合计'].update({month: round(je_sum, 2)})
                # calculate type row
                df_type_month = type_df[type_df['kprq'].str.contains('2020-' + month)]
                je_sum = np.sum(df_type_month['je'].values)
                info_by_provider[provider + '-' + type].update({month: round(je_sum, 2)})

    # print(info_by_provider)
    provider_df = pd.DataFrame(info_by_provider)
    provider_df = provider_df.stack().unstack(0)  # transpose
    ids = provider_df.index.ravel()
    company = [i.split('-')[0] for i in ids]
    type = [i.split('-')[1] for i in ids]
    provider_df['company'] = company
    provider_df['type'] = type
    provider_df.index = pd.Series([i for i in range(provider_df.shape[0])])
    print(provider_df)
    provider_df.to_excel('provider summary.xlsx', sheet_name='Sheet1')
    print('DataFrame is written successfully to the Excel File.')


def provider_freq_analysis():
    provider_df = pd.read_excel('provider summary.xlsx')
    cols = provider_df.columns.ravel()
    unnamed = [i for i in cols if re.search(r'Unnamed.*', i)]
    for i in unnamed:
        provider_df = provider_df.drop(columns=i)
    provider_all_df = provider_df[provider_df['type'] == '合计']
    # print(provider_all_df)
    summary = {}
    for index in provider_all_df.index:
        row_val = provider_all_df.loc[index].values[:11]
        row_nonzero_val = [i for i in row_val if i != 0]
        summary[provider_all_df.loc[index]['company']] = len(row_nonzero_val)
    # print(summary)
    summary_dic = {'公司': list(summary.keys()), '交易月份数': list(summary.values())}
    summary_df = pd.DataFrame(summary_dic)
    summary_df = summary_df.sort_values(by='交易月份数', ascending=False)
    print(summary_df)
    summary_df.to_excel('provider_month_count.xlsx')
    summary_count = {}
    for key, val in summary.items():
        if val in summary_count:
            summary_count[val] += 1
        else:
            summary_count[val] = 1
    xs = list(summary_count.keys())
    ys = list(summary_count.values())
    plt.rcParams['font.family'] = ['Arial Unicode MS']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    sns.set_style('whitegrid', {'font.sans-serif': ['Arial Unicode MS', 'Arial']})
    bar_plot = sns.barplot(x=xs, y=ys, palette='muted')
    for a, b in zip(xs, ys):
        plt.text(a - 1, b, '%d' % b, ha='center', va='bottom', fontsize=7)
    plt.title('供应商交易月数量分布')
    plt.show()
    print(summary_count)


def first_last_occur_analysis():
    df = pd.read_excel('provider summary.xlsx')
    cols = df.columns.ravel()
    unnamed = [i for i in cols if re.search(r'Unnamed.*', i)]
    for i in unnamed:
        df = df.drop(columns=i)
    df = df[df['type'] == '合计']
    first_occur = {}
    last_occur = {}
    print(df)
    for index in df.index:
        row_val = df.loc[index, months].values
        company = df.loc[index, 'company']
        # print(row_val)
        first = -1
        last = -1
        for i in range(len(row_val)):
            if first == -1 and int(row_val[i]) != 0:
                first = i+1
            if row_val[i] != 0:
                last = i+1
        first_occur[company] = first
        last_occur[company] = last
    first_dic = {'公司': list(first_occur.keys()), '月份': list(first_occur.values())}
    first_df = pd.DataFrame(first_dic)
    first_df = first_df.sort_values(by='月份', ascending=False)
    print(first_df)
    first_df.to_excel('first_occur.xlsx')
    last_dic = {'公司': list(last_occur.keys()), '月份': list(last_occur.values())}
    last_df = pd.DataFrame(last_dic)
    last_df = last_df.sort_values(by='月份', ascending=False)
    print(last_df)
    last_df.to_excel('last_occur.xlsx')

    # count summary plot
    plt.rcParams['font.family'] = ['Arial Unicode MS']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    sns.set_style('whitegrid', {'font.sans-serif': ['Arial Unicode MS', 'Arial']})
    # first occur plot
    summary_count = {}
    for key, val in first_occur.items():
        if val in summary_count:
            summary_count[val] += 1
        else:
            summary_count[val] = 1
    xs = list(summary_count.keys())
    ys = list(summary_count.values())
    bar_plot = sns.barplot(x=xs, y=ys, palette='muted')
    for a, b in zip(xs, ys):
        plt.text(a - 1, b, '%d' % b, ha='center', va='bottom', fontsize=7)
    plt.title('每月新增供应商数量')
    plt.show()
    print(summary_count)
    # last occur plot
    summary_count = {}
    for key, val in last_occur.items():
        if val in summary_count:
            summary_count[val] += 1
        else:
            summary_count[val] = 1
    xs = list(summary_count.keys())
    ys = list(summary_count.values())
    plt.figure()
    bar_plot = sns.barplot(x=xs, y=ys, palette='muted')
    for a, b in zip(xs, ys):
        plt.text(a - 1, b, '%d' % b, ha='center', va='bottom', fontsize=7)
    plt.title('每月流失供应商数量')
    plt.show()
    print(summary_count)

if __name__ == '__main__':
    start_time = time.time()
    pd.set_option('display.float_format', lambda x: '%.3f' % x)
    df = pd.read_excel(input_file)
    df = df[df['kprq'].str.contains('2020')]

    # 年度报告
    # year_analysis(df)

    # 月度报告
    # month_analysis(df)

    # 大类分析
    # type_analysis(df)

    # 交易对手
    # provider_analysis(df)

    # count provider frequency
    # provider_freq_analysis()

    # first_last_occur
    first_last_occur_analysis()


    end_time = time.time()
    print('======= Time taken: %f =======' %(end_time - start_time))
