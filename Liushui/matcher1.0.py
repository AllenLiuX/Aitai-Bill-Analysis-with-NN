# -- coding:UTF-8 --
import re
import pandas as pd
import time
import sys, os
import hashlib
import re
import Modules.mongodb as mongo
import Modules.public_module as md
import Modules.pymysql as mysql
from sqlalchemy import create_engine


# def clear_company_file(path, name):
#     mongo.delete_datas({'path': path}, name, 'mapping')

path = 'data/亿控2019年银行日记账.xls'


class Matcher:
    def __init__(self, file_path, sheet, output_path, user_name):
        # dataframes
        self.raw_df = pd.read_excel(file_path, sheet_name=sheet)
        self.target_df = None
        self.generated_df = None

        self.sheet_name = sheet
        self.user_name = user_name
        self.file_path = file_path
        self.output_path = output_path
        self.title = file_path.split('/')[-1]
        self.self_name = ''
        self.self_account = ''
        self.self_bank = ''
        self.start_date = ''
        self.end_date = ''
        self.transaction_num = 0
        self.currency = 'CNY'
        self.init_balance = 0
        self.gen_date = ''

        self.option_list = []

        # rules variables
        self.base_rules_summary = None
        self.base_rules = None
        self.user_rules = {}
        self.necessary_info = {}
        self.necessary_items = ['self_name', 'self_account', 'self_bank', 'currency', 'start_date', 'end_date']

        # mapping variables
        # self.matched_mapping = {}
        self.reversed_mapping = {}
        # self.option_unmatched = []
        self.target_unmatched = []
        self.name_mapping = {}


    def info_extractor(self):
        row_num_found = False
        row_num = 0
        if '银行' in self.sheet_name:
            self.self_bank = self.sheet_name
        # 从标题提取日期
        if not self.start_date or not self.end_date:
            res = re.findall(r'(20[12]\d)(\d*)-?(\d*)', self.title)[0]
            print(res)
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
            print(res)
        keywords_dict = {
                    'header_key': ['摘要', '交易类型', '交易时间', '日期', '备注','交易日期','对方账号'],
                    'self_bank': ['本方银行'],
                    'self_name': ['公司名称'],
                    'self_account': ['银行帐号', '银行账号'],
                    'start_date': ['查询开始日期'],
                    'end_date': ['查询结束日期'],
                    'init_balance': ['对帐单期初余额'],
                    'gen_date': ['生成日期'],
                    'currency': ['账户币种'],
        }
        for index in self.raw_df.index:     # 逐行看关键词是否存在
            # 看是否本来就匹配
            cols = self.raw_df.columns.ravel().tolist()
            for i in cols:
                if i in keywords_dict['header_key']:
                    row_num = 0
                    row_num_found = True
                    break
            if row_num_found:
                break
            for i in range(len(self.raw_df.loc[index].values)):
                #需要先找表头
                cell = self.raw_df.loc[index].values[i]
                if cell in keywords_dict['header_key']:       # 通过关键词寻找表头位置
                    row_num = index + 1
                    row_num_found = True
                    break

                for key in keywords_dict:   # 获取表头前统计信息
                    if (self.raw_df.loc[index].values[i] in keywords_dict[key]):
                        exec('self.{} = self.raw_df.loc[index].values[i + 1]'.format(key))      # i+1为被匹配信息右边一项
        if row_num_found:
            self.target_df = pd.read_excel(self.file_path, header=row_num)      # 重新建立dataframe
            self.option_list = self.target_df.columns.ravel().tolist()   #表头list
        else:
            print('titles not found!')
            # exit(1)
            return False
        return True

    def rule_setup(self):       # 初始化base_rule
        mongo.delete_col('base_rule', 'mapping')    # 每次删掉原有collection
        target_headers = ['交易日期', '交易时间', '本方名称', '本方账号', '本方银行', '对方名称',
                          '对方账号', '交易类型', '摘要', '流入金额', '流出金额', '交易后余额', '系统分类']
        target_summary = ['开始日期', '结束日期', '货币种类', '流水条数', '流入总额', '流出总额']
        mongo.insert_datas([{
            'type': 'rule_summary',
            'target_headers': target_headers,
            'target_summary': target_summary}], 'base_rule', 'mapping')
        mapping_rules = {       # 可以多对一，在后面匹配上后reverse便形成一对一，不冲突
            'type': 'base_rule',
            '交易日': '交易日期',
            '交易时间': '交易时间',
            '收/付方名称': '对方名称',
            '收/付方帐号': '对方账号',
            '交易类型': '交易类型',
            '摘要': '摘要',
            '备注': '摘要',
            '贷方金额': '流入金额',
            '借方金额': '流出金额',
            '余额': '交易后余额',
            '收取金额': '流入金额',
            '汇入金额': '流入金额',
            '汇出金额': '流出金额',
            '支出金额': '流出金额',
            '账户余额': '交易后余额',
            '对方户名': '对方名称',
            '对方账号': '对方账号',
            # '日期': '交易日期',
            # '交易类型': '系统分类',
        }
        mongo.insert_data(mapping_rules, 'base_rule', 'mapping')

    def mapping(self):
        # get base rule and rule summary from mongodb
        self.base_rules_summary = mongo.show_datas('base_rule', {'type': 'rule_summary'}, 'mapping')[0]
        self.base_rules = mongo.show_datas('base_rule', {'type': 'base_rule'}, 'mapping')[0]
        try:
            self.user_rules = mongo.show_datas('user_rule', {'type': 'user_rule', 'name': self.user_name}, 'mapping')[0]
            # self.base_rules.update(self.user_rules)         # 合并user_rules 进base_rule!
        except:
            self.user_rules["type"] = "user_rule"
            self.user_rules['name'] = self.user_name
            # print('no user rules yet.')
        try:
            self.necessary_info = mongo.show_datas('necessary', {'type': 'necessary', 'path': self.output_path}, 'mapping')[0]
        except:
            self.necessary_info = {
                'type': 'necessary',
                'path': self.output_path,
            }
        self.target_unmatched = self.base_rules_summary['target_headers'].copy()    # 需要.copy，防止总的headers list被修改
        self.necessary_unmatched = self.necessary_items.copy()
        # self.option_unmatched = list(self.option_list).copy()
        # self.option_unmatched.append('none')        # 用作空选项
        self.option_list.append('none')
        for key in self.option_list:
            if key in self.base_rules:     # 如果在baserule里已找到匹配项
                val = self.base_rules[key]
                # self.matched_mapping[item] = self.base_rules[item]
                self.reversed_mapping[val] = key
                self.target_unmatched.remove(val)
                # self.option_unmatched.remove(item)            # 可多选？去不去掉呢？？
        # 去掉input excel中随录信息包含值
        if self.self_name:
            self.target_unmatched.remove('本方名称')
            # self.necessary_unmatched.remove('self_name')
            # necessary['self_name'] = self.self_name
        if self.self_account:
            self.target_unmatched.remove('本方账号')
            # self.necessary_unmatched.remove('self_account')
            # necessary['self_account'] = self.self_account

        # 三步，库数据更新表，表数据更新库，找到空项
        # TODO 库里的necc，把表数据更新
        for key, val in self.necessary_info.items():
            if key not in ['type', 'path', '_id'] and val:
                exec('self.{} = "{}"'.format(key, val))
                self.necessary_unmatched.remove(key)

        # TODO 表数据更新库。去除表里包含的necessary
        # neccs = [self.self_name, self.self_account, self.self_bank, self.currency, self.start_date, self.end_date]
        # for i in range(len(neccs)):
        #     if neccs[i]:
        #         self.necessary_unmatched.remove(self.necessary_items[i])
        #         self.necessary_info[self.necessary_items[i]] = neccs[i]

        for i in self.necessary_unmatched:
            # if exec('temp = "self.{}"'.format(i)):
                # exec('self.necessary_unmatched.remove("{}")'.format(i))     # 注意，在里面如果要变量变str，需要加""
            exec('self.necessary_info["{}"] = self.{}'.format(i, i))

        #  TODO 根据库数据找到未匹配数据
        for i, val in self.necessary_info.items():
            if i in self.necessary_unmatched and val:
                self.necessary_unmatched.remove(i)
        print(self.necessary_info, self.necessary_unmatched)
        mongo.delete_datas({'type': 'necessary', 'path': self.output_path}, 'necessary', 'mapping')
        mongo.insert_data(self.necessary_info, 'necessary', 'mapping')


        # 生成反向mapping
        # for key, val in self.matched_mapping.items():  # 如果有多个none怎么办呢？:此时还无none, 所以需要先reverse，再加none
        #     self.reversed_mapping[val] = key
        self.reversed_mapping.update(self.user_rules)  # 合并user_rules 进base_rule!
        target_unmatched = []
        for i in self.target_unmatched:    # 一个个处理还没有匹配上的target选项
            # cur_tar = self.target_unmatched[0]
            if i not in self.reversed_mapping:        # user_rule被加进reversemap了，但target_unmatched并没有被update
                target_unmatched.append(i)
        self.target_unmatched = target_unmatched
        # return [self.target_unmatched, self.option_unmatched]
        return [self.target_unmatched, self.option_list, self.necessary_unmatched]

    def update_rule(self, query):       # query should be in the form of {'target': 'option'}
        for key, selected in query.items():
            # selected = query[key]
            # 1.更新option_unmatched
            # if selected not in self.option_unmatched:
            if selected not in self.option_list:
                print('错误！不存在此选项')
                return False

            # 2. 分情况更新target_unmatched和user_rule
            if key in self.target_unmatched:  # 还没被match的
                self.target_unmatched.remove(key)
            self.user_rules[key] = selected
            # mongo.delete_col('user_rule', 'mapping')  # 每次删掉原有collection
            mongo.delete_datas({'name': self.user_name}, 'user_rule', 'mapping')
            mongo.insert_data(self.user_rules, 'user_rule', 'mapping')

            # 3. 更新reversed_mapping 为之后生成excel作准备
            self.reversed_mapping[key] = selected
            # if selected != 'none':  # none 不去掉，因为还可能被选择
            #     self.option_unmatched.remove(selected)
        return True

    def clear_user_rule(self):
        mongo.delete_datas({'name': self.user_name}, 'user_rule', 'mapping')
        # mongo.delete_col('user_rule', 'mapping')
        
    def manual_mapping(self):
        while self.target_unmatched:    # 一个个处理还没有匹配上的target选项
            cur_tar = self.target_unmatched[0]
            # print(cur_tar)
            if cur_tar in self.reversed_mapping:        # user_rule被加进reversemap了，但target_unmatched并没有被update
                self.target_unmatched.remove(cur_tar)
                continue
            print('Options: ')
            # for i in range(0, len(self.option_unmatched), 4):   # 每四个换一行显示
            #     print(self.option_unmatched[i:i + 4])
            for i in range(0, len(self.option_list), 4):   # 每四个换一行显示
                print(self.option_list[i:i + 4])
            selected = input('与"{}"对应的是：'.format(cur_tar))
            self.update_rule({cur_tar: selected})

        while self.necessary_unmatched:
            cur_tar = self.necessary_unmatched[0]
            val = input('{} = '.format(cur_tar))
            add_stats({cur_tar: val}, self.output_path)
            self.necessary_unmatched.remove(cur_tar)

    def database_input(self):
        self.name_mapping = {  # 之后可以考虑用头四个字转拼音来生成collection名字
            '上海爱钛技术咨询有限公司': 'aitai',
            '宜昌华昊新材料科技有限公司': 'huahao',
            '浙江亿控自动化设备有限公司': 'yikong',
            '爱钛': 'aitai',
            '华昊': 'huahao',
            '亿控': 'yikong',
            '同普': 'tongpu',
        }
        # 从标题提取name
        if not self.self_name:
            for name in self.name_mapping:
                if name in self.title:
                    self.self_name = name

        if self.self_name in self.name_mapping:
            comp_id = self.name_mapping[self.self_name]
        elif not self.self_name:
            comp_id = 'temp'
        else:
            comp_id = self.self_name
        print(comp_id)
        # clear_company_file(self.output_path, name_mapping[self.self_name])
        mongo.delete_datas({'path': self.output_path}, comp_id, 'mapping')
        print(self.raw_df)
        print(self.target_df)
        info = {
            'type': 'form',
            'path': self.output_path,
            'company_name': self.self_name,
            'dates': [self.start_date, self.end_date],
            'account': self.self_account,
            'currency': self.currency,
            'gen_date': self.gen_date,
            'transactions_num': self.target_df.shape[1]
        }
        # self.transaction_num = self.target_df.shape[1]
        # info['transctions_num'] = self.transaction_num

        mongo.insert_data(info, comp_id, 'mapping')

    def dataframe_generator(self):
        print(self.base_rules)
        print(self.reversed_mapping)
        self.generated_df = pd.DataFrame(columns=self.base_rules_summary['target_headers'])
        for row in self.target_df.index:
            insert_row = {
                '本方名称': self.self_name,
                '本方账号': self.self_account,
                '本方银行': self.self_bank,
            }
            for item in self.base_rules_summary['target_headers']:
                if item in ['本方名称', '本方账号', '本方银行']:
                    continue
                elif self.reversed_mapping[item] == 'none':
                    # mapped_item = ''
                    insert_row[item] = ''  # 注意！mapped_item不能为空。
                else:
                    mapped_item = self.reversed_mapping[item]
                    inserted_item = self.target_df.loc[row, mapped_item]         # 注意！mapped_item不能为空。
                    if item == '交易日期':
                        inserted_item = md.to_date(str(inserted_item))
                    insert_row[item] = inserted_item
            # print(insert_row)
            self.generated_df = self.generated_df.append(insert_row, ignore_index=True)     # 注意df得新赋值，而不是直接.append

        # print(self.generated_df)

    def separate_col(self):
        if self.reversed_mapping['流出金额'] == self.reversed_mapping['流入金额']:
            self.generated_df['流入金额'][self.generated_df['流入金额'] <= 0] = 0
            self.generated_df['流出金额'][self.generated_df['流出金额'] >= 0] = 0
            self.generated_df['流出金额'] = -self.generated_df['流出金额']
            self.generated_df['流入金额'].fillna(0, inplace=True)
            self.generated_df['流出金额'].fillna(0, inplace=True)

    def excel_generator(self):
        # column names to english
        self.english_mapping = {
            '交易日期': 'date',
            '交易时间': 'time',
            '本方名称': 'sender_name',
            '本方账号': 'sender_account',
            '本方银行': 'sender_bank',
            '对方名称': 'receiver_name',
            '对方账号': 'receiver_account',
            '交易类型': 'type',
            '摘要': 'abstract',
            '流入金额': 'received_amount',
            '流出金额': 'sent_amount',
            '交易后余额': 'balance',
            '系统分类': 'system_classification'
        }
        
        # self.generated_df.rename(columns=self.english_mapping, inplace=True)
        print(self.generated_df)
        # to excel
        writer = pd.ExcelWriter(self.output_path)
        self.generated_df.to_excel(writer, sheet_name='Sheet1')
        writer.save()
        print('DataFrame is written successfully to the Excel File.')

        # to mysql
        # table_name = self.name_mapping[self.self_name]+self.start_date+'-'+self.end_date

        # db = mysql.Database()
        # columns_name = []
        # for i in self.base_rules_summary['target_headers']:
        #     columns_name.append(self.english_mapping[i])
        # db.create('aitai3', columns_name)
        # for index in self.generated_df.index:
        #     # break
        #     vals = self.generated_df.loc[index].values.tolist()
        #     vals2 = [str(i) for i in vals]
        #     vals = ['nan' if i=='' else i for i in vals2]
        #     print(vals)
        #     db.insert('aitai3', vals)

        # engine = create_engine('mysql+pymysql://bank_dev:072EeAb717e269bF@rm-uf6z3yjw3719s70sbuo.mysql.rds.aliyuncs.com:3306/bank_dev?charset=utf8')
        #
        # self.generated_df.to_sql(table_name, engine, index=False)
        # print('DataFrame is written successfully to mysql')


