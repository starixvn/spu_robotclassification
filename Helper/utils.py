import pandas as pd
from datetime import date
import os
from tqdm import tqdm
class Utilities():

    def read_data(location, file_name, is_entire = 1, length_of_assessment = None, start_date = None):
        
        try:
            if is_entire:
                data =  pd.read_csv(location + file_name)
            else:
                list_files = sorted(os.listdir(location))
                start_file_index = list_files.index(start_date + ".csv")
                list_target_files = list_files[start_file_index:start_file_index + length_of_assessment]
                data = pd.concat([pd.read_csv(location + fn) for fn in tqdm(list_target_files, desc = "Concat Files")], ignore_index = True)
            max_train_date = data.winlostdate.max()
            data.rename(columns = {"winlostdate":"ReportDate",
                                    "custid":"CustId",
                                    "sporttype":"SporttypeId",
                                    "bettype":"BettypeId",
                                    "liveindicator":"IsLive"}, inplace = True)
            data['ReportDate'] = data['ReportDate'].apply(lambda z : z.split(' ')[0])
            # print("data\n", data.head())
        except AttributeError:
            data =  pd.read_csv(location + file_name)
        return data
    
    @staticmethod
    def save_data(location, file_name, dataframe):
        dataframe.to_csv(location + file_name, index = False)

    @staticmethod
    def filter_categorie(categorie, dataframe):
        """
        >>> Input   :   categorie   : string | represents combination sport-bettype-liveIndicator-whichDay
                        dataframe   : pandas.DataFrame
        >>> Output  :   filtered pandas.DataFrame
        """
        cols = [col for col in dataframe.columns.to_list() if categorie in col]
        cat_df = dataframe[cols]

        # filter non-play customers
        filtered_cat_df = cat_df.dropna()
        return filtered_cat_df

    @staticmethod
    def compute_deltas(margin, streak, amplitude):
        """
        >>> Input   :   margin      , a float number in range[-1,1]
                        streak      , an integer
        >>> Output  :   delta_a     , a float number
                        delta_b     , a float number
        """
        if margin > 0:
            return amplitude*margin*abs(streak), 0
        else:
            return 0, amplitude*abs(margin)*abs(streak)

    @staticmethod
    def is_weekend(a_given_date):
        """
        Simply check a given date is if it is weekend

        >>> Input   :   a_given_date    : string | format YYYY-MM-DD

        >>> Output  :   True or False
        """
        year_month_day = a_given_date.split('-')
        year,month,day = year_month_day[0],year_month_day[1],year_month_day[2]
        my_day = date(int(year), int(month), int(day)).weekday()
        if my_day >= 5:
            return 'WE'
        else:
            return 'WD'
    
    @staticmethod
    def transform_sport_type(x):
        if (x-1)*(x-2) == 0:
            return 's' + str(x)
        else:
            return 'other'
    
    @staticmethod
    def transform_bet_type(x):
        return 'b' + str(x)
        
    def preprocess_data(data, str_to_id, is_aggregated = 0, dead_line = None, min_bet_count = 10, is_day_eliminated = 0):
        data = data[data.BettypeId.isin([1, 3, 7, 8])]
        yourdata = data[['ReportDate', 'CustId', 'IBCWinloss', 'IBCTurnover', 'BetCount']]
        yourdata['UserWinloss'] = - yourdata['IBCWinloss']
        yourdata.rename(columns = {'CustId':'C'}, inplace = True)
        mydata = pd.DataFrame()
        mydata['IsLive'] = data['IsLive'].apply(lambda x : 'L' if x else 'NL') # mydata['IsLive']
        mydata['SporttypeId'] = data['SporttypeId'].apply(Utilities.transform_sport_type) # mydata['SporttypeId']
        mydata['BettypeId'] = data['BettypeId'].apply(Utilities.transform_bet_type) # mydata['BettypeId']
        if not is_day_eliminated:
            mydata['Day'] = data['ReportDate'].apply(Utilities.is_weekend) # mydata['Day']
            mydata['Category_in_short'] = mydata['SporttypeId'] + mydata['BettypeId'] + mydata['IsLive'] + mydata['Day']
        else:
            mydata['Category_in_short'] = mydata['SporttypeId'] + mydata['BettypeId'] + mydata['IsLive']
        mydata['CAT'] = mydata['Category_in_short'].apply(lambda z : str_to_id[z]['CategoryID'])

        old = pd.merge(yourdata, mydata, right_index = True, left_index = True)
        if is_aggregated:
            new = old.groupby(['C', 'CAT']).sum().reset_index()
            new['ReportDate'] = dead_line
            # new = new[new.UserWinloss != 0]
            new = new[(new.UserWinloss != 0) & (new.BetCount >= min_bet_count)]
            new.to_csv("D:/Project/Robot/TEST_DATA/agg_test.csv", index=False)
        else:
            
            new = old.groupby(['C', 'CAT', 'ReportDate']).sum().reset_index()
            new = new[(new.UserWinloss != 0) & (new.BetCount >= min_bet_count)]
            # new = new[new.UserWinloss != 0]
            new.to_csv("D:/Project/Robot/TEST_DATA/preprocessed.csv", index=False)
    
        return new

    def transform_category_mapping(data, is_day_eliminated = 0):
        data = data.set_index('CategoryID')
        mydata = pd.DataFrame()
        mydata['IsLive'] = data['IsLive'].apply(lambda x : 'L' if x else 'NL') # mydata['IsLive']
        mydata['SportID'] = data['SportID'].apply(Utilities.transform_sport_type) # mydata['SporttypeId']
        mydata['BettypeId'] = data['BettypeID'].apply(Utilities.transform_bet_type) # mydata['BettypeId'
        if not is_day_eliminated:
            mydata['Day'] = data['IsWeekend'].apply(lambda z : 'WE' if z else 'WD')
            mydata['Category_in_short'] = mydata['SportID'] + mydata['BettypeId'] + mydata['IsLive'] + mydata['Day']
        else:
            mydata['Category_in_short'] = mydata['SportID'] + mydata['BettypeId'] + mydata['IsLive']
        mydata1 = mydata[['Category_in_short']].reset_index().set_index('Category_in_short')
        # print("mydata\n", mydata)
        mydata2 = mydata[['Category_in_short']]
        str_to_id = mydata1.to_dict(orient = 'index')
        id_to_str = mydata2.to_dict(orient = 'index')
        return str_to_id, id_to_str