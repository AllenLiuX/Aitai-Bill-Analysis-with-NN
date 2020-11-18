#coding:utf-8
#python 3.7

from keras_preprocessing.text import Tokenizer
from keras_preprocessing import sequence

from keras.preprocessing.text import Tokenizer
from keras.models import Sequential
from keras.layers.core import Dense, Activation, Dropout, Flatten
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import SimpleRNN
from keras.preprocessing import sequence
# from sklearn.model_selection import train_test_split
# import nltk
# from nltk.corpus import stopwords
# import collections
import time
import pandas as pd
import numpy as np
import os
from warnings import simplefilter
import warnings

# remove Future Warning
simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings('ignore')

def readfeed():
    feedlist = []
    # get negative feed
    for i in os.listdir('imdb/train/neg'):
        with open('imdb/train/neg/'+i, 'r') as r:
            res = r.readline()
            feedlist.append(res)
    # get positive feed
    for i in os.listdir('imdb/train/pos'):
        with open('imdb/train/pos/' + i, 'r') as r:
            res = r.readline()
            feedlist.append(res)
    print(len(feedlist))

    # # 评论内容整合
    # content = pos_list.extend(neg_list)
    # content = pos_list
    return feedlist


if __name__ == '__main__':
    start = time.time()
    word = readfeed()
    token = Tokenizer(num_words=2000)
    token.fit_on_texts(word)
    x_train_seq = token.texts_to_sequences(word)
    x_train = sequence.pad_sequences(x_train_seq, maxlen=200, padding='post')
    # 创建标签
    all_label = [1]*12500 + [0]*12500

    model = Sequential()

    model.add(Embedding(
        output_dim=32,
        input_dim=2000,
        input_length=200
    ))
    model.add(Dropout(0.1))
    model.add(SimpleRNN(units=16))
    model.add(Dense(units=256, activation='relu'))
    model.add(Dropout(0.1))
    model.add(Dense(units=1, activation='sigmoid')) #0-1
    model.compile(
        loss='binary_crossentropy',
        optimizer='adam',
        metrics=['accuracy']
    )

    model.fit(x=x_train, y=all_label, batch_size=400, validation_split=0.2, epochs=5)

    model.save('imdb.h5')

    print('----- time taken: %f -----' % (time.time()-start))