def add_rules(query, user):
    user_rules = {}
    try:
        user_rules = mongo.show_datas('user_rule', {'type': 'user_rule', 'name': user}, 'mapping')[0]
    except:
        user_rules["type"] = "user_rules"
        user_rules['name'] = user
        # print('no user rules yet.')
    user_rules.update(query)
    # for key, val in query.items():
    #     user_rules[key] = val
    mongo.delete_datas({'name': user}, 'user_rule', 'mapping')  # 每次删掉原有collection
    mongo.insert_data(user_rules, 'user_rule', 'mapping')
    return 'success'


def add_stats(query, path):
    necc_info = {}
    try:
        necc_info = mongo.show_datas('necessary', {'type': 'necessary', 'path': path}, 'mapping')[0]
    except:
        necc_info["type"] = "necessary"
        necc_info['path'] = path
        # print('no user rules yet.')
    necc_info.update(query)
    # for key, val in query.items():
    #     user_rules[key] = val
    mongo.delete_datas({'type': 'necessary', 'path': path}, 'necessary', 'mapping')  # 每次删掉原有collection
    mongo.insert_data(necc_info, 'necessary', 'mapping')
    return 'success'


def store(file_path, output_path, user_name):
    matcher = Matcher(file_path, output_path, user_name)
    # matcher.clear_user_rule()
    if not matcher.info_extractor():
        return 'failed'
    matcher.rule_setup()
    remains = matcher.mapping()
    if remains[0]:      # target_unmatched is not empty
        return remains
    else:
        data_store(file_path, output_path, user_name)
    return 'success'


