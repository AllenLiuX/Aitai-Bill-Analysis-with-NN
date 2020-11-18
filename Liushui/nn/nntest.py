#coding:utf-8
from keras.preprocessing.text import Tokenizer
from keras.preprocessing import sequence
import time



if __name__ == '__main__':
    start = time.time()
    s1 = 'i am happy'
    s2 = 'i am henry'
    s3 = 'i was told that i need to go home now'
    s4 = 'hello there.'
    str = [s1, s2, s3, s4]

    tok = Tokenizer(num_words=20)
    tok.fit_on_texts(str)
    print(tok.document_count)
    print(tok.word_index)
    print(tok.texts_to_sequences(str))
    print(sequence.pad_sequences(tok.texts_to_sequences(str), maxlen=20, padding='post'))       # post or pre

    end = time.time()
    print('------time taken: %f ------' % (end-start))