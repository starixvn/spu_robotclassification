# String = "1,3,8"
# Lyst = String.split(',')
# print('Lyst\n',Lyst)

import pandas as pd
import numpy as np
from utils import filter_categorie
if __name__=='__main__':
    # location = "D:/Project/Formula_BET/SaveData/PreprocessedData/"
    # file_name = "preprocessed.csv"
    # df = pd.read_csv(location+file_name,index_col=0)
    location = "C:/Users/diego.nguyen/Downloads/"
    file_name = "robot_classification (3).csv"
    df = pd.read_csv(location+file_name)
    print(df.tail())
    # categorie = 's1b7LWD'
    # cat_df = filter_categorie(categorie,df)
    # cat_df.info()
    # print('Category dataframe\n',cat_df.sample(5))
    # my_sequence = cat_df.loc[37717858,categorie+'WL_sequence']
    # my_array = np.array([float(x) for x in my_sequence.split(',') if x != ''])
    # print('Get sequence\n',type(my_sequence))
    # for k in df.index:
    #     print('Get sequence\n',k)