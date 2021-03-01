# import sqlite3
import pymysql



class Database():
    def __init__(self):
        # self.db = sqlite3.connect(db)
        self.db = pymysql.connect(host='rm-uf6z3yjw3719s70sbuo.mysql.rds.aliyuncs.com', user='bank_dev', password='(fill this blank)',
                             db='bank_dev')
        self.cursor = self.db.cursor()

    def drop_table(self, table):
        print(table, 'table is deleted.')
        sql = 'DROP TABLE ' + table
        self.cursor.execute(sql)
        self.db.commit()

    def show_table(self, table):
        sql = 'select * from ' + table
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        print(res)
        return res

    def close_db(self):
        self.db.close()

    def create(self, table, cols):
        self.cursor.execute("show tables")
        table_lists = self.cursor.fetchall()
        # print(table_lists)
        if len(table_lists)>0:
            print(table_lists)
            if (table.lower(),) in table_lists:
                print('table already exist. skip create.')
                return
        sql = 'CREATE TABLE ' + table + ' ('
        for c in cols:
            sql += c + ', '
        sql = sql[:-2]
        sql += ')'
        print(sql)
        self.cursor.execute(sql)
        self.db.commit()

    def insert(self, table, vals, cols=[]):
        sql = 'INSERT INTO '+table
        if cols:
            sql += '('
            for c in cols:
                sql += c+', '
            sql = sql[:-1]
            sql += ')'
        sql += ' VALUES ('
        for v in vals:
            sql += v+', '
        sql = sql[:-2]
        sql += ')'
        print(sql)
        self.cursor.execute(sql)
        self.db.commit()

if __name__ == '__main__':
    db = Database()
    # db.drop_table('REPORTS')
    list = ['date text', 'time text', 'sender_name text',
            'sender_account text', 'sender_bank text', 'receiver_name text',
            'receiver_account text', 'type text', 'abstract text',
            'received_amount text', 'sent_amount text', 'balance text',
            'system_classification text']
    db.create('AITAI2', list)
    db.insert('AITAI', ['20201212', '140000'])
    db.create('AITAI2020', ['BEGIN_DATE TEXT', 'END_DATE TEXT'])
    db.insert('REPORT2', ['20000101', '20000103'])
    res = db.show_table('reports')
    db.close_db()
