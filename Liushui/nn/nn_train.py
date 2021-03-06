# coding:utf-8
from keras.preprocessing.text import Tokenizer
from keras.preprocessing import sequence
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers.core import Dense, Activation, Dropout, Flatten
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import SimpleRNN
from keras.utils import plot_model
from sklearn import preprocessing
import jieba
import pandas as pd
import numpy as np
import pickle
import math
from collections import Counter
import seaborn as sns
import matplotlib.pyplot as plt
import time
import sys

sys.path.append('/Users/vincentl/PycharmProjects/Aita-Tech/Liushui')
import mydata as data

model_path = 'models/class.h5'
path = 'xlsx_files/yikong_label.xlsx'
rulePath = 'xlsx_files/system type rules.xlsx'
ABSTRACT_MAX_LEN = 20
IMPRECISE_CUT = True


def get_data(plot=True):
    df = pd.read_excel(path)
    if not 'type' in df.columns.ravel():
        df.rename(columns=data.english_mapping, inplace=True)

    df['system_classification'] = df['system_classification'].fillna('null')  # 将df中A列所有空值赋值为'null'
    df = df[df['system_classification'] != 'null']
    # print(df.columns.ravel())
    df['abstract'] = df['abstract'].fillna('')
    df['sender_name'] = df['sender_name'].fillna('')
    data_df = df[['received_amount', 'sent_amount', 'receiver_name', 'abstract', 'system_classification']]
    data_df['texts'] = df['receiver_name'] + data_df['abstract']
    # data_df.to_csv('data.csv')

    # label generating
    # add tokenize based sysrule instead of training set's type col
    label_df = pd.read_excel(rulePath, sheet_name=1, header=1)
    labels_for_tok = label_df['系统分类'].tolist()
    labels_for_tok = [i for i in labels_for_tok if type(i) == str]
    labels_for_tok = [i.replace('/', '') for i in labels_for_tok]
    label_tok = Tokenizer(num_words=50, lower=False, split=' ')
    label_tok.fit_on_texts(labels_for_tok)

    labels = data_df['system_classification'].tolist()
    labels = [i for i in labels if type(i) == str]
    labels = [i.replace('/', '') for i in labels]
    # label_tok = Tokenizer(num_words=50, lower=False, split=' ')
    # label_tok.fit_on_texts(labels)
    # print(label_tok.document_count)
    token_label = np.array(label_tok.texts_to_sequences(labels))
    oh_label = to_categorical(token_label.reshape(-1))  # to one hot format
    print(oh_label[:5])
    print(oh_label.shape)

    # abstract tokenizing
    abstracts = data_df['texts'].tolist()
    abstracts = list(map(lambda x: x if type(x) == str else '', abstracts))  # replace nan cell into ''
    abstracts = [jieba.cut(i, cut_all=IMPRECISE_CUT) for i in abstracts]
    abstracts = [' '.join(i) for i in abstracts]  # 'xxxx' into 'xx xx xx'
    print(abstracts[:10])
    word_tok = Tokenizer(num_words=600, lower=False, split=' ')
    word_tok.fit_on_texts(abstracts)
    token_sentences = word_tok.texts_to_sequences(abstracts)
    word2index = word_tok.word_index
    print(word2index)
    x_train = sequence.pad_sequences(token_sentences, maxlen=ABSTRACT_MAX_LEN, padding='post')
    print(x_train[:10])

    # append keyword matching label as new feature
    labels = data_df['system_classification'].tolist()
    labels = ['' if pd.isna(i) else str(i) for i in labels]
    labels = [i.replace('/', '') for i in labels]
    label_dig = [0 if not i else label_tok.word_index[i] for i in labels]
    print(label_dig[:50])
    print(label_tok.word_index)
    x_train = np.insert(x_train, -1, label_dig, axis=1)

    # append in and out money amount
    in_data = np.array(data_df['received_amount'].to_list())
    out_data = np.array(data_df['sent_amount'].to_list())
    in_data = [math.log(i, 2) if i > 0 else 0 for i in in_data]
    out_data = [math.log(i, 2) if i > 0 else 0 for i in out_data]
    # # scale to 0-1000 method
    # k = 1000 / (max(in_data) - min(in_data))
    # in_data = [k * (x - min(in_data)) for x in in_data]
    # k = 1000 / (max(out_data) - min(out_data))
    # out_data = [k * (x - min(out_data)) for x in out_data]

    # # scale to standard scaler method
    # scaler = preprocessing.StandardScaler()
    # in_data = scaler.fit_transform(in_data)
    # in_data = preprocessing.scale(in_data, with_mean=False)
    # out_data = preprocessing.scale(out_data, with_mean=False)
    # print('===========in======')
    # print(in_data[:30])
    # print(out_data[:30])
    x_train = np.insert(x_train, -1, in_data, axis=1)
    x_train = np.insert(x_train, -1, out_data, axis=1)
    print(x_train[:10])

    model = Sequential()

    model.add(Embedding(
        output_dim=32,
        input_dim=2000,  # after append the in and out, max value may be 1000, which exceeds input_dim if set to 1000.
        input_length=ABSTRACT_MAX_LEN + 3
    ))
    model.add(Dropout(0.1))
    model.add(SimpleRNN(units=16))
    model.add(Dense(units=256, activation='relu'))
    model.add(Dropout(0.1))
    model.add(Dense(units=39, activation='softmax'))  # 0-1, units changed from 16 to 39 after change tokenization
    model.compile(
        loss='binary_crossentropy',
        optimizer='adam',
        metrics=['accuracy']
    )

    history = model.fit(x=x_train, y=oh_label, batch_size=40, validation_split=0.2, epochs=10)
    if plot:
        plt.plot(history.history['acc'])
        plt.plot(history.history['val_acc'])
        plt.title('Model accuracy')
        plt.ylabel('Accuracy')
        plt.xlabel('Epoch')
        plt.legend(['Train', 'Test'], loc='upper left')
        plt.savefig('plots/training accuracy.png')
        plt.show()

    plot_model(model, to_file='model.png')

    # save model and tokenizers
    model.save(model_path)

    with open('models/word_tok.pickle', 'wb') as handle:
        pickle.dump(word_tok, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open('models/label_tok.pickle', 'wb') as handle:
        pickle.dump(label_tok, handle, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    start_time = time.time()
    get_data(False)
    end_time = time.time()

    print('======= Time taken: %f =======' % (end_time - start_time))
