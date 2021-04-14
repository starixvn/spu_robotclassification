from utils import is_weekend
from scipy import stats
import pandas as pd
from tqdm import tqdm

kinds = ['out','in','sequence']
cats = ['BC','TO','WL']
sports = ['s1','s2','other']
bets = ['b1','b3','b7','b8']
lives = ['L','NL']
days = ['WD','WE']

class TransformData():
    def __init__(self,dataframe):
        self.dataframe = dataframe
        self.active_days = dataframe.ReportDate.unique()

    def build_outline_of_customer_dict(self):
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
        customer_list = self.dataframe.CustId.unique()
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
    
    def generate_daily_stats_customer_based(self,example_day):
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
        example_df = self.dataframe[self.dataframe.ReportDate==example_day]
        for _,row in example_df.iterrows():
            cus,sport,bet,live = row['CustId'], 's'+str(row['SporttypeId']), 'b'+str(row['BettypeId']), row['IsLive']
            if bet not in bets:
                continue
            if sport not in sports:
                sport = 'other'
            bet_count,turn_over,win_loss = row['BetCount'],row['IBCTurnover'],row['IBCWinloss']
            if live:
                live = 'L'
            else:
                live = 'NL'
            if is_weekend(example_day):
                day = 'WE'
            else:
                day = 'WD'
            key = sport+bet+live+day 
            if cus not in daily_stats_cus_based:
                daily_stats_cus_based[cus] = {} 
            daily_stats_cus_based[cus][key+'BC'] = bet_count
            daily_stats_cus_based[cus][key+'TO'] = turn_over
            daily_stats_cus_based[cus][key+'WL'] = win_loss
        return daily_stats_cus_based
    
    def generate_daily_stats_category_based(self, daily_stats_cus_based):
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
    
    def transform(self):
        customers_dict = self.build_outline_of_customer_dict()
        for active_day in tqdm(self.active_days,desc='Preprocessing...'):
            daily_stats_cus_based = self.generate_daily_stats_customer_based(active_day)
            for customer,cats in daily_stats_cus_based.items():
                cats_list = list(cats.keys())
                bet_count = [cat for cat in cats_list if cat.endswith('BC')]
                turn_over = [cat for cat in cats_list if cat.endswith('TO')]
                bc_total = sum([cats[cat] for cat in bet_count])
                to_total = sum([cats[cat] for cat in turn_over])
                for cat,value in cats.items():
        
                    if cat.endswith('BC'):
                        customers_dict[customer][cat.replace('BC','')+'_num_active_days'] += .5
                        customers_dict[customer][cat+'_in'] += value/to_total
                        customers_dict[customer][cat+'_sequence'] += ','+str(value)
                    elif cat.endswith('TO'):
                        customers_dict[customer][cat.replace('TO','')+'_num_active_days'] += .5
                        customers_dict[customer][cat+'_in'] += value/bc_total
                        customers_dict[customer][cat+'_sequence'] += ','+str(value)
                    else:
                        customers_dict[customer][cat+'_accummulated'] += value
                        customers_dict[customer][cat+'_sequence'] += ','+str(value)

            daily_stats_cat_based = self.generate_daily_stats_category_based(daily_stats_cus_based)
            for attribute,cus in daily_stats_cat_based.items():  
                for customer,value in cus.items():
                    if attribute.endswith('BC'):
                        stat_of_bet_count_in_a_day = list(cus.values())
                        customers_dict[customer][attribute+'_out'] += stats.percentileofscore(stat_of_bet_count_in_a_day,value)/100
                        # customers_dict[customer][attribute+'_sequence'] += ','+str(value)

                    elif attribute.endswith('TO'):
                        stat_of_turnover_in_a_day = list(cus.values())
                    
                        customers_dict[customer][attribute+'_out'] += stats.percentileofscore(stat_of_turnover_in_a_day,value)/100
                        # customers_dict[customer][attribute+'_sequence'] += ','+str(value)
                    # else:
                    #     customers_dict[customer][attribute+'_accummulated'] += value
                    #     customers_dict[customer][attribute+'_sequence'] += ','+str(value)
        features_df = pd.DataFrame(customers_dict.values(),index=customers_dict.keys())
        print('Features\n',features_df.head(5))
        features_df.to_csv("D:/Project/Formula_BET/SaveData/PreprocessedData/preprocessed.csv")
        df = pd.read_csv("D:/Project/Formula_BET/SaveData/PreprocessedData/preprocessed.csv",index_col=0)
        print('df\n',df.head(5))