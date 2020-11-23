# -- coding:UTF-8 --
import re
import pandas as pd
import json
import time
import sys, os
import re
import Modules.mongodb as mongo
import Modules.public_module as md
import Modules.pymysql as mysql
import mydata as data
from sqlalchemy import create_engine


class Matcher:
    def __init__(self, company, file_path, table, rule_name, batch_id):
        # dataframes
        self.raw_df = pd.read_excel(file_path, sheet_name=table)
        self.target_df = None
        self.generated_df = None

        self.company = company
        self.table = table
        self.file_path = file_path
        self.batch_id = batch_id
        self.title = file_path.split('/')[-1]
        self.self_name = ''
        self.self_account = ''
        self.self_bank = ''
        self.start_date = ''
        self.end_date = ''
        self.transaction_num = ''
        self.currency = ''
        self.init_balance = ''
        self.gen_date = ''

        self.option_list = []

        # rules variables
        self.base_rules = data.mapping_rules
        self.target_headers = data.target_headers
        self.rule_name = rule_name
        self.user_rules = {}
        self.info = {}
        self.necessary_items = ['self_name', 'self_account', 'self_bank', 'currency', 'start_date', 'end_date']

        # mapping variables
        self.reversed_mapping = {}
        self.target_unmatched = []
        self.name_mapping = {}

    def info_extractor(self):
        # 匹配表头行 并提取表格信息
        row_num_found = False
        row_num = 0
        keywords_dict = data.keywords_dict
        for index in self.raw_df.index:  # 逐行看关键词是否存在
            # 看是否第0行本来就匹配
            cols = self.raw_df.columns.ravel().tolist()
            for i in cols:
                if i in keywords_dict['header_key']:
                    row_num = 0
                    row_num_found = True
                    break
            if row_num_found:
                break

            for i in range(self.raw_df.shape[1]):
                # 需要先找表头
                cell = self.raw_df.loc[index].values[i]
                if cell in keywords_dict['header_key']:  # 通过关键词寻找表头位置
                    row_num = index + 1
                    row_num_found = True
                    break

                for key in keywords_dict:  # 获取表头前统计信息
                    if (cell in keywords_dict[key]):
                        print(cell)
                        exec('self.{} = self.raw_df.loc[index].values[i + 1]'.format(key))  # i+1为被匹配信息右边一项
                        break

        if row_num_found:
            self.target_df = pd.read_excel(self.file_path, header=row_num)  # 重新建立dataframe
            self.option_list = self.target_df.columns.ravel().tolist()  # 表头list
            self.transaction_num = self.target_df.shape[0]
        else:
            print('titles not found!')
            return False
        print(self.target_df)

        # 从标题提取name
        self.name_mapping = data.name_mapping
        if not self.self_name:
            for name in self.name_mapping:
                if name in self.title:
                    self.self_name = name

        # 从表名提取银行
        if '银行' in self.table:
            self.self_bank = self.table

        # 从第一格提取账号
        cell = self.raw_df.columns.ravel()[0]
        match = re.findall(r'(\d{16,19})', cell)
        if match:
            print('Found self account number: ', match[0])
            self.self_account = match[0]


        # 从标题提取日期
        if not self.start_date or not self.end_date:
            res = re.findall(r'(20[12]\d)(\d*)-?(\d*)', self.title)
            if res:
                res = res[0]
                if not res[1] and not res[2]:  # 只匹配到年份
                    self.start_date = res[0] + '0101'
                    self.end_date = res[0] + '1231'
                elif not res[2]:
                    self.start_date = res[0] + res[1] + '01'
                    self.end_date = res[0] + res[1] + '30'
                elif len(res[1]) == 2:
                    if len(res[2]) == 6:
                        self.start_date = res[0] + res[1] + '01'
                        self.end_date = res[2] + '30'
                    if len(res[2]) == 2:
                        self.start_date = res[0] + res[1] + '01'
                        self.end_date = res[0] + res[2] + '30'
                    if len(res[2]) == 1:
                        self.start_date = res[0] + res[1] + '01'
                        self.end_date = res[0] + '0' + res[2] + '30'


        # store as json
        df_json = self.target_df.to_json(orient='columns', force_ascii=False)
        df_data = {
            'company': self.company,
            'file': self.title,
            'table': self.table,
            'data': df_json
        }
        query = {'company': self.company, 'file': self.title, 'table': self.table, 'batchid': self.batch_id}
        if mongo.show_datas('unmapped_df', query, 'Cache'):
            # mongo.update_datas(query, {'$set': df_data}, 'unmapped_df', 'Cache')
            mongo.delete_datas(query, 'unmapped_df', 'Cache')
            mongo.insert_data(df_data, 'unmapped_df', 'Cache')
        else:
            mongo.insert_data(df_data, 'unmapped_df', 'Cache')

        # data2 = mongo.show_datas('unmapped_df', query, 'Cache')[0]
        # df2 = pd.read_json(data2['data'])
        # print(df2)
        return True

    def mapping(self, rule_name):
        try:
            self.user_rules = mongo.show_datas('user_rule', {'company': self.company, 'rule_name': rule_name}, 'Mapping')[0]
        except:
            self.user_rules = {
                'company': self.company,
                'rule_name': rule_name
            }
            # print('no user rules yet.')

        self.target_unmatched = self.target_headers.copy()

        # 根据base rule填充mapping
        self.option_list.append('none')
        for key in self.option_list:
            if key in self.base_rules:  # 如果在base rule里已找到匹配项
                val = self.base_rules[key]
                self.reversed_mapping[val] = key
                self.target_unmatched.remove(val)
        # 去掉input excel中随录信息包含值
        if self.self_name:
            self.target_unmatched.remove('本方名称')
        if self.self_account:
            self.target_unmatched.remove('本方账号')

        # 根据user rule填充mapping
        self.reversed_mapping.update(self.user_rules)  # 合并user_rules 进base_rule!
        target_unmatched = []
        for i in self.target_unmatched:  # 一个个处理还没有匹配上的target选项
            if i not in self.reversed_mapping:  # user_rule被加进reversemap了，但target_unmatched并没有被update
                target_unmatched.append(i)  # 不直接remove self的，因为for循环remove后index会过
        self.target_unmatched = target_unmatched
        print(self.target_unmatched, self.option_list, self.reversed_mapping)
        return [self.target_unmatched, self.option_list, self.reversed_mapping]

    def save_info(self):
        '''
            info 库里的先update表里的，因为方便修改库里的信息然后反映到表上
            不重合时互相update
        '''
        self.info = {
            # TODO 修改analyser里的dates, account写法
            # 'dates': [self.start_date, self.end_date],
            'company': self.company,
            'file': self.title,
            'table': self.table,
            'self_name': self.self_name,
            'self_account': self.self_account,
            'self_bank': self.self_bank,
            'currency': self.currency,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'gen_date': self.gen_date,
            'transactions_num': self.transaction_num,
            'init_balance': self.init_balance,
        }
        query = {'company': self.company, 'file': self.title, 'table': self.table}
        # 库数据更新表数据
        try:
            db_info = mongo.show_datas('sheet_info', query, 'Info')[0]
            for k, v in db_info.items():
                if k not in self.info or self.info[k] == '':    # 不更新已有的数据
                    self.info[k] = v
            if '_id' in self.info:
                del self.info['_id']
        except:
            pass

        # 表数据更新库
        if mongo.show_datas('sheet_info', query, 'Info'):
            mongo.update_datas(query, {'$set': self.info}, 'sheet_info', 'Info')
        else:
            mongo.insert_data(self.info, 'sheet_info', 'Info')

        # 根据库数据找到未匹配数据
        nec_unmatched = []
        for i in self.necessary_items:
            if i not in self.info or self.info[i] == '':
                nec_unmatched.append(i)
        self.necessary_unmatched = nec_unmatched

        return [self.necessary_unmatched, self.info]

    def update_rule(self, query):  # query should be in the form of {'target': 'option'}
        for key, selected in query.items():
            # 1.更新option_unmatched
            if selected not in self.option_list:
                print('错误！不存在此选项')
                return False

            # 2. 分情况更新target_unmatched和user_rule
            if key in self.target_unmatched:  # 还没被match的
                self.target_unmatched.remove(key)
            self.user_rules[key] = selected
            mongo.delete_datas({'name': self.user_name}, 'user_rule', 'mapping')
            mongo.insert_data(self.user_rules, 'user_rule', 'mapping')

            # 3. 更新reversed_mapping 为之后生成excel作准备
            self.reversed_mapping[key] = selected

        return True

    def manual_mapping(self):
        asked_template = False
        while self.target_unmatched:  # 一个个处理还没有匹配上的target选项
            # use rule template
            if not asked_template:
                templates = mongo.show_datas('user_rule', {'company': self.company}, 'Mapping')
                print('现有的规则模版为：')
                rule_name_all = []
                for i in templates:
                    del i['_id']
                    del i['company']
                    rule_name_all.append(i['rule_name'])
                    print(i)
                rule_name = input('使用规则模版：')
                if rule_name:
                    if rule_name not in rule_name_all:
                        print('无此模版。')
                        continue
                    self.mapping(rule_name)
                    asked_template = True
                    continue
                asked_template = True

            # write new rule
            cur_tar = self.target_unmatched[0]
            print('Options: ')
            for i in range(0, len(self.option_list), 4):  # 每四个换一行显示
                print(self.option_list[i:i + 4])
            selected = input('与"{}"对应的是：'.format(cur_tar))
            if selected == '':
                selected = 'none'

            if selected not in self.option_list:
                print('错误！不存在此选项')
                continue

            if cur_tar in self.target_unmatched:  # 还没被match的
                self.target_unmatched.remove(cur_tar)
            self.reversed_mapping[cur_tar] = selected
            add_rules({cur_tar: selected}, self.company, self.rule_name)

        while self.necessary_unmatched:
            cur_tar = self.necessary_unmatched[0]
            val = input('{} = '.format(cur_tar))
            add_stats({cur_tar: val}, self.company, self.title, self.table, self.batch_id)
            self.necessary_unmatched.remove(cur_tar)

    def dataframe_generator(self):
        print(self.reversed_mapping)
        self.generated_df = pd.DataFrame(columns=self.target_headers)

        for col in self.target_headers:
            if col not in ['本方名称', '本方账号', '本方银行']:
                mapped_col = self.reversed_mapping[col]
                if mapped_col not in ['none']:
                    self.generated_df[col] = self.target_df[mapped_col]
        dates = self.generated_df['交易日期'].astype(str).apply(md.to_date)
        times = self.generated_df['交易时间'].astype(str).apply(md.to_date)     # 现在还没有implement time conversion to str
        self.generated_df['交易日期'] = dates
        self.generated_df['交易时间'] = times
        self.generated_df['本方名称'].fillna(self.self_name, inplace=True)
        self.generated_df['本方账号'].fillna(self.self_account, inplace=True)
        self.generated_df['本方银行'].fillna(self.self_bank, inplace=True)
        print(self.generated_df)

    def separate_col(self):
        if self.reversed_mapping['流出金额'] == self.reversed_mapping['流入金额']:
            self.generated_df['流入金额'][self.generated_df['流入金额'] <= 0] = 0
            self.generated_df['流出金额'][self.generated_df['流出金额'] >= 0] = 0
            self.generated_df['流出金额'] = -self.generated_df['流出金额']
            self.generated_df['流入金额'].fillna(0, inplace=True)
            self.generated_df['流出金额'].fillna(0, inplace=True)

    def save_df(self):
        df_json = self.generated_df.to_json(orient='columns', force_ascii=False)
        df_data = {
            'company': self.company,
            'file': self.title,
            'table': self.table,
            'batch_id': self.batch_id,
            'data': df_json
        }
        query = {'company': self.company, 'file': self.title, 'table': self.table, 'batch_id': self.batch_id}
        if mongo.show_datas('mapped_df', query, 'Cache'):
            # mongo.update_datas(query, {'$set': df_data}, 'mapped_df', 'Cache')
            mongo.delete_datas(query, 'mapped_df', 'Cache')
            mongo.insert_data(df_data, 'mapped_df', 'Cache')
        else:
            mongo.insert_data(df_data, 'mapped_df', 'Cache')
            print('batch_id is ', self.batch_id)


