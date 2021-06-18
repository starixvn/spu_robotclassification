from datetime import date
import pandas as pd
class Data_Preprocessing_Manager():

    @staticmethod
    def filter_categorie(categorie, dataframe):
        """
        >>> Input   :   categorie   : string | represents combination sport-bettype-liveIndicator-whichDay
                        dataframe   : pandas.DataFrame
        >>> Output  :   filtered pandas.DataFrame
        """
        cols = [col for col in dataframe.columns.to_list() if categorie in col]
        cat_df = dataframe[cols]
        # print("cat_df\n", cat_df.sample(5))
        # cat_df.to_csv(f"D:/Project/Robot/TRANSFORMED_DATA/{categorie}.csv", index = False)
        # filter non-play customers
        filtered_cat_df = cat_df.dropna(how = "all")
        assert len(filtered_cat_df.index) > 0
        return filtered_cat_df


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

    @staticmethod
    def aggregate(df, winloss_sign, phase):
        marginalization = df.groupby(['C', 'CAT']).sum().reset_index()
        day_count = df.groupby(['C', 'CAT'])["IBCWinloss"].count().reset_index()
        target_cols = ["UserWinloss", "IBCTurnover", "BetCount"]
        marginalization = marginalization.rename(columns = {key:phase + winloss_sign + key for key in target_cols})
        day_count = day_count.rename(columns = {"IBCWinloss":phase + winloss_sign + "ActiveDays"})
                                                    
        merger = marginalization.merge(day_count, how = "inner", right_on = ["C", "CAT"], left_on = ["C", "CAT"])
        merger[phase + winloss_sign + "WinlossPerDay"] = merger[phase + winloss_sign + "UserWinloss"]/merger[phase + winloss_sign + "ActiveDays"]
        return merger
    
    def preprocess_data(data, str_to_id, is_training, is_aggregated = 0, dead_line = None, min_bet_count = 10, 
                        is_day_eliminated = 0, is_live_indicator_eliminated = 0, is_bettype_eliminated = 0):
        if is_training:
            phase = "Training"
        else:
            phase = "Testing"
        data = data[data.BettypeId.isin([1, 3, 7, 8])]
        yourdata = data[['ReportDate', 'CustId', 'IBCWinloss', 'IBCTurnover', 'BetCount']]
        yourdata['UserWinloss'] = - yourdata['IBCWinloss']
        yourdata.rename(columns = {'CustId':'C'}, inplace = True)
        mydata = pd.DataFrame()
        mydata['SporttypeId'] = data['SporttypeId'].apply(Data_Preprocessing_Manager.transform_sport_type) # mydata['SporttypeId']
        
        if is_day_eliminated and is_live_indicator_eliminated and is_bettype_eliminated:
            mydata['Category_in_short'] = mydata['SporttypeId']
        elif is_day_eliminated and is_live_indicator_eliminated:
            mydata['BettypeId'] = data['BettypeId'].apply(Data_Preprocessing_Manager.transform_bet_type) # mydata['BettypeId']
            mydata['Category_in_short'] = mydata['SporttypeId'] + mydata['BettypeId']
        elif is_day_eliminated:
            mydata['BettypeId'] = data['BettypeId'].apply(Data_Preprocessing_Manager.transform_bet_type) # mydata['BettypeId']
            mydata['IsLive'] = data['IsLive'].apply(lambda x : 'L' if x else 'NL') # mydata['IsLive']
            mydata['Category_in_short'] = mydata['SporttypeId'] + mydata['BettypeId'] + mydata['IsLive']
        else:
            mydata['BettypeId'] = data['BettypeId'].apply(Data_Preprocessing_Manager.transform_bet_type) # mydata['BettypeId']
            mydata['IsLive'] = data['IsLive'].apply(lambda x : 'L' if x else 'NL') # mydata['IsLive']
            mydata['Day'] = data['ReportDate'].apply(Data_Preprocessing_Manager.is_weekend) # mydata['Day']
            mydata['Category_in_short'] = mydata['SporttypeId'] + mydata['BettypeId'] + mydata['IsLive'] + mydata['Day']
        mydata['CAT'] = mydata['Category_in_short'].apply(lambda z : str_to_id[z]['CategoryID'])

        merged = pd.merge(yourdata, mydata, right_index = True, left_index = True)
        if is_aggregated:
            # index_reseted = merged.groupby(['C', 'CAT']).sum().reset_index()
            
            positive_winloss = merged[merged.UserWinloss > 0]
            positive_merger = Data_Preprocessing_Manager.aggregate(positive_winloss, winloss_sign = "Positive", phase = phase)            
            # print("positive_merger\n", positive_merger.head())
            negative_winloss = merged[merged.UserWinloss < 0]
            negative_merger = Data_Preprocessing_Manager.aggregate(negative_winloss, winloss_sign = "Negative", phase = phase)
            # print("negative_merger\n", negative_merger.head())
            the_finalized = positive_merger.merge(negative_merger, how = "outer", on = ["C", "CAT"])
            the_finalized['ReportDate'] = dead_line
            the_finalized = the_finalized.fillna(0)
            the_finalized[phase + "ActiveDays"] = the_finalized[phase + "NegativeActiveDays"] + \
                                                    the_finalized[phase + "PositiveActiveDays"]
            the_finalized[phase + "TurnOver"] = the_finalized[phase + "NegativeIBCTurnover"] + \
                                                the_finalized[phase + "PositiveIBCTurnover"]
            the_finalized[phase + "UserWinloss"] = the_finalized[phase + "NegativeUserWinloss"] + \
                                                    the_finalized[phase + "PositiveUserWinloss"]
            the_finalized[phase + "BetCount"] = the_finalized[phase + "NegativeBetCount"] + \
                                                the_finalized[phase + "PositiveBetCount"]
            # print("the_finalized\n", the_finalized.head())
            # print("NegativeWinlossActiveDays = " + str(the_finalized.NegativeWinlossActiveDays.unique()))
            print(phase + "ActiveDays = " + str(the_finalized[phase + "ActiveDays"].unique()))
            # index_reseted = index_reseted[(index_reseted.UserWinloss != 0) & (index_reseted.BetCount >= min_bet_count)]
            the_finalized.to_csv(f"D:/Project/Robot/TEST_DATA/agg_{phase}.csv", index=False)
        else:
            
            the_finalized = merged.groupby(['C', 'CAT', 'ReportDate']).sum().reset_index()
            # the_finalized = the_finalized[(the_finalized.UserWinloss != 0) & (the_finalized.BetCount >= min_bet_count)]
            # the_finalized = the_finalized[the_finalized.UserWinloss != 0]
            the_finalized.to_csv(f"D:/Project/Robot/TEST_DATA/preprocessed_{phase}.csv", index = False)
            # the_finalized = the_finalized[(the_finalized.C == 13515302) & (the_finalized.CAT == 2)]
            # print("TAIL of the_finalized\n", the_finalized.tail(10))
        return the_finalized