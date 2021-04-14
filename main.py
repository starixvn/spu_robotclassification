import pandas as pd
import numpy as np
from utils import filter_categorie, create_peak_std_df
from GB_classify import GB_classify
from TransformData import TransformData

if __name__=='__main__':
    # location = "C:/Users/diego.nguyen/Downloads/"
    # file_name = "robot_classification (3).csv"
    location = "D:/Project/Formula_BET/SaveData/PreprocessedData/"
    file_name = "preprocessed.csv"

    # filter categorie
    categorie = 's1b7LWD'
    # df = pd.read_csv(location+file_name)
    df = pd.read_csv(location+file_name,index_col=0)
    # print('Sample\n',df.sample(3))
    # df.info()
    # wanring_cols = np.array([403,404,405,412,413,414,421,422,423,430,431,432]) - 1
    # print('Last columns',df.iloc[:,wanring_cols].sample(10))
    # filtered_df = df.iloc[:,wanring_cols]
    # filtered_df = filtered_df.dropna()
    # print('Num rows',filtered_df)
    cat_df = filter_categorie(categorie,df)
    # print('Category dataframe\n',cat_df.sample(5))
    # cus = GB_classify(0,0)
    # while True:
    #     try:
    #         input_from_user = input("Please enter result: ")
    #         win_status, lose_status = int(input_from_user.split(" ")[0]),int(input_from_user.split(" ")[1])
    #         cus.update_hyper_params(win_status,lose_status)
    #         cus.visualize_current_posterior()
    #     except ValueError:
    #         continue
    # obj = TransformData(df)
    # obj.transform()
    # print('Bettypes\n',df.BettypeId.unique())
    _,_,_, output = create_peak_std_df(categorie,cat_df)
    print('Sample\n',output.sample(20))