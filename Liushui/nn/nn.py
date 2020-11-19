#coding:utf-8
from keras.preprocessing.text import Tokenizer
from keras.preprocessing import sequence
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers.core import Dense, Activation, Dropout, Flatten
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import SimpleRNN
import nltk
import jieba
import json
import pandas as pd
import numpy as np
import pickle
from collections import Counter
import seaborn as sns
import matplotlib.pyplot as plt
import time
import sys
from collections import Counter
sys.path.append('/Users/vincentl/PycharmProjects/Aita-Tech/Liushui')
# print(sys.path)
import mydata as data


path = 'output.xlsx'

def get_data():
    df = pd.read_excel(path)
    df.rename(columns=data.english_mapping, inplace=True)
    df = df.iloc[:, 2:]

    df['system_classification'] = df['system_classification'].fillna('null')  # 将df中A列所有空值赋值为'null'
    df = df[df['system_classification'] != 'null']
    # print(df.columns.ravel())
    df['abstract'] = df['abstract'].fillna('')
    df['sender_name'] = df['sender_name'].fillna('')
    data_df = df[['received_amount', 'sent_amount', 'receiver_name', 'abstract', 'system_classification']]
    data_df['texts'] = df['receiver_name'] + data_df['abstract']
    data_df.to_csv('data.csv')

    # label generating
    labels = data_df['system_classification'].tolist()
    labels = [i for i in labels if type(i) == str]
    labels = [i.replace('/', '') for i in labels]
    label_tok = Tokenizer(num_words=50, lower=False, split=' ')
    label_tok.fit_on_texts(labels)
    print(label_tok.document_count)
    word2index = label_tok.word_index
    token_label = np.array(label_tok.texts_to_sequences(labels))
    oh_label = to_categorical(token_label.reshape(-1))  # to one hot format
    print(oh_label[:5])
    print(oh_label.shape)

    # abstract tokenizing
    abstracts = data_df['texts'].tolist()
    abstracts = list(map(lambda x: x if type(x) == str else '', abstracts)) # replace nan cell into ''
    abstracts = [jieba.cut(i, cut_all=False) for i in abstracts]
    abstracts = [' '.join(i) for i in abstracts]        # 'xxxx' into 'xx xx xx'
    print(abstracts[:5])
    word_tok = Tokenizer(num_words=600, lower=False, split=' ')
    word_tok.fit_on_texts(abstracts)
    word2index = word_tok.word_index
    token_sentences = word_tok.texts_to_sequences(abstracts)
    print(word2index)
    x_train = sequence.pad_sequences(token_sentences, maxlen=15, padding='post')
    print(x_train[:10])

    model = Sequential()

    model.add(Embedding(
        output_dim=32,
        input_dim=1000,
        input_length=15
    ))
    model.add(Dropout(0.1))
    model.add(SimpleRNN(units=16))
    model.add(Dense(units=256, activation='relu'))
    model.add(Dropout(0.1))
    model.add(Dense(units=16, activation='softmax'))  # 0-1
    model.compile(
        loss='binary_crossentropy',
        optimizer='adam',
        metrics=['accuracy']
    )

    model.fit(x=x_train, y=oh_label, batch_size=40, validation_split=0.2, epochs=10)

    model.save('class.h5')

    with open('word_tok.pickle', 'wb') as handle:
        pickle.dump(word_tok, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open('label_tok.pickle', 'wb') as handle:
        pickle.dump(label_tok, handle, protocol=pickle.HIGHEST_PROTOCOL)



if __name__ == '__main__':
    start_time = time.time()
    get_data()
    end_time = time.time()

    print('======= Time taken: %f =======' %(end_time - start_time))