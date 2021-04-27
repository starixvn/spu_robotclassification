import pandas as pd
from datetime import date

class Utilities():

    def read_data(location, file_name):
        
        try:
            data =  pd.read_csv(location + file_name, skiprows = [1])
            # print("data with winlostdate col\n", data.head())
            max_train_date = data.winlostdate.max()
            data.rename(columns = {"winlostdate":"ReportDate",
                                    "custid":"CustId",
                                    "sporttype":"SporttypeId",
                                    "bettype":"BettypeId"}, inplace = True)
        except Exception as e:
            print(type(e).__name__)
            data =  pd.read_csv(location + file_name)
        # finally:
        return data
    
    def save_data(location, file_name, dataframe):
        # if type(file) == pd.core.DataFrane
        dataframe.to_csv(location + file_name)

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

    def compute_deltas(margin, streak, amplitude=10.):
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
    
    def transform_sport_type(x):
        if (x-1)*(x-2) == 0:
            return 's' + str(x)
        else:
            return 'other'
    def transform_bet_type(x):
        return 'b' + str(x)

    def preprocess_data(data, cat_map):
        data = data[data.BettypeId.isin([1, 3, 7, 8])]
        yourdata = data[['ReportDate', 'CustId', 'IBCWinloss', 'IBCTurnover', 'BetCount']]
        yourdata.rename(columns = {'CustId':'C'}, inplace = True)
        mydata = pd.DataFrame()
        mydata['IsLive'] = data['IsLive'].apply(lambda x : 'L' if x else 'NL') # mydata['IsLive']
        mydata['SporttypeId'] = data['SporttypeId'].apply(Utilities.transform_sport_type) # mydata['SporttypeId']
        mydata['BettypeId'] = data['BettypeId'].apply(Utilities.transform_bet_type) # mydata['BettypeId']
        mydata['Day'] = data['ReportDate'].apply(Utilities.is_weekend) # mydata['Day']
        mydata['Category_in_short'] = mydata['SporttypeId'] + mydata['BettypeId'] + mydata['IsLive'] + mydata['Day']
        mydata['CAT'] = mydata['Category_in_short'].apply(lambda z : cat_map[z]['CategoryID'])
    
        return pd.merge(yourdata, mydata, right_index = True, left_index = True)

    def transform_category_mapping(data):
        data = data.set_index('CategoryID')
        mydata = pd.DataFrame()
        mydata['IsLive'] = data['IsLive'].apply(lambda x : 'L' if x else 'NL') # mydata['IsLive']
        mydata['SportID'] = data['SportID'].apply(Utilities.transform_sport_type) # mydata['SporttypeId']
        mydata['BettypeId'] = data['BettypeID'].apply(Utilities.transform_bet_type) # mydata['BettypeId'
        mydata['Day'] = data['IsWeekend'].apply(lambda z : 'WE' if z else 'WD')
        mydata['Category_in_short'] = mydata['SportID'] + mydata['BettypeId'] + mydata['IsLive'] + mydata['Day']
        mydata = mydata[['Category_in_short']].reset_index().set_index('Category_in_short')
        # print("mydata\n", mydata)
        cat_map = mydata.to_dict(orient = 'index')
        return cat_map