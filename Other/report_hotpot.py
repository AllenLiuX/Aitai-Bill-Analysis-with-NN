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
    type_all_df.to_excel('output/type summary.xlsx', sheet_name='Sheet1')
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
    provider_df.to_excel('output/provider summary.xlsx', sheet_name='Sheet1')
    print('DataFrame is written successfully to the Excel File.')


def provider_freq_analysis():
    provider_df = pd.read_excel('output/provider summary.xlsx')
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
    summary_df.to_excel('output/provider_month_count.xlsx')
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
    # plt.show()
    plt.savefig('plot/供应商交易月数量分布')
    print(summary_count)


def first_last_occur_analysis():
    df = pd.read_excel('output/provider summary.xlsx')
    cols = df.columns.ravel()
    unnamed = [i for i in cols if re.search(r'Unnamed.*', i)]
    for i in unnamed:
        df = df.drop(columns=i)
    df = df[df['type'] == '合计']
    first_occur = {}
    last_occur = {}
    first_month_to_money = {}
    last_month_to_money = {}
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
        if first in first_month_to_money:
            first_month_to_money[first] += row_val[first - 1]
        else:
            first_month_to_money[first] = row_val[first - 1]
        if last in last_month_to_money:
            last_month_to_money[last] += row_val[last - 1]
        else:
            last_month_to_money[last] = row_val[last - 1]

    # generate first df and last df
    first_company_to_month = {'公司': list(first_occur.keys()), '月份': list(first_occur.values())}
    first_df = pd.DataFrame(first_company_to_month)
    first_df = first_df.sort_values(by='月份', ascending=False)
    print(first_df)
    first_df.to_excel('output/first_occur.xlsx')
    last_company_to_month = {'公司': list(last_occur.keys()), '月份': list(last_occur.values())}
    last_df = pd.DataFrame(last_company_to_month)
    last_df = last_df.sort_values(by='月份', ascending=False)
    print(last_df)
    last_df.to_excel('output/last_occur.xlsx')

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
    # plt.show()
    plt.savefig('plot/每月新增供应商数量')
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
    # plt.show()
    plt.savefig('plot/每月流失供应商数量')
    print(summary_count)

    # calculate money for first and last in each month
    print(first_month_to_money)
    all_money_dic = {}
    for month in months[:-1]:  # remove month 12
        month_all = np.sum(df[month].values)
        all_money_dic[int(month)] = month_all
    print(all_money_dic)
    first_ratio = {}
    last_ratio = {}
    for key, val in first_month_to_money.items():
        first_ratio[key] = val / all_money_dic[key]
    for key, val in last_month_to_money.items():
        last_ratio[key] = val / all_money_dic[key]
    print(first_ratio)

    ## calculate money in all for each first and last month
    company_to_money = df.set_index('company')['total'].to_dict()
    first_month_to_company = {}
    last_month_to_company = {}
    first_month_to_money_all = {}
    last_month_to_money_all = {}
    # print(first_company_to_month)
    for key, val in first_occur.items():
        if val in first_month_to_company:
            first_month_to_company[val] += [key]
            first_month_to_money_all[val] += company_to_money[key]
        else:
            first_month_to_company[val] = [key]
            first_month_to_money_all[val] = company_to_money[key]
    for key, val in last_occur.items():
        if val in last_month_to_company:
            last_month_to_company[val] += [key]
            last_month_to_money_all[val] += company_to_money[key]
        else:
            last_month_to_company[val] = [key]
            last_month_to_money_all[val] = company_to_money[key]
    
    first_month_to_all = {}  # eg 3月计算3月到12月一共的公司总金额
    last_month_to_all = {}
    first_sum = 0
    last_sum = 0
    for i in months[:-1]:  # ['01', '02', ..., '11']
        first_cur = 12 - int(i)
        last_cur = int(i)
        first_sum += all_money_dic[first_cur]
        first_month_to_all[first_cur] = first_sum
        last_sum += all_money_dic[last_cur]
        last_month_to_all[last_cur] = last_sum
    print(first_month_to_all)  # 公司持续总金额
    print(last_month_to_all)

    # calculate ratio of month / all
    first_ratio_all = {}
    last_ratio_all = {}
    for key, val in first_month_to_money_all.items():
        first_ratio_all[key] = val / first_month_to_all[key]
    for key, val in last_month_to_money_all.items():
        last_ratio_all[key] = val / last_month_to_all[key]
    print(first_ratio_all)
    
    # generate excel
    first_all = {'新增供应商月度总金额': first_month_to_money, '公司总月度金额': all_money_dic, '月度金额占比': first_ratio,
                 '新增供应商持续总金额': first_month_to_money_all, '公司总持续金额': first_month_to_all, '持续金额占比': first_ratio_all}
    first_all_df = pd.DataFrame(first_all)
    first_all_df = first_all_df.sort_index()
    first_all_df.to_excel('output/新增月金额占比统计.xlsx')

    last_all = {'新增供应商月度总金额': last_month_to_money, '公司总月度金额': all_money_dic, '金额月度占比': last_ratio,
                '新增供应商持续总金额': last_month_to_money_all, '公司总持续金额': last_month_to_all, '持续金额占比': last_ratio_all}
    last_all_df = pd.DataFrame(last_all)
    last_all_df = last_all_df.sort_index()
    last_all_df.to_excel('output/流失月金额占比统计.xlsx')


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

    # 月度交易对手频次分析
    # provider_freq_analysis()

    # 新增流失交易方金额及占比分析
    first_last_occur_analysis()


    end_time = time.time()
    print('======= Time taken: %f =======' %(end_time - start_time))