def add_rules(request, company, rule_name):
    user_rules = {}
    try:
        user_rules = mongo.show_datas('user_rule', {'company':company, 'rule_name': rule_name}, 'Mapping')[0]
        user_rules.update(request)
        mongo.update_datas({'company':company, 'rule_name': rule_name}, {'$set': user_rules}, 'user_rule', 'Mapping')
    except:
        user_rules['company'] = company
        user_rules['rule_name'] = rule_name
        # print('no user rules yet.')
        user_rules.update(request)
        print(user_rules)
        mongo.insert_data(user_rules, 'user_rule', 'Mapping')
    return 'success'


def add_stats(request, company, file, table, batch_id):
    query = {'company': company, 'file': file, 'table': table, 'batch_id': batch_id}
    try:
        necc_info = mongo.show_datas('sheet_info', query, 'Info')[0]
        mongo.delete_datas(query, 'sheet_info', 'Info')
    except:
        necc_info = query
    necc_info.update(request)
    mongo.insert_data(necc_info, 'sheet_info', 'Info')
    print(necc_info)
    return 'success'


def process_table_api(company, file_path, table='Sheet1', rule_name='', batch_id='default', method='api'):
    matcher = Matcher(company, file_path, table, rule_name, batch_id=batch_id)
    if not matcher.info_extractor():
        return 'fail'
    map_res = matcher.mapping(rule_name)
    info_res = matcher.save_info()
    if method == 'api':
        if map_res[0] or info_res[0]:
            return map_res + info_res
    elif method == 'local':
        print(info_res)
        matcher.manual_mapping()
    else:
        return 'wrong parameter for method'
    matcher.dataframe_generator()
    matcher.separate_col()
    matcher.save_df()
    return 'success'


