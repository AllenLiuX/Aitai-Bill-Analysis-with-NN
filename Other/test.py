import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import time

if __name__ == '__main__':
    start_time = time.time()
    df = pd.DataFrame({'col1': [2, 3], 'col2': [3, 4], 'col3': ['a', 'c']})
    print(df)
    dic = df.set_index('col1')['col2'].to_dict()
    print(dic)
    end_time = time.time()
    print('======= Time taken: %f =======' %(end_time - start_time))
