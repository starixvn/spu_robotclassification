import numpy as np
import pandas as pd
from GB_classify import GB_classify
from datetime import date

def filter_categorie(categorie,dataframe):
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

def compute_deltas(margin,streak,amplitude=10.):
    """
    >>> Input   :   margin      , a float number in range[-1,1]
                    streak      , an integer
    >>> Output  :   delta_a     , a float number
                    delta_b     , a float number
    """
    if margin > 0:
        return amplitude*margin*streak,0
    else:
        return 0,amplitude*abs(margin)*streak

def process(margin_array,split=.0):
    """
    Process profile for a single customer
    Also apply winning/losing streak !
    >>> Input   :   margin_array  , a numpy array containing margin versus days of a customer
                    split         , a float how much percent of array used to establish prior
    
    >>> Output  :   mode          , a float number tells the value of peak of beta distribution
                    std           , a float number tells the standard deivation
    """
    num_effective_days = len(margin_array)
    streak = 1
    split_point = int(np.floor(split*num_effective_days))
    history,present = margin_array[:split_point],margin_array[split_point:]
    m,l = len(history[history>0]),len(history[history<0])
    cus = GB_classify(m,l)
    delta_a,delta_b = compute_deltas(margin_array[0],1)
    cus.update_hyper_params(delta_a,delta_b)
    for day in range(1,len(present)):
        if margin_array[day]*margin_array[day-1] > 0:
            streak += 1
            delta_a,delta_b = compute_deltas(margin_array[day],streak)
            cus.update_hyper_params(delta_a,delta_b)
        else:
            streak = 1
            delta_a,delta_b = compute_deltas(margin_array[day],streak)
            cus.update_hyper_params(delta_a,delta_b)
    mode,std = cus.get_mode(),cus.get_std()
    return mode,std

def is_weekend(a_given_date):
    """
    Simply check a given date is if it is weekend

    >>> Input   :   a_given_date    : string | format YYYY-MM-DD

    >>> Output  :   True or False
    """
    year_month_day = a_given_date.split('-')
    year,month,day = year_month_day[0],year_month_day[1],year_month_day[2]
    my_day = date(int(year),int(month),int(day)).weekday()
    if my_day >= 5:
        return True
    else:
        return False

def create_peak_std_df(categorie,cat_df,threshold_activ_days=4,split=.0):
    """
    Compute mode and standard deviation for each customer with a given dataset

    >>> Input   :   categorie             , string
                    cat_df                , dataframe of a certain categorie
                    threshold_activ_days  , integer that reflects the minimal number of days to filter
                    split                 , float that reflects how much percent of array used to establish prior
    
    >>> Output  :   all_draw_num          , number of customer with all results are draw
                    too_few_num           , number of customer whose number active days < threshold_activ_days
                    peak_std_dict         , dictionary whose key is custid , value is peak and std of its distribution
                    peak_std_df           , dataframe of peak_std_dict
    """
    peak_std_dict,all_draw_num,too_few_num = {},0,0
    for custid in cat_df.index:
        turn_over_sequence = cat_df.loc[custid,categorie+'TO_sequence']
        win_loss_sequence = cat_df.loc[custid,categorie+'WL_sequence']
        turn_over_array = np.array([float(x) for x in turn_over_sequence.split(',') if x != ''])
        win_loss_array = np.array([float(x) for x in win_loss_sequence.split(',') if x != ''])
        margin_array = win_loss_array / turn_over_array

        # round 1 filter
        filtered_margin_array =  margin_array[margin_array != 0]

        # round 2 filter
        if len(filtered_margin_array) >= threshold_activ_days :
            peak,std = process(filtered_margin_array,split = split)
            peak_std_dict[custid] = {'peak' : peak,'std' : std}
        else:
            if len(filtered_margin_array) < 1:
                all_draw_num += 1
            else:
                too_few_num += 1
    
    return all_draw_num,too_few_num,peak_std_dict,pd.DataFrame(peak_std_dict.values(),index=peak_std_dict.keys())