from keras_preprocessing.text import Tokenizer
from keras.preprocessing import sequence
from keras.models import load_model
import pickle
import jieba
import os
import numpy as np
import pandas as pd
from collections import Counter
import seaborn as sns
import matplotlib.pyplot as plt
import time
import math
# import sys
# sys.path.append('/Users/vincentl/PycharmProjects/Aita-Tech/Liushui')
import mydata as data
import Modules.public_module as md

input_path = 'output2.xlsx'
output_path = 'predict2.xlsx'

def pre_review(texts, in_data, out_data):
    with open('word_tok.pickle', 'rb') as handle:
        word_tok = pickle.load(handle)
    model = load_model('class.h5')

    texts = list(map(lambda x: x if type(x) == str else '', texts))  # replace nan cell into ''
    texts = [jieba.cut(i, cut_all=False) for i in texts]
    texts = [' '.join(i) for i in texts]  # 'xxxx' into 'xx xx xx'
    input_seq = word_tok.texts_to_sequences(texts)
    x_test = sequence.pad_sequences(input_seq, maxlen=15, padding='post')
    # print(word_tok.word_index)
    x_test = np.insert(x_test, -1, in_data, axis=1)
    x_test = np.insert(x_test, -1, out_data, axis=1)
    print(x_test)
    predict = model.predict_classes(x_test)

    print(predict)
    return predict


if __name__ == '__main__':
    start_time = time.time()
    test_data = ['采购发给银行电子公司', '安徽部分报销', '货款', '登报费']
    df = pd.read_excel(input_path)
    df.rename(columns=data.english_mapping, inplace=True)
    texts = df['receiver_name'] + df['abstract']
    print(texts.values)
    # append in and out money amount
    in_data = df['received_amount'].to_list()
    out_data = df['sent_amount'].to_list()
    in_data = [math.log(i, 2) if i > 1 else 0 for i in in_data]
    out_data = [math.log(i, 2) if i > 1 else 0 for i in out_data]
    predicts = pre_review(texts, in_data, out_data)

    with open('label_tok.pickle', 'rb') as handle:
        label_tok = pickle.load(handle)
    map = label_tok.word_index
    rev_map = md.reverse_oneone_map(map)
    cn_predicts = [rev_map[i] for i in predicts]

    print(len(cn_predicts))
    print(df.shape)
    df['predicted'] = pd.Series(data=cn_predicts)
    writer = pd.ExcelWriter(output_path)
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    print('DataFrame is written successfully to the Excel File.')
    counter = Counter(cn_predicts)
    print(dict(counter))

    # x轴中文乱码问题
    plt.rcParams['font.family'] = ['Arial Unicode MS']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    sns.set_style('whitegrid', {'font.sans-serif': ['Arial Unicode MS', 'Arial']})

    # 显示不完全问题
    plt.figure(figsize=(15, 8))
    plt.tick_params(axis='x', labelsize=8)  # 设置x轴标签大小
    plt.xticks(rotation=-25)
    bar_plot = sns.barplot(x=list(dict(counter).keys()), y=list(dict(counter).values()), palette='muted')
    # sns.countplot(data=predicts)
    plt.show()
    end_time = time.time()
    print('======= Time taken: %f =======' %(end_time - start_time))
