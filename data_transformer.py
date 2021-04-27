# from unicodedata import category
# from utils import Utilities
# from training_model_controller import DataTransformer
from scipy import stats
import pandas as pd
from tqdm import tqdm

kinds = ['out','in','sequence']
cats = ['BC','TO','WL']
sports = ['s1','s2','other']
bets = ['b1','b3','b7','b8']
lives = ['L','NL']
days = ['WD','WE']

class DataTransformer():

    def build_outline_of_customer_dict(customer_list):
        """
        Build a customer-based dictionary to update scores during processing
        >>> Output  :   customers_dict  , Python dictionary whose format looks like {31340:{'s1b1LWDTO_in':.89,'s1b1LWDTO_out':.75,
                                                                                            's1b1LWDTO_sequence':',3.2,-95.8','s1b1LWDTO_accummulate':300
                                                                                            },
                                                                                    .
                                                                                    .
                                                                                    .
                                                                                    }
        """
        customers_dict = {}
        for customer in customer_list:
            customers_dict[customer] ={}
            for day in days:
                for sport in sports:
                    for bet in bets:
                        for live in lives:
                            customers_dict[customer][sport+bet+live+day+'_num_active_days'] = 0
                            for kind in kinds:
                                for cat in cats:
                                    if kind=='sequence':
                                        customers_dict[customer][sport+bet+live+day+cat+'_'+kind] = ''
                                    else:
                                        if cat=='WL':
                                            customers_dict[customer][sport+bet+live+day+cat+'_accummulated'] = 0
                                        else:
                                            customers_dict[customer][sport+bet+live+day+cat+'_'+kind] = 0
        return customers_dict

    def generate_daily_stats_customer_based(dataframe, example_day):
        """
        For a single day, build a dictionary whose parent keys are customers
        This kind of dictionary is helpful to calculcate INTERNAL SCORE
        >>> Input   :   example_day , string

        >>> Output  :   daily_stats_cus_based , Python dictionary whose format looks like   {   31340   :{'s1b1LWDBC':15    ,'s1b3LNWETO':300,...},
                                                                                                468016  :{'s1b1LWDBC':25    ,'s1b3LNWETO':500,...} ,
                                                                                            .
                                                                                            .
                                                                                            .
                                                                                            }
        """
        daily_stats_cus_based = {}
        example_df = dataframe[dataframe.ReportDate == example_day]
        for row in example_df.itertuples():
            custid = row.C
            category = row.SporttypeId + row.BettypeId + row.IsLive + row.Day
            if custid not in daily_stats_cus_based:
                daily_stats_cus_based[custid] = {} 
            daily_stats_cus_based[custid][category + 'BC'] = row.BetCount
            daily_stats_cus_based[custid][category + 'TO'] = row.IBCTurnover
            daily_stats_cus_based[custid][category + 'WL'] = row.IBCWinloss
        return daily_stats_cus_based
    
    def generate_daily_stats_category_based(daily_stats_cus_based):
        """
        Build a dictionary whose parent keys are categories
        This kind of dictionary is helpful to calculate OUTSTANDING SCORE

        >>> Input   :   daily_stats_cus_based   ,   Python dictionary whose format looks like   {   31340   :{'s1b1LWDBC':15    ,'s1b3LNWETO':300,...},
                                                                                                    468016  :{'s1b1LWDBC':25    ,'s1b3LNWETO':500,...} ,
                                                                                                .
                                                                                                .
                                                                                                .
                                                                                                }

        >>> Output  :   daily_stats_cat_based   ,   Python dictionary whose format looks like   {   's1b1LWDBC' :{31340:15  ,468016:25,...},
                                                                                                    's1b3LNWETO':{31340:300 ,468016:500},
                                                                                                    .
                                                                                                    .
                                                                                                    .
                                                                                                }
        """
        daily_stats_cat_based = {}
        for cus,attributes in daily_stats_cus_based.items():
            for attribute,value in attributes.items():
                if attribute not in daily_stats_cat_based:
                    daily_stats_cat_based[attribute] = {}
                    daily_stats_cat_based[attribute][cus] = value
                else:
                    daily_stats_cat_based[attribute][cus] = value
        return daily_stats_cat_based

    def compute_internal_score(daily_stats_cus_based, customers_dict):
        for customer, cats in daily_stats_cus_based.items():
            bc_total = sum([cats[cat] for cat in cats.keys() if cat.endswith('BC')])
            to_total = sum([cats[cat] for cat in cats.keys() if cat.endswith('TO')])
            for cat,value in cats.items():
                customers_dict[customer][cat[:-2] + '_num_active_days'] += 1/3    
                if cat.endswith('BC'):
                    customers_dict[customer][cat + '_in'] += value/bc_total
                    customers_dict[customer][cat + '_sequence'] += ','+str(value)
                elif cat.endswith('TO'):
                    customers_dict[customer][cat + '_in'] += value/to_total
                    customers_dict[customer][cat + '_sequence'] += ','+str(value)
                else:
                    customers_dict[customer][cat + '_accummulated'] += value
                    customers_dict[customer][cat + '_sequence'] += ','+str(value)
        return customers_dict
    
    def compute_outstanding_score(daily_stats_cat_based, customers_dict):
        for attribute,cus in daily_stats_cat_based.items():  
            for customer,value in cus.items():
                if attribute.endswith('BC'):
                    stat_of_bet_count_in_a_day = list(cus.values())
                    customers_dict[customer][attribute+'_out'] += stats.percentileofscore(stat_of_bet_count_in_a_day, value)/100
                elif attribute.endswith('TO'):
                    stat_of_turnover_in_a_day = list(cus.values())
                
                    customers_dict[customer][attribute+'_out'] += stats.percentileofscore(stat_of_turnover_in_a_day, value)/100
        return customers_dict

    def transform(dataframe):
        active_days = dataframe.ReportDate.unique()
        customer_list = dataframe.C.unique()
        customers_dict = DataTransformer.build_outline_of_customer_dict(customer_list)
        for active_day in tqdm(active_days, desc = 'Preprocessing...'):

            daily_stats_cus_based = DataTransformer.generate_daily_stats_customer_based(dataframe, active_day)

            DataTransformer.compute_internal_score(daily_stats_cus_based, customers_dict)

            daily_stats_cat_based = DataTransformer.generate_daily_stats_category_based(daily_stats_cus_based)

            customers_dict = DataTransformer.compute_outstanding_score(daily_stats_cat_based, customers_dict)

        features_df = pd.DataFrame(customers_dict.values(), index = customers_dict.keys())
        print('Features\n',features_df.head(5))
        return features_df
        