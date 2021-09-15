import pandas as pd
from Utilities.Data_Preprocessing_Manager import Data_Preprocessing_Manager
class Category_Mapping_Manager():

    def transform_category_mapping(data, is_day_eliminated = 0, is_live_indicator_eliminated = 0, is_bettype_eliminated = 0):
        data = data.set_index('CategoryID')
        mydata = pd.DataFrame()
        mydata['SportID'] = data['SportID'].apply(Data_Preprocessing_Manager.transform_sport_type) # mydata['SporttypeId']
        if is_day_eliminated and is_live_indicator_eliminated and is_bettype_eliminated:
            mydata['Category_in_short'] = mydata['SportID']
        elif is_day_eliminated and is_live_indicator_eliminated:
            mydata['BettypeID'] = data['BettypeID'].apply(Data_Preprocessing_Manager.transform_bet_type) # mydata['BettypeId'
            mydata['Category_in_short'] = mydata['SportID'] + mydata['BettypeID']
        elif is_day_eliminated:
            mydata['BettypeID'] = data['BettypeID'].apply(Data_Preprocessing_Manager.transform_bet_type) # mydata['BettypeId'
            mydata['IsLive'] = data['IsLive'].apply(lambda x : 'L' if x else 'NL') # mydata['IsLive']
            mydata['Category_in_short'] = mydata['SportID'] + mydata['BettypeID'] + mydata['IsLive']
        else:
            mydata['BettypeID'] = data['BettypeID'].apply(Data_Preprocessing_Manager.transform_bet_type) # mydata['BettypeId'
            mydata['IsLive'] = data['IsLive'].apply(lambda x : 'L' if x else 'NL') # mydata['IsLive']
            mydata['Day'] = data['IsWeekend'].apply(lambda x : "WE" if x else "WD") # mydata['Day']
            mydata['Category_in_short'] = mydata['SportID'] + mydata['BettypeID'] + mydata['IsLive'] + mydata['Day']
        mydata1 = mydata[['Category_in_short']].reset_index().set_index('Category_in_short')
        # print("mydata\n", mydata)
        mydata2 = mydata[['Category_in_short']]
        str_to_id = mydata1.to_dict(orient = 'index')
        id_to_str = mydata2.to_dict(orient = 'index')
        return str_to_id, id_to_str