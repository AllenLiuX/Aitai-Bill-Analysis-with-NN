import datetime
import re
import math
import numpy as np
import pandas as pd
from operator import itemgetter
# import pdfplumber
# import camelot
# import tabula

def to_date(str):
    if len(str) > 8:
        str = str[:4] + str[5:7] + str[8:10]
    # date = datetime.datetime.strptime(str, '%Y%m%d').date()
    return str
    # return date


# def pdf2df(path):
#     # tables = tabula.read_pdf(path, encoding='gbk', pages='all')
#     # # t = tables[0].df
#     # print(tables)
#     with pdfplumber.open(path) as pdf:
#          # for table in pdf.pages[2].extract_tables():
#          #     tb = pd.DataFrame(table[1:], columns=table[0], index=None)
#          #     print(tb)
#         # for t in table:
#         #     # 得到的table是嵌套list类型，转化成DataFrame更加方便查看和分析
#         #     df = pd.DataFrame(t[1:], columns=t[0])
#         #     print(df)
#             table = pdf.pages[2].extract_tables()
#             print('result')
#             print(table)
#     # return table


def correlation_coefficient(a, b):
    a_avg = sum(a) / len(a)
    b_avg = sum(b) / len(b)

    # 计算分子，协方差————按照协方差公式，本来要除以n的，由于在相关系数中上下同时约去了n，于是可以不除以n
    cov_ab = sum([(x - a_avg) * (y - b_avg) for x, y in zip(a, b)])

    # 计算分母，方差乘积————方差本来也要除以n，在相关系数中上下同时约去了n，于是可以不除以n
    sq = math.sqrt(sum([(x - a_avg) ** 2 for x in a]) * sum([(x - b_avg) ** 2 for x in b]))

    corr_factor = cov_ab / sq
    return corr_factor


def benford(nums):
    dict = {}
    for i in range(1,10):
        dict[str(i)] = 0
    for i in nums:
        t = str(i)[0]       #首字母
        if t != '0':
            dict[t] += 1
    # print(dict)
    real = []   # array of real prob
    for key, val in dict.items():
        # dict[key] = val/len(nums)
        real += [val/len(nums)]
    expect = []
    for d in range(1, 10):
        expect += [math.log10(1+1/d)]
    cor = correlation_coefficient(real, expect)
    # cor = np.corrcoef(real, expect)[0][1]
    return [cor, real]


def merge_dates(dates):
    D = sorted(dates, key=itemgetter(0))
    res = []
    if len(D) <= 1:
        return D
    start = D[0][0]
    end = D[0][1]
    for i in D[1:]:
        if i[0] <= end+1:       # +1因为两端相差1天也是连续
            end = max(i[1], end)
            continue
        else:
            res.append([start, end])
            start = i[0]
            end = i[1]
    res.append([start, end])
    return res

if __name__ == '__main__':
    to_date('20200101')
    pdf2df('../data/202001-202003泰隆流水.pdf')
    nums = [123, 125, 129, 235, 45, 43363, 134, 4346, 643, 3, 356, 8, 6, 5, 8, 97, 5]
    dates = [[1,5], [2, 4], [1, 3], [10,11], [8, 9]]
    # print(merge_dates(dates))
    # print(benford(nums))

