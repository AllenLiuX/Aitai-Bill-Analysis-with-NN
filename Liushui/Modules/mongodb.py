# -- coding:UTF-8 --
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")


def insert_data(data, collection, db='articles'):
    mydb = myclient[db]  # use articles as default database
    mycol = mydb[collection]
    x = mycol.insert_one(data)
    # print(x.inserted_id)


def insert_datas(data_list, collection, db='articles'):
    mydb = myclient[db]  # use articles as default database
    mycol = mydb[collection]  # collection
    x = mycol.insert_many(data_list)
    # print(x.inserted_ids)


def show_datas(collection, query={}, db='articles', sortby='_id', seq=True):
    mydb = myclient[db]
    mycol = mydb[collection]
    result = []
    if seq:
        objects = mycol.find(query).sort(sortby)
    else:
        objects = mycol.find(query).sort(sortby, -1)
    for x in objects:
        result.append(x)
    return result


def delete_datas(query, collection, db='articles'):
    mydb = myclient[db]
    mycol = mydb[collection]
    x = mycol.delete_many(query)
    # print(x.deleted_count, ' objects has been deleted.')


def update_datas(query, values, collection, db='articles'):
    mydb = myclient[db]
    mycol = mydb[collection]
    x = mycol.update_many(query, values)
    # print(x.modified_count, ' objects has been modified.')


def delete_col(collection, db='articles'):
    mydb = myclient[db]
    mycol = mydb[collection]
    mycol.drop()


if __name__ == '__main__':
    insert_datas([{'a': 'hello2'}, {'a': 'hello3'}, {'a': 'hello4'}], 'fxbg')
    data = show_datas('fxbg', sortby='a', seq=False)
    print(data)
    delete_datas({'a': {'$regex': '^mod'}}, 'fxbg')
    update_datas({'a': {'$regex': '^hello'}}, {'$set': {'a': 'modified'}}, 'fxbg')
    data = show_datas('fxbg')
    print(data)
    # 获取数据库list
    dblist = myclient.list_database_names()
    print(dblist)
    id_match_res = show_datas('woshipm',query={'id': 3134984})
    print(id_match_res)
