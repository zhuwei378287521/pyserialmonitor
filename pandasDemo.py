# -*-coding:utf-8-*-
import time

import pandas as pd

CSV_FILE_PATH = './test.csv'

data = {'row1': [1, 2, 3, 'biubiu'], 'row2': [3, 1, 3, 'kaka']}
print(data)
data_df = pd.DataFrame(data)
# data_df.to_csv('./test.csv')


# df = pd.read_csv(CSV_FILE_PATH)
# print(df.head(5))

a = [[time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), time.time(), '1.2'],
     [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), time.time(), '10'],
     [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), time.time(), '5']]
df = pd.DataFrame(a, columns=['time', 'timestamp', 'data'])
print(df)
#df.to_csv(CSV_FILE_PATH)
df.to_csv(CSV_FILE_PATH, mode='a', header=False)
