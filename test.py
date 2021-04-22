# String = "1,3,8"
# Lyst = String.split(',')
# print('Lyst\n',Lyst)

import pandas as pd
# import numpy as np
# from utils import filter_categorie
# from scipy.stats import shapiro
# from scipy.stats.distributions import norm
# from GB_classify import GB_classify
class Diego():
    def __init__(a):
        pass
    def build_data(n):
        return list(range(n))
    
    # def compute(data_points):
    #     for point in data_points:
    #         print("Data Point Square %s" % point**2)
    def get_min_max(self, data_points):
        self.min = min(data_points)
        print("MIN %s" % self.min)
        self.max = max(data_points)
        print("MAX %s" % self.max)
    
    def normalize_data(self, data_points):
        for point in data_points:
            nmd = (point - self.min)/(self.max - self.min)
            print("Normalized Data Point %.3f" % nmd)
            # print("Normalized Data Point %.3f" % point)
    
    def run(self, n):
        data_points = Diego.build_data(n)
        # MIN = 
        self.get_min_max(data_points)
        self.normalize_data(data_points)
def transform_sport_type(x):
        if (x-1)*(x-2) == 0:
            return 's' + str(x)
        else:
            return 'other'
def transform_bet_type(x):
    return 'b' + str(x)

if __name__=='__main__':
    # location = "D:/Project/Formula_BET/SaveData/PreprocessedData/"
    # file_name = "preprocessed.csv"
    # df = pd.read_csv(location+file_name,index_col=0)
    location = "C:/Users/diego.nguyen/Desktop/"
    file_name = "category_mapping.csv"
    data = pd.read_csv(location + file_name)
    data = data.set_index('CategoryID')
    mydata = pd.DataFrame()
    mydata['IsLive'] = data['IsLive'].apply(lambda x : 'L' if x else 'NL') # mydata['IsLive']
    mydata['SportID'] = data['SportID'].apply(transform_sport_type) # mydata['SporttypeId']
    mydata['BettypeId'] = data['BettypeID'].apply(transform_bet_type) # mydata['BettypeId'
    mydata['Day'] = data['IsWeekend'].apply(lambda z : 'WE' if z else 'WD')
    mydata['Category_in_short'] = mydata['SportID'] + mydata['BettypeId'] + mydata['IsLive'] + mydata['Day']
    # print("mydata\n", mydata)
    mydata = mydata[['Category_in_short']].reset_index().set_index('Category_in_short')
    # print("mydata\n", mydata)
    cat_map = mydata.to_dict(orient = 'index')
    print("cat_map\n", cat_map)
    # df['SporttypeId'] = df['SporttypeId'].map(str)
    # ls = ['1', '2']
    # df['SporttypeId'] = df['SporttypeId'].apply(lambda x : 'other' if x not in ls)
    # btl = df.BettypeId.unique()
    # df = df.head(5)
    # df['IsLive'] = df['IsLive'].apply(lambda x : 'L' if x else 'NL')
    # print(btl)
    # df = df[['CustId', 'SporttypeId', 'BettypeId', 'IBCWinloss']]
    # for row in df.itertuples(name=None, index=False):
    # for row in df.itertuples():
    #     print(row.IBCWinloss)
    # for _,row in df.iterrows():
    #     print(row)
    # df = df.set_index(['CustId','SporttypeId']).to_dict(orient = 'index')
    # print('cols\n', cols)
    # categorie = 's1b7LWD'
    # cat_df = filter_categorie(categorie,df)
    # cat_df.info()
    # print('Category dataframe\n',cat_df.sample(5))
    # my_sequence = cat_df.loc[37717858,categorie+'WL_sequence']
    # my_array = np.array([float(x) for x in my_sequence.split(',') if x != ''])
    # print('Get sequence\n',type(my_sequence))
    # for k in df.index:
    #     print('Get sequence\n',k)
    # data = np.random.normal(loc = 20, scale = 5, size = 15000)
    # data = 20 + 5*np.random.randn(100)
    # stat, p = shapiro(data)
    # print("stat = %.3f, p = %.3f" % (stat, p))
    # if p > .05 :
    #     print("Probably Gaussian")
    # else:
    #     print("Probably not Gaussian")
    # mean, std = norm.fit(data)
    # print("mean = %.3f, var = %.3f" % (mean, std))
    # classifier = GB_classify(0,0,2,2)
    # mode = classifier.get_mode()
    # std = classifier.get_std()
    # print("mode = %.3f, std = %.3f" % (mode, std))
    # diego = Diego()
    # diego.run(10)
    # my_dict = {'s1b1LWDTO':3, 's1b1NLWDTO':5, 's1b3LWEBC':6, 's2b7LWEBC':8}
    # cats_list = my_dict.keys()
    # total_bc = sum([my_dict[cat] for cat in cats_list if cat.endswith('BC')])
    # total_to = sum([my_dict[cat] for cat in cats_list if cat.endswith('TO')])
    # print('total_to\n', total_to)
    # a = 0
    # for _ in range(3):
    #     a += 1/3
    # print('a\n',a)
    # b = 's1b1LWDTO'
    # print(b[:-2])
    # data = [{'C':2053, 'S':1, 'B':1}, {'C':1994, 'S':2, 'B':3}, {'C':2021, 'S':2, 'B':7}]
    # data = pd.DataFrame(data)
    # print(data)
    # data = data.set_index('C')
    # print(data)
    # mydata = pd.DataFrame()
    # mydata['diego'] = data['S'].apply(lambda z : 's' + str(z))
    # mydata['tania'] = data['B'].apply(lambda z : 'b' + str(z))
    # print(mydata)
    # location = "D:/Project/Formula_BET/SaveData/PreprocessedData/"
    # file_name = "preprocessed.csv"

    # filter categorie
    # categorie = 's1b7LWD'
    # df = pd.read_csv(location+file_name,index_col=0)
    # print('Sample\n',data.ReportDate.unique())
    # df.info()
    # wanring_cols = np.array([403,404,405,412,413,414,421,422,423,430,431,432]) - 1
    # print('Last columns',df.iloc[:,wanring_cols].sample(10))
    # filtered_df = df.iloc[:,wanring_cols]
    # filtered_df = filtered_df.dropna()
    # print('Num rows',filtered_df)
    # cat_df = filter_categorie(categorie,df)
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
    # _,_,_, output = create_peak_std_df(categorie,cat_df)
    # print('Sample\n',output.sample(20))