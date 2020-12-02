# -- coding:UTF-8 --
import pandas as pd
import time
import sys, os
import Modules.mongodb as mongo
import Modules.public_module as md
import Modules.pymysql as mysql
import mydata as data
from sqlalchemy import create_engine


db = create_engine(
        'mysql+pymysql://bank_dev:072EeAb717e269bF@rm-uf6z3yjw3719s70sbuo.mysql.rds.aliyuncs.com:3306/bank_dev')


def get_df(table):
    df = pd.read_sql_table(table, db)
    return df


if __name__ == '__main__':
    start_time = time.time()
    get_df('liushui')

    end_time = time.time()
    print('======= Time taken: %f =======' %(end_time - start_time))