def data_store(file_path, output_path, user_name):
    matcher = Matcher(file_path, output_path, user_name)
    if not matcher.info_extractor():
        return 'failed'
    matcher.mapping()
    matcher.database_input()
    matcher.dataframe_generator()
    matcher.separate_col()
    matcher.excel_generator()


def run(file_path, sheet, output_path, user_name):
    matcher = Matcher(file_path, sheet, output_path, user_name)
    # matcher.clear_user_rule()
    if not matcher.info_extractor():
        return 'failed'
    matcher.rule_setup()
    matcher.mapping()
    matcher.manual_mapping()
    matcher.database_input()
    matcher.dataframe_generator()
    matcher.separate_col()
    matcher.excel_generator()
    return 'success'

def entry(file_path, output_path, user_name):
    sheets = pd.ExcelFile(file_path)
    result = []
    cache_tables = []
    for sheet in sheets.sheet_names:
        print('------ Processing sheet ' + sheet + ' ------')
        table = 'cache/'+sheet+'.xlsx'
        res = run(file_path, sheet, table, file_path)
        if res == 'failed':
            continue
        result.append(res)
        cache_tables.append(table)
    # 合并进同一张表
    final_df = pd.read_excel(cache_tables[0])
    for i in cache_tables[1:]:
        new_df = pd.read_excel(i)
        final_df = pd.concat([final_df, new_df], ignore_index=True)
    writer = pd.ExcelWriter(output_path)
    final_df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    print('DataFrame is written successfully to the Excel File.')
    return result



