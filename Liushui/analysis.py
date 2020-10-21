import pandas as pd
import numpy as np
import time
# import Modules.mongodb as mongo
import Modules.public_module as md

class Analyzer:
    def __init__(self, file_path):
        self.all_df = pd.read_excel(file_path)

    """
    @:param error_tolerance 是交易后算余额所能容忍的误差值。建议设置大于1
    """
    def balance_check(self, error_tolerance):
        invalid = []
        income = self.all_df['流入金额'].values
        out = self.all_df['流出金额'].values
        balance = self.all_df['交易后余额'].values
        for i in range(1, len(income)):
            if not np.isnan(income[i]):
                if abs(balance[i-1] + income[i] - balance[i]) > error_tolerance:
                    invalid.append(i)
            elif not np.isnan(out[i]):
                if abs(balance[i-1] - out[i] != balance[i]) > error_tolerance:
                    invalid.append(i)
            else:
                invalid.append(i)
        print(invalid)
        print(self.all_df.loc[invalid]['交易日期'].values)
        invalid_dates = self.all_df.loc[invalid]['交易日期'].values     # 提取所有不正确余额对应的日期
        print('ratio of invalid balance: ', len(invalid_dates)/len(income))
        return invalid_dates

    def benford_check(self):
        income = self.all_df['流入金额'].values
        out = self.all_df['流出金额'].values
        # balance = self.all_df['交易后余额'].values
        income2, out2, balance2 = [], [], []
        # print(income)
        for i in range(len(income)):
            if not np.isnan(income[i]):
                income2.append(income[i])
            if not np.isnan(out[i]):
                out2.append(out[i])
            # if not np.isnan(balance[i]):
            #     balance2.append(balance[i])
        # print((balance2))
        all = income2 + out2
        print(md.benford(all))
        # print(md.benford(income2))
        # print(md.benford(out2))
        # print(md.benford(balance2))

def run(file_path):
    analyst = Analyzer(file_path)
    # analyst.balance_check(0)
    analyst.benford_check()

if __name__ == '__main__':
    start_time = time.time()
    run('output/output2.xlsx')
    print("--- %s seconds ---" % (time.time() - start_time))