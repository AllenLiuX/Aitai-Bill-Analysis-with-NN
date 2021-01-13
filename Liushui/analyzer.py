# -- coding:UTF-8 --
import pandas as pd
import numpy as np
import time
import Modules.mongodb as mongo
import Modules.public_module as md
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


if __name__ == '__main__':
    start_time = time.time()
    calculation_A('yikong', '1', 'output/yikongtest.xlsx')
    print('======= Time taken: %f =======' % (time.time() - start_time))
