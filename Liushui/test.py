import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import time

if __name__ == '__main__':
    start_time = time.time()
    df1 = pd.DataFrame(np.ones((4, 4)) * 1, columns=list('DCBA'), index=list('4321'))
    df2 = pd.DataFrame(np.ones((4, 4)) * 2, columns=list('FEDC'), index=list('6543'))
    df3 = pd.DataFrame(np.ones((4, 4)) * 3, columns=list('DCBA'), index=list('6521'))
    all_df = pd.DataFrame(columns=['in', 'out', 'balance'])
    print(df1, df2, df3, sep='\n')
    df_sum = df1.add(df3, fill_value=0)
    print(df_sum)
    s = df_sum.iloc[2]
    print('2021' > '2020')
    # print(s.name)
    print('======= Time taken: %f =======' % (time.time() - start_time))
