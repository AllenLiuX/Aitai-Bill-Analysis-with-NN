# -- coding:UTF-8 --
import pandas as pd
import numpy as np
import time
import Modules.mongodb as mongo
import Modules.public_module as md

'''
以每个公司为一个Verifier，从sheet_info里提取公司所含所有表单的基本信息和定位（file+table), 并根据定位依次处理每个表单
'''
class Verifier:
    def __init__(self, company):
        self.company = company
        self.file_paths = []        # [[file1, table1], [file2, table2], ...]
        self.dates = []
        self.self_accounts = []
        self.path2account = {}

    def get_paths(self):
        return self.file_paths

    def get_infos(self):
        # forms = mongo.show_datas(self.name, {'type': 'form'}, 'mapping')
        datas = mongo.show_datas('sheet_info', {'company': self.company}, 'Info')

        for form in datas:
            self.file_paths.append([form['file'], form['table']])
            if form['start_date'] and form['end_date']:
                self.dates.append([form['start_date'], form['end_date']])
            if form['self_account']:
                self.self_accounts.append(form['self_account'])
            self.path2account[form['file']+form['table']] = form['self_account']

        # final_df = pd.read_json(datas[0]['data'])
        # for i in range(1, len(datas)):
        #     cur_table = datas[i]['data']
        #     cur_df = pd.read_json(cur_table)
        #     final_df = pd.concat([final_df, cur_df], ignore_index=True)
        # print(final_df)

        # make dates from str to int
        for d in range(len(self.dates)):
            if self.dates[d][0] and self.dates[d][1]:
                self.dates[d][0] = int(self.dates[d][0])
                self.dates[d][1] = int(self.dates[d][1])
            else:
                continue
        print(self.file_paths)
        print(self.dates)
        print(self.self_accounts)
        return True

    """
       @:param error_tolerance 是交易后算余额所能容忍的误差值。建议设置大于1
    """
    def balance_check(self, error_tolerance, file_path):
        # cur_df = pd.read_excel(file_path)
        datas = mongo.show_datas('mapped_df', {'file': file_path[0], 'table': file_path[1]}, 'Cache')
        cur_df = pd.read_json(datas[-1]['data'])
        invalid = []
        cur_df['流入金额'].fillna(0, inplace=True)
        cur_df['流出金额'].fillna(0, inplace=True)
        skip = False
        try:
            cur_df['流入金额'] = cur_df['流入金额'].astype(int)
            cur_df['流出金额'] = cur_df['流出金额'].astype(int)
        except Exception as e:
            print(e)
            print('failed to convert datatype to in for income and out money')
            skip = True
        income = cur_df['流入金额'].values
        out = cur_df['流出金额'].values
        balance = cur_df['交易后余额'].values
        if not skip:
            for i in range(1, len(income)):
                try:
                    if not income[i] is None and not pd.isna(income[i]) and income[i] != 0:
                        if abs(balance[i-1] + income[i] - balance[i]) > error_tolerance:
                            invalid.append(i)
                    elif not out[i] is None and not pd.isna(out[i]) and out[i] != 0:
                        if abs(balance[i-1] - out[i] != balance[i]) > error_tolerance:
                            invalid.append(i)
                except Exception as e:
                    print(income, i)
                    print(e)
                    print(type(income[i]))
                    print(income[i])
                    exit(1)
                # else:
                #     invalid.append(i)
        # print(cur_df.loc[invalid]['交易日期'].values[:5])
        invalid_dates = cur_df.loc[invalid]['交易日期'].values.tolist()     # 提取所有不正确余额对应的日期 <class 'numpy.ndarray'>
        print('ratio of invalid balance: ', len(invalid_dates)/len(income))
        return invalid_dates

    def benford_check(self, file_path):
        # cur_df = pd.read_excel(file_path)
        datas = mongo.show_datas('mapped_df', {'file': file_path[0], 'table': file_path[1]}, 'Cache')
        cur_df = pd.read_json(datas[-1]['data'])
        income = cur_df['流入金额'].values
        out = cur_df['流出金额'].values
        # balance = cur_df['交易后余额'].values
        income2, out2, balance2 = [], [], []
        # print(income)
        try:
            cur_df['流入金额'] = cur_df['流入金额'].astype(int)
            cur_df['流出金额'] = cur_df['流出金额'].astype(int)
        except Exception as e:
            print(e)
            print('failed to convert datatype to in for income and out money')
            return 'benford_check failed'
        for i in range(len(income)):
            if not np.isnan(income[i]):
                income2.append(income[i])
            if not np.isnan(out[i]):
                out2.append(out[i])
        all = income2 + out2
        res = md.benford(all)
        print('benford coefficient: ', res[0])
        print('total samples: ', len(all))
        return res[0], len(all)

    def info_missing_check(self, file_path):
        # cur_df = pd.read_excel(file_path)
        datas = mongo.show_datas('mapped_df', {'file': file_path[0], 'table': file_path[1]}, 'Cache')
        cur_df = pd.read_json(datas[-1]['data'])
        abstract = cur_df['摘要'].values
        receiver_name = cur_df['对方名称'].values
        abstract_num = 0
        receiver_num = 0
        for i in range(len(abstract)):
            if type(abstract[i]) != str:
                abstract_num += 1
            if type(receiver_name[i]) != str:
                receiver_num += 1
        print('缺失的对方名称有：', receiver_num)
        print('缺失的摘要有：', abstract_num)
        return [abstract_num, receiver_num]

    def dates_check(self):
        merged_dates = md.merge_dates(self.dates)
        print('the merged dates are:', merged_dates)
        return merged_dates

    def inner_account_check(self):
        invalid_accounts = []
        for path in self.file_paths:
            # cur_df = pd.read_excel(path)
            datas = mongo.show_datas('mapped_df', {'file': path[0], 'table': path[1]}, 'Cache')
            cur_df = pd.read_json(datas[-1]['data'])
            accounts = []       # 对方账号
            for index in cur_df.index:      # 逐行找向自己公司转账的条目，并提取账号
                if cur_df.loc[index, '对方名称'] == self.company:
                    cur_account = cur_df.loc[index, '对方账号']
                    accounts.append(cur_account)
                    if cur_account not in self.self_accounts:
                        invalid_accounts.append(cur_account)
        print('missing accounts:', invalid_accounts)
        return invalid_accounts

    def cross_validation(self):
        invalid_accounts = []
        account2df = {}
        # 先把账号下表格都打开
        for path in self.file_paths:
            # cur_df = pd.read_excel(path)
            datas = mongo.show_datas('mapped_df', {'file': path[0], 'table': path[1]}, 'Cache')
            cur_df = pd.read_json(datas[-1]['data'])
            account2df[self.path2account[path[0]+path[1]]] = cur_df

        account2trans = {}
        for account in self.self_accounts:
            cur_df = account2df[account]

            accounts = []  # 对方账号
            for index in cur_df.index:  # 逐行找向自己公司转账的条目，并提取账号
                if cur_df.loc[index, '对方名称'] == self.company:
                    cur_account = cur_df.loc[index, '对方账号']
                    accounts.append(cur_account)
                    if cur_account not in self.self_accounts:
                        invalid_accounts.append(cur_account)
                    cur_trans = cur_df.loc[index]
                    if account not in account2trans:
                        account2trans[account] = [cur_trans]
                    else:
                        account2trans[account].append(cur_trans)

        unmatched_trans = []
        for from_acc, trans in account2trans.items():
            for tran in trans:
                tran_date = tran.loc['交易日期']
                tran_in = tran.loc['流入金额']
                tran_out = tran.loc['流出金额']
                out_acc = tran.loc['对方账号']
                if out_acc in account2df:
                    to_df = account2df[out_acc]
                else:
                    print('not existed account: ', out_acc)
                    continue
                matched = False
                for index in cur_df.index:      # 为什么这里cur_df没有declare过？？
                    if cur_df.loc[index, '对方账号'] == from_acc and cur_df.loc[index, '交易日期'] == tran_date:
                        if cur_df.loc[index, '流入金额'] == tran_out or cur_df.loc[index, '流出金额'] == tran_in:
                            print('Get one matched transaction.', from_acc, out_acc)
                            matched = True
                            break
                if not matched:
                    print('---- not matched!----\n', tran)
                    unmatched_trans.append(tran)

        # print('missing accounts:', invalid_accounts)
        return unmatched_trans


def run(name):
    verifier = Verifier(name)
    infostatus = verifier.get_infos()
    if not infostatus:
        return 'invalid name'
    print(verifier.get_paths())
    res = {}
    print('------ Reports ------')
    for path in verifier.get_paths():
        cur_info = {}
        print('----- '+path[0]+path[1]+' ------')
        cur_info['balence_error_dates'] = verifier.balance_check(1, path)
        cur_info['benford'] = verifier.benford_check(path)
        infomiss = verifier.info_missing_check(path)
        cur_info['abstract_missing'] = infomiss[0]
        cur_info['receiver_missing'] = infomiss[1]
        res[path[0]+path[1]] = cur_info
    print('----- overall report -----')
    res['dates_coverage'] = verifier.dates_check()
    res['missing_accounts'] = verifier.inner_account_check()
    res['unmatched_trans'] = verifier.cross_validation()
    return res


if __name__ == '__main__':
    start_time = time.time()
    res = run('yikong')
    print(res)
    print("--- %s seconds ---" % (time.time() - start_time))