from sqlalchemy import create_engine

def db():
    db = create_engine('mysql+pymysql://bank_dev:072EeAb717e269bF@rm-uf6z3yjw3719s70sbuo.mysql.rds.aliyuncs.com:3306/bank_dev')
    return db



