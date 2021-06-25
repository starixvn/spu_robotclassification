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
    
    @staticmethod
    def prepare_data(data):
        data = data[data.BettypeId.isin([1, 3, 7, 8])]
        yourdata = data[['ReportDate', 'CustId', 'IBCWinloss', 'IBCTurnover', 'BetCount']]
        yourdata['UserWinloss'] = - yourdata['IBCWinloss']
        yourdata.rename(columns = {'CustId':'C'}, inplace = True)
        return yourdata

    @staticmethod
    def build_column_Category_ID(data, str_to_id, is_day_eliminated, is_live_indicator_eliminated, is_bettype_eliminated):
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
        return mydata

    @staticmethod   
    def preprocess_data(data, str_to_id, is_training, is_aggregated, dead_line, is_day_eliminated, min_bet_count,
                         is_live_indicator_eliminated, is_bettype_eliminated,):

        yourdata = Data_Preprocessing_Manager.prepare_data(data)
        mydata = Data_Preprocessing_Manager.build_column_Category_ID(data, str_to_id, is_day_eliminated, 
                                                                    is_live_indicator_eliminated, is_bettype_eliminated)
        merged = pd.merge(yourdata, mydata, right_index = True, left_index = True)

        if is_training:
            phase = "Training"
        else:
            phase = "Testing"

        if is_aggregated:            
            positive_winloss = merged[merged.UserWinloss > 0]
            positive_merger = Data_Preprocessing_Manager.aggregate(positive_winloss, winloss_sign = "Positive", phase = phase)            
            negative_winloss = merged[merged.UserWinloss < 0]
            negative_merger = Data_Preprocessing_Manager.aggregate(negative_winloss, winloss_sign = "Negative", phase = phase)
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
            the_finalized = the_finalized[the_finalized[phase + "BetCount"] >= min_bet_count]
            print(phase + "ActiveDays = " + str(the_finalized[phase + "ActiveDays"].unique()))
        else:          
            the_finalized = merged.groupby(['C', 'CAT', 'ReportDate']).sum().reset_index()
            the_finalized = the_finalized[the_finalized["BetCount"] >= min_bet_count]
        return the_finalized