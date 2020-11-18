import datetime
import traceback
import os
import numpy as np
import hashlib
import requests
import pandas as pd
import json


def to_json_array(df):
    try:
        df2 = df.fillna('').copy()
    except:
        df2 = df.copy()
    res = df2.T.to_dict()
    res2 = []
    for x in res.keys():
        res2.append(res[x])
    return res2


def timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


def divide(num1, num2, n=None):
    if num2 == 0:
        return np.nan
    else:
        if not n == None:
            return round(num1 / num2, n)
        else:
            return num1 / num2


def save_errlog(apiname, service_name):
    log = ['\n' + timestamp() + '\n']
    log.append(apiname + '\n')
    server_file = os.getcwd() + '/log_err/errlog_%s.txt' % (service_name)

    try:
        with open(server_file, 'a+') as f:
            f.writelines(log)
        traceback.print_exc(file=open(server_file, 'a+'))
    except:
        pass


def get_all_filename(path):
    res = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if (('.DS_Store' in file) == False) & (('__MACOS' in root) == False):
                res.append(os.path.join(root, file))
    return res


def get_new_col_lis(dic, df, col_key, default, default_col=''):
    if type(col_key) == list:
        lis = col_key
    else:
        lis = df[col_key].tolist()

    if default_col:
        lis2 = df[default_col].tolist()
    else:
        lis2 = []

    res = []

    if (default == 'original') & (len(lis2) > 0):
        for x, default2 in zip(lis, lis2):
            try:
                res.append(dic[x])
            except:
                try:
                    res.append(dic[str(x)])
                except:
                    try:
                        res.append(dic[int(x)])
                    except:
                        res.append(default2)
    else:
        for x in lis:
            try:
                res.append(dic[x])
            except:
                try:
                    res.append(dic[str(x)])
                except:
                    try:
                        res.append(dic[int(x)])
                    except:
                        res.append(default)

    return res


def get_md5(string):
    md5 = hashlib.md5(string.encode()).hexdigest().upper()
    return md5


def get_item_table(code):
    code1 = code[:1]
    table = {'1': 'financial_balance_sheet',
             '2': 'financial_balance_sheet',
             '6': 'financial_income_statement',
             '7': 'financial_cash_flow_statement',
             '8': 'financial_operation',
             '9': 'financial_operation'}[code1]
    return table


def check_keys(data, keys):
    lost_keys = []
    for x in keys:
        if not x in data:
            lost_keys.append(x)
    return lost_keys


def get_current_year():
    return int(datetime.datetime.now().strftime('%Y'))


def get_current_mon():
    return int(datetime.datetime.now().strftime('%m'))


def get_current_date():
    return datetime.datetime.now().strftime('%Y-%m-%d')


def get_ltm_period_list():
    lis = []
    lis2 = []
    p = pd.Period(datetime.datetime.now().strftime('%Y-%m'), 'M') - 1
    for i in range(12):
        pp = p - i
        lis.append([pp.year, pp.month])
        lis2.append(pp.strftime('%Y-%m'))
    return lis, lis2


def lower_columns(df):
    cols = []
    for x in df.columns:
        if isinstance(x, str):
            cols.append(x.lower())
        else:
            cols.append(x)
    df.columns = cols


def api(ip, apiid, params):
    url = 'http://%s/service-postInvestment/R%s' % (ip, apiid)  # dev
    requests.post(url, data=params)


def max_continue_count(lis, element):
    cont_lis = []
    max_cont_cnt = 0
    for x in lis:
        if x == element:
            cont_lis.append(x)
        else:
            max_cont_cnt = max(max_cont_cnt, len(cont_lis))
            cont_lis = []
    max_cont_cnt = max(max_cont_cnt, len(cont_lis))
    return max_cont_cnt


def get_lost_keys(data, keys):
    lost_keys = []
    for k in keys:
        if k not in data:
            lost_keys.append(k)
    return lost_keys


