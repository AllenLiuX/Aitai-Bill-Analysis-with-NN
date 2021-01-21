# -- coding:UTF-8 --
import pandas as pd
import numpy as np
import time
import Modules.mongodb as mongo
import Modules.public_module as md
import mydata
import time
import datetime


def expand_date(df, start_date, end_date):
    start = datetime.datetime.strptime(start_date, '%Y%m%d').date()
    end = datetime.datetime.strptime(end_date, '%Y%m%d').date()
    df['date'] = df['交易日期'].apply(str)
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    df = df.loc[:, ('date', '流入金额', '流出金额', '交易后余额')]
    df.index = df['date']
    df = df.drop(columns='date')
    index = pd.date_range(start_date, end_date, freq='1d')
    new_df = pd.DataFrame(columns=['in', 'out', 'balance'], index=index)
    new_df['in'].fillna(value=0, inplace=True)
    new_df['out'].fillna(value=0, inplace=True)
    for i in df.index:
        date_df = df.loc[i]
        if isinstance(date_df, pd.DataFrame):   # this step is to cut data exceed the start and end dates
            date = date_df.index[0]
            if date < start or date > end:
                continue
        else:
            date = date_df.name
            if date < start or date > end:
                continue
        in_sum = date_df['流入金额'].sum()
        out_sum = date_df['流出金额'].sum()
        new_df.loc[i, 'in'] = in_sum
        new_df.loc[i, 'out'] = out_sum

    cur_balance = df.iloc[0].loc['交易后余额'] - df.iloc[0].loc['流入金额'] + df.iloc[0].loc['流出金额']
    for i in new_df.index:  # 每天看是否有新的余额更新
        try:
            date_df = df.loc[i]
            if isinstance(date_df, pd.DataFrame):
                date = date_df.index[0]  # this step is to cut data exceed the start and end dates
                if date < start or date > end:
                    continue
                cur_balance = date_df.iloc[-1].loc['交易后余额']
            else:
                date = date_df.name
                if date < start or date > end:
                    continue
                cur_balance = date_df.loc['交易后余额']
        except:
            pass    # no date was found, use previous balance
        new_df.loc[i, 'balance'] = cur_balance
    # print(df['交易后余额'])
    # print(df[df.index.duplicated()])
    # print(df['交易后余额'].resample('30d').asfreq()[0:5])
    return new_df


def calculation_A(company, batch_id, file_output):
    infos = mongo.show_datas('sheet_info', query={'company': company, 'batch_id': batch_id}, db='Info')
    dfs = []
    for info in infos:
        print(info['file'], info['table'])
        data = mongo.show_datas('mapped_df', {'file': info['file'], 'table': info['table'], 'batch_id': batch_id},
                                'Cache')
        cur_df = pd.read_json(data[0]['data'])
        cur_df = expand_date(cur_df, info['start_date'], info['end_date'])
        # print(cur_df)
        dfs.append(cur_df)
    all_df = pd.DataFrame(columns=['in', 'out', 'balance'])
    for df in dfs:
        all_df = all_df.add(df, fill_value=0)
    print(all_df)
    balance_all = all_df['balance']
    in_all = all_df['in'].resample('1M', label='left', loffset=datetime.timedelta(days=1), closed='left').sum()
    out_all = all_df['out'].resample('1M', label='left', loffset=datetime.timedelta(days=1), closed='left').sum()
    print(balance_all, in_all, out_all, sep='\n')
    return balance_all, in_all, out_all


def get_dfs_by_company(company, batch_id):
    datas = mongo.show_datas('mapped_df', query={'company': company, 'batch_id': batch_id}, db='Cache')
    df = pd.read_json(datas[0]['data'])
    for data in datas[1:]:
        cur_df = pd.read_json(data['data'])
        df = df.append(cur_df)  # 记得赋值！
    df.rename(columns=mydata.english_mapping, inplace=True)
    df['year'] = df['date'].apply(lambda x: str(x)[:4])
    return df

