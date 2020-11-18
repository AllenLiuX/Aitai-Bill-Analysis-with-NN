from keras_preprocessing.text import Tokenizer
from keras.preprocessing import sequence
from keras.models import load_model
import os
import numpy as np
from collections import Counter
import seaborn as sns
import matplotlib.pyplot as plt
import time

def pre_review(reviews):
    resdict = {1:'negative', 0: 'positive'}
    token = Tokenizer(num_words=500)
    # newtext = [newtext]
    newtext = reviews
    token.fit_on_texts(newtext)
    input_seq = token.texts_to_sequences(newtext)
    pad = sequence.pad_sequences(input_seq, maxlen=200)
    model = load_model('imdb.h5')
    predict = model.predict_classes(pad)
    # print(resdict[predict[0][0]])
    print(predict)
    return predict


if __name__ == '__main__':
    start_time = time.time()
    pos = []
    for i in os.listdir('imdb/test/pos'):
        with open('imdb/test/pos/' + i, 'r') as r:
            res = r.readline()
            pos.append(res)
    pred = pre_review(pos)
    pred = np.array(pred).reshape(-1)
    count = Counter(pred)
    count = dict(count)
    bar_plot = sns.barplot(x=list(count.keys()), y=list(count.values()), palette='muted')
    plt.show()

    end_time = time.time()
    print('======= Time taken: %f =======' % (end_time - start_time))