def get_scene_id_list(group_id, db):
    df = pd.read_sql("select * from bd_fm_dict where group_id=%d" % group_id, db)
    if df.empty:
        df = pd.read_sql("select * from bd_fm_dict where group_id=0", db)

    scene_id_list = list(set(df.scene_id.tolist()))
    return scene_id_list


def get_partition_one(df, key_col, order_col, asc1=True, asc2=False):
    # order_col,key_col排序后, 对key_col取第一个, 结果key_col不重复
    df.sort_values(by=[key_col, order_col], inplace=True, ascending=[asc1, asc2])
    uni_index_list = []
    last_key = None
    for x, y in zip(df[key_col], df.index):
        if last_key == x:
            continue
        else:
            uni_index_list.append(y)
            last_key = x
    df = df[df.index.isin(uni_index_list)]
    return df


def sql_where_in(where_lis):
    if isinstance(where_lis, pd.core.series.Series):
        where_lis = where_lis.tolist()
    if where_lis:
        txt = '('
        for x in where_lis:
            if type(x) == str:
                txt = txt + '\'' + x + '\','
            else:
                x = str(x)
                txt = txt + x + ','
        txt = txt[:-1] + ')'
    else:
        txt = ''
    return txt


def get_df_dict(df, col1, col2):
    return dict(zip(df[col1], df[col2]))


def get_df_rows_uuid(df):
    res = []
    for x in df.index:
        string = str(df.loc[x].to_dict())
        res.append(hashlib.md5(string.encode()).hexdigest())
    return res


def get_excel_date(integer):
    date = pd.Timestamp('1900-01-01') + pd.Timedelta(days=integer - 2)
    res = date.strftime('%Y年%m月')
    return res


def get_diff_day(day_before, day_after):
    d1 = datetime.datetime.strptime(day_before, '%Y-%m-%d')
    d2 = datetime.datetime.strptime(day_after, '%Y-%m-%d')
    return (d2 - d1).days


def get_period(f, t):  # 获取周期
    gap = int(t) - int(f)
    if gap == 0:
        period = 'M'
    elif gap == 2:
        period = 'Q'
    elif gap == 11:
        period = 'Y'
    else:
        period = 'YTD'
    return period


def to_numeric(lis):
    rs = []
    for x in lis:
        try:
            rs.append(float(x))
        except:
            rs.append(np.nan)
    return rs


def read_sql(field_lis, table, db, where_lis=None):
    # where_lis 类型 list
    # where_lis = ["entity_code='wind6_18'",'version=0']
    if where_lis == None:
        wheres = ''
    else:
        wheres = 'where %s' % ' and '.join(where_lis)
    df = pd.read_sql("select %s from %s %s" % (','.join(field_lis), table, wheres), db)
    return df


def return_df(df):
    rs = json.loads(df.fillna('').to_json(orient='records'))
    return rs


def xirr(cashflows, guess=0.1):
    from scipy import optimize

    try:
        if isinstance(cashflows, pd.core.frame.DataFrame):
            tmp = []
            for x, y in zip(cashflows.date, cashflows.amt):
                tmp.append((x, y))
            cashflows = tmp
    except:
        pass

    # 样例数据 [('2017-12-31', -200), ('2025-12-31', 1025.15625)]
    # 函数
    def xnpv(rate, cashflows):
        return sum(
            [cf / (1 + rate) ** ((datetime.datetime.strptime(t, '%Y-%m-%d') - datetime.datetime.strptime(cashflows[0][0], '%Y-%m-%d')).days / 365.0) for (t, cf) in cashflows])

    try:
        return round(optimize.newton(lambda r: xnpv(r, cashflows), guess), 4)
    except Exception as e:
        return np.nan


def get_value_or_default(dic, key, default):
    try:
        res = dic[key]
        if (res == '') or (res == 'null'):
            res = default
    except:
        res = default
    return res