if __name__ == '__main__':
    start_time = time.time()
    # res = run('data/202001-03同普泰隆流水.xls', 'output/sample1.xlsx', 'vincent')
    # add_stats({'self_bank':'招行'}, 'output/sample3.xlsx')

    yikong = os.listdir('data/yikong')
    all_excels = []
    print(yikong)
    for file in yikong:
        if file[0] == '~':
            continue
        print('------ Processing file '+file+' ------')
        outpos = 'output/'+file+'.xlsx'
        entry('data/yikong/'+file, 'output/'+file+'.xlsx', 'yikong2')
        all_excels.append(outpos)
    final_df = pd.read_excel(all_excels[0])
    for i in all_excels[1:]:
        new_df = pd.read_excel(i)
        final_df = pd.concat([final_df, new_df], ignore_index=True)
    writer = pd.ExcelWriter('output/yikongall.xlsx')
    final_df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    print('======= Final DataFrame is written successfully to the Excel File.')


    # res = entry(path, 'output/sample3.xlsx', 'yikong')

    # res = run(path, 'output/sample3.xlsx', 'aitai')
    # res = add_rules({'交易时间': 'none'}, 'vincent')
    # print(res)
    # run('data/sample2.xls', 'output/sample2.xlsx', 'vincent')
    print("--- %s seconds ---" % (time.time() - start_time))