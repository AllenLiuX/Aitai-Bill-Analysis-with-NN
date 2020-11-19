import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import seaborn as sns

filePath = 'system type rules.xlsx'

process_path = '../output/yikongall2.xlsx'


def reverse_map(rules):
    rev_map = {}
    for key, val in rules.items():
        for v in val:
            rev_map[v] = key
    return rev_map

def get_rules(filePath):
    df = pd.read_excel(filePath, sheet_name=1, header=1)
    ins = list(range(0, 8)) + list(range(23, 28)) + list(range(32, 35))
    data_df = df.iloc[:, [2, 3]]
    types = data_df['系统分类'].values
    rules = {}
    in_or_out = {}
    print(data_df.dtypes)
    data_df['交易类型/摘要'] = data_df['交易类型/摘要'].astype(str)
    for i in data_df.index:
        key = data_df.loc[i].values[0]
        if i in ins:
            in_or_out[key] = 1
        else:
            in_or_out[key] = 0
        val = data_df.loc[i].values[1].split('/')
        rules[key] = val
    print(rules)
    print(in_or_out)

    in_map, out_map = {}, {}
    for key, val in rules.items():
        if in_or_out[key] == 1:
            for v in val:
                in_map[v] = key
        else:
            for v in val:
                out_map[v] = key

    return in_map, out_map


def process_file(process_path, in_map, out_map):
    df = pd.read_excel(process_path)
    stats = {}
    for i in df.index:
        row = df.loc[i].values
        receiver = row[6]
        abstract = row[9]
        inval = row[10]
        outval = row[11]
        try:
            if float(inval) > 0:
                for key in in_map.keys():
                    if key in str(abstract) or key in str(receiver):
                        # print(in_map[key])
                        df['系统分类'].loc[i] = in_map[key]
                        if in_map[key] in stats:
                            stats[in_map[key]] += 1
                        else:
                            stats[in_map[key]] = 1
        except Exception as e:
            print(e)
        try:
            if float(outval) > 0:
                for key in out_map.keys():
                    if key in str(abstract)  or key in str(receiver):
                        # print(out_map[key])
                        df['系统分类'].loc[i] = out_map[key]
                        if out_map[key] in stats:
                            stats[out_map[key]] += 1
                        else:
                            stats[out_map[key]] = 1
        except Exception as e:
            print(e)
    writer = pd.ExcelWriter('output.xlsx')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    print('DataFrame is written successfully to the Excel File.')

    # x轴中文乱码问题
    plt.rcParams['font.family'] = ['Arial Unicode MS']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    sns.set_style('whitegrid', {'font.sans-serif': ['Arial Unicode MS', 'Arial']})
    
    # 显示不完全问题
    plt.figure(figsize=(15, 8))
    plt.tick_params(axis='x', labelsize=8)  # 设置x轴标签大小
    plt.xticks(rotation=-25)
    bar_plot = sns.barplot(x=list(stats.keys()), y=list(stats.values()), palette='muted')
    plt.show()

if __name__ == '__main__':
    start_time = time.time()
    in_map, out_map = get_rules(filePath)
    # print(out_map[''])
    try:
        # del in_map['']
        # del in_map[' ']
        del in_map['nan']
        del out_map['']
        # del out_map[' ']
        del out_map['nan']
    except Exception as e:
        print(e)
    print(out_map.keys())
    # print(out_map[''])
    # print(in_map.keys())
    process_file(process_path, in_map, out_map)
    print("--- %s seconds ---" % (time.time() - start_time))