def process_file(company, file_path, batch_id, method='local'):
    tables = pd.ExcelFile(file_path)
    result = []
    for table in tables.sheet_names:
        print('------ Processing table ' + table + ' ------')
        rule_name = file_path.split('/')[-1]+'-'+table      # 目前暂时的rule_name命名方法！
        res = process_table_api(company, file_path, table, rule_name, batch_id=batch_id, method=method)
        if res == 'fail': # 没找到表头行
            continue
        result.append(res)
    print(result)
    return result


def process_dir(company, dir_path, batch_id):
    files = os.listdir(dir_path)
    print(files)
    result = []
    for file in files:
        if file[0] == '~':
            continue
        print('------ Processing file ' + file + ' ------')
        file_path = os.path.join(dir_path, file)
        res = process_file(company, file_path, batch_id=batch_id)
        result.append(res)
    return result


def output_excel(company, batch_id, file_output):
    datas = mongo.show_datas('mapped_df', {'company': company, 'batch_id': batch_id}, 'Cache')
    final_df = pd.read_json(datas[0]['data'])
    for i in range(1, len(datas)):
        cur_table = datas[i]['data']
        cur_df = pd.read_json(cur_table)
        final_df = pd.concat([final_df, cur_df], ignore_index=True)
    print(final_df)
    writer = pd.ExcelWriter(file_output)
    final_df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    print('DataFrame is written successfully to the Excel File.')


def upload_mysql(company, batch_id):
    datas = mongo.show_datas('mapped_df', {'company': company, 'batch_id': batch_id}, 'Cache')
    final_df = pd.read_json(datas[0]['data'])
    db = create_engine(
        'mysql+pymysql://bank_dev:072EeAb717e269bF@rm-uf6z3yjw3719s70sbuo.mysql.rds.aliyuncs.com:3306/bank_dev')
    for i in range(1, len(datas)):
        cur_table = datas[i]['data']
        cur_df = pd.read_json(cur_table)
        final_df = pd.concat([final_df, cur_df], ignore_index=True)
    final_df.rename(columns=data.english_mapping, inplace=True)
    df = final_df.iloc[:, 1:]
    df['batch_id'] = batch_id
    print(df)
    df.to_sql('liushui', db, index=False, if_exists='append')

if __name__ == '__main__':
    start_time = time.time()
    # res = process_table_api('aitai', 'data/sample1.xls', rule_name='test_rule2')
    # res = process_dir('yikong', 'data/yikong', batch_id='3')
    # print(res)
    # output_excel('yikong', '3', 'output/yikong1.xlsx')
    upload_mysql('yikong', '3')
    print("--- %s seconds ---" % (time.time() - start_time))