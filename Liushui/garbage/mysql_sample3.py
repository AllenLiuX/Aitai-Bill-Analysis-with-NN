import pandas as pd
import re
from sqlalchemy import create_engine

db = create_engine('mysql+pymysql://bank_dev:072EeAb717e269bF@rm-uf6z3yjw3719s70sbuo.mysql.rds.aliyuncs.com:3306/bank_dev')

file = 'output/yikong1.xlsx'
# df = pd.read_sql("select * from aitai2",db)
yk = '91330782091672637Q'  # 浙江亿控自动化设备有限公司
tp = '91310110557496664Y'  # 上海同普电力技术有限公司

cols_mysql = ['shxydm', 'date', 'time', 'sender_name', 'sender_account',
       'sender_bank', 'receiver_name', 'receiver_account', 'type', 'abstract',
       'received_amount', 'sent_amount', 'balance', 'system_classification']
df = pd.read_excel(file)
df['shxydm'] = yk
cols_cn = ['shxydm','交易日期', '交易时间', '本方名称', '本方账号', '本方银行', '对方名称', '对方账号',
       '交易类型', '摘要', '流入金额', '流出金额', '交易后余额', '系统分类'] # 与cols_mysql匹配的中文列名
df = df[cols_cn].copy()
df.columns = cols_mysql
df.sender_account = [str(int(x)) if len(re.findall('[0-9]',str(x))) == len(str(x)) else x for x in df.sender_account]
df.receiver_account = [str(int(x)) if len(re.findall('[0-9]',str(x))) == len(str(x)) else x for x in df.receiver_account]
print(df.dtypes)
df.to_sql('aitai6',db,index=False,if_exists='append')