def calculate_A_type(company, batch_id):
    df = get_dfs_by_company(company, batch_id)
    # df = df.loc[:, ['date', 'receiver_name', 'received_amount', 'sent_amount', 'system_classification']]
    # df['system_classification'] = df['system_classification'].fillna('其他')
    in_and_out = ['received_amount', 'sent_amount']
    result = {}
    for inout_standard in in_and_out:
        in_or_out_df = df[df[inout_standard] > 0]
        if inout_standard == 'received_amount':
            in_or_out_df['system_classification'] = in_or_out_df['system_classification'].fillna('其他收入')
        else:
            in_or_out_df['system_classification'] = in_or_out_df['system_classification'].fillna('其他支出')
        # calculate the sum of money for each year
        year_to_money = {}
        years = list(set(in_or_out_df['year'].tolist()))
        for year in years:
            year_df = in_or_out_df[in_or_out_df['year'] == year]
            year_to_money[year] = year_df['received_amount'].sum()+year_df['sent_amount'].sum()

        type_to_year = {}
        types = list(set(in_or_out_df['system_classification'].tolist()))
        for cur_type in types:
            type_df = in_or_out_df[in_or_out_df['system_classification'] == cur_type]
            year_to_data = {}
            years = list(set(type_df['year'].tolist()))
            for year in years:
                year_df = type_df[type_df['year'] == year]
                year_df = year_df.drop(columns=['year'])
                money = year_df['received_amount'].sum()+year_df['sent_amount'].sum()
                data = {'number': year_df.shape[0],
                        'money': money,
                        'ratio': money/year_to_money[year],
                        'transactions': year_df}
                year_to_data[year] = data
            type_to_year[cur_type] = year_to_data
        if inout_standard == 'received_amount':
            result['in_data'] = type_to_year
        else:
            result['out_data'] = type_to_year
    # print(result)
    return result


def rival_calculate(company, batch_id):
    df = get_dfs_by_company(company, batch_id)
    in_and_out = ['received_amount', 'sent_amount']
    result = {}
    for inout_standard in in_and_out:
        in_or_out_df = df[df[inout_standard] > 0]
        year_to_data = {}
        years = list(set(in_or_out_df['year'].tolist()))
        for year in years:
            year_df = in_or_out_df[in_or_out_df['year'] == year]
            year_sum_money = year_df['received_amount'].sum() + year_df['sent_amount'].sum()
            rival_to_data = {}
            rivals = list(set(year_df['receiver_name'].tolist()))
            for rival in rivals:
                rival_df = year_df[year_df['receiver_name'] == rival]
                money = rival_df['received_amount'].sum()+rival_df['sent_amount'].sum()
                data = {'money': money,
                        'ratio': money / year_sum_money}
                rival_to_data[rival] = data
            # year_to_data[year] = rival_to_data
            summary_df = pd.DataFrame(rival_to_data)
            summary_df = summary_df.stack().unstack(0)
            summary_df = summary_df.sort_values(by='money', ascending=False)
            summary_df = summary_df.iloc[:20, :]
            year_to_data[year] = summary_df
            # rivals.append(summary_df.index.tolist())
        # print(rivals)
        # print(len(rivals))
            # 按年份排序
        rivals = [year_to_data[i].index.tolist() for i in sorted(year_to_data.keys())]
        print(rivals)
        two_duplicate = []
        three_duplicate = []
        for i in range(len(rivals)-1):
            dup2 = set(rivals[i]) & set(rivals[i+1])
            two_duplicate.append(list(dup2))
            if i < len(rivals)-2:
                dup3 = set(rivals[i]) & set(rivals[i+1]) & set(rivals[i+2])
                three_duplicate.append(list(dup3))
        # print(two_duplicate, three_duplicate)
        if inout_standard ==   'received_amount':
            result['in_data'] = year_to_data
            result['in_two_duplicate'] = two_duplicate
            result['in_three_duplicate'] = three_duplicate
        else:
            result['out_data'] = year_to_data
            result['out_two_duplicate'] = two_duplicate
            result['out_three_duplicate'] = three_duplicate
    # print(result)
    return result


if __name__ == '__main__':
    start_time = time.time()
    # calculation_A('yikong', '1', 'output/yikongtest.xlsx')
    # calculate_A_type('yikong', '1')
    rival_calculate('yikong', '1')
    print('======= Time taken: %f =======' % (time.time() - start_time))
