import pandas as pd
import numpy as np
import time
import Modules.mongodb as mongo
import Modules.public_module as md

class Analyzer:
    def __init__(self, name):
        self.name = name
        self.company_name = ''
        self.file_paths = []
        self.dates = []
        self.self_accounts = []

    """
    @:param error_tolerance 是交易后算余额所能容忍的误差值。建议设置大于1
    """
    def get_paths(self):
        return self.file_paths

    def get_infos(self):
        forms = self.base_rules = mongo.show_datas(self.name, {'type': 'form'}, 'mapping')
        for form in forms:
            self.file_paths.append(form['path'])
            self.dates.append(form['dates'])
            self.self_accounts.append(form['account'])
        self.company_name = forms[0]['company_name']
        # make dates from str to int
        for d in range(len(self.dates)):
            self.dates[d][0] = int(self.dates[d][0])
            self.dates[d][1] = int(self.dates[d][1])
        print(self.file_paths)
        print(self.dates)
        print(self.self_accounts)


    def balance_check(self, error_tolerance, file_path):
        cur_df = pd.read_excel(file_path)
        invalid = []
        income = cur_df['流入金额'].values
        out = cur_df['流出金额'].values
        balance = cur_df['交易后余额'].values
        for i in range(1, len(income)):
            if not np.isnan(income[i]):
                if abs(balance[i-1] + income[i] - balance[i]) > error_tolerance:
                    invalid.append(i)
            elif not np.isnan(out[i]):
                if abs(balance[i-1] - out[i] != balance[i]) > error_tolerance:
                    invalid.append(i)
            else:
                invalid.append(i)
        # print(cur_df.loc[invalid]['交易日期'].values[:5])
        invalid_dates = cur_df.loc[invalid]['交易日期'].values     # 提取所有不正确余额对应的日期
        print('ratio of invalid balance: ', len(invalid_dates)/len(income))
        return invalid_dates

    def benford_check(self, file_path):
        cur_df = pd.read_excel(file_path)
        income = cur_df['流入金额'].values
        out = cur_df['流出金额'].values
        # balance = cur_df['交易后余额'].values
        income2, out2, balance2 = [], [], []
        # print(income)
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
        cur_df = pd.read_excel(file_path)
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
        return abstract_num, receiver_num


    def dates_check(self):
        merged_dates = md.merge_dates(self.dates)
        print('the merged dates are:', merged_dates)
        return merged_dates

    def inner_account_check(self):
        invalid_accounts = []
        for path in self.file_paths:
            cur_df = pd.read_excel(path)
            accounts = []       # 对方账号
            for index in cur_df.index:      # 逐行找向自己公司转账的条目，并提取账号
                if cur_df.loc[index, '对方名称'] == self.company_name:
                    cur_account = cur_df.loc[index, '对方账号']
                    accounts.append(cur_account)
                    if cur_account not in self.self_accounts:
                        invalid_accounts.append(cur_account)
        print('missing accounts:', invalid_accounts)



def run(name):
    analyst = Analyzer(name)
    analyst.get_infos()

    print('------ Reports ------')
    for path in analyst.get_paths():
        print('----- '+path+' ------')
        analyst.balance_check(0, path)
        analyst.benford_check(path)
        analyst.info_missing_check(path)
    print('----- overall report -----')
    analyst.dates_check()
    analyst.inner_account_check()

if __name__ == '__main__':
    start_time = time.time()
    run('aitai')
    print("--- %s seconds ---" % (time.time() - start_time))