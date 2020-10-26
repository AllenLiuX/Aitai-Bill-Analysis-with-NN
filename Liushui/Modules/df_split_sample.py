import pandas as pd

path = '../data/亿控2019年银行日记账.xls'
df = pd.read_excel(path, header=1)
df.rename(columns={'收入/支出（￥）': 'amt'}, inplace=True)

df_p = df.query("amt>=0").copy()  # 正金额表
df_n = df.query("amt<0").copy()  # 负金额表

df_p.rename(columns={'amt': 'in'}, inplace=True)
df_n.rename(columns={'amt': 'out'}, inplace=True)

df_res = pd.concat([df_p, df_n],axis=0)
df_res['in'].fillna(0, inplace=True)
df_res['out'].fillna(0, inplace=True)
df_res['out'] = -df_res['out']




print(df)