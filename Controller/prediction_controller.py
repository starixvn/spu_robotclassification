from scipy.stats import shapiro
from scipy.stats.distributions import norm
from Helper.utils import Utilities
from Model.distribution_model import DistributionModel
from DataAccess.database_interaction import DB_Interaction
from tqdm import tqdm
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

class PredictionController():

    def check_Gaussian_distribution(data, config):
        _, p = shapiro(data)
        if p > .05 :
            # print("Probably Gaussian")
            mean, std = norm.fit(data)
        else:
            # print("Probably not Gaussian")
            mean, std = config.default_mean, config.default_std
        return mean, std

    def predict_for_a_singleton(today_mode, upper_bound, lower_bound):
        if today_mode >= upper_bound:
            win_lose_guess = 1
        elif today_mode <= lower_bound:
            win_lose_guess = 0
        return win_lose_guess
    
    def update_training_results_for_a_singleton(a, b, streak, today_margin, amplitude):
        delta_a, delta_b = Utilities.compute_deltas(streak, today_margin, amplitude)
        updated_a = a + delta_a
        updated_b = b + delta_b
        classifier = DistributionModel(0, 0, updated_a, updated_b)
        updated_mode = classifier.get_mode()
        if today_margin == 0:
            return updated_mode, a,b, streak
        else:
            updated_streak = today_margin / abs(today_margin)
            if streak*today_margin > 0:
                updated_streak = streak + updated_streak
            return updated_mode, updated_a, updated_b, updated_streak

    def validate_training_results(concat_df, config):
        collection_of_boundaries = {}
        remove_list = []
        cat_list = concat_df.CAT.to_list()
        for cat_id in cat_list:
            df = concat_df[concat_df.CAT == cat_id]
            if len(df.index) <= 3:
                remove_list.append(cat_id)
                continue
            mean, std = PredictionController.check_Gaussian_distribution(df['M'], config)
            upper_bound = mean + std
            lower_bound = mean - std
            collection_of_boundaries[cat_id] = {"upper_bound":upper_bound, "lower_bound":lower_bound}
        concat_df = concat_df[~ concat_df.CAT.isin(remove_list)]
        return collection_of_boundaries, concat_df

    def validate_predictable_mode(mode, category, collection_of_boundaries):
        upper_bound = collection_of_boundaries[category]['upper_bound']
        lower_bound = collection_of_boundaries[category]['lower_bound']
        if mode >= upper_bound or mode <= lower_bound:
            if mode >= upper_bound:
                return (1,1)
            else:
                return (1,0)
        else:
            return (0,0)

    def process_prediction_phase(collection_of_boundaries, concat_df, amplitude):
        concat_df['Today_Margin'] = concat_df['IBCWinloss']/concat_df['IBCTurnover']
        mydf = pd.DataFrame()
        mydf['C'] = concat_df['C']
        mydf['CAT'] = concat_df['CAT']
        mydf['AD'] = concat_df['AD'] + 1
        concat_df['temp_output1'] = concat_df.apply(lambda z : PredictionController.validate_predictable_mode(z['M'], z['CAT'], collection_of_boundaries), axis = 1)
        mydf['IP'] = concat_df['temp_output1'].apply(lambda z : z[0])
        mydf['IPW'] = concat_df['temp_output1'].apply(lambda z : z[1])
        concat_df['temp_output2'] = concat_df.apply(lambda z : PredictionController.update_training_results_for_a_singleton(z['SWD'], z['SLD'], z['STR'], z['Today_Margin'], amplitude), axis = 1)
        mydf['M'] = concat_df['temp_output2'].apply(lambda z : z[0])
        mydf['SWD'] = concat_df['temp_output2'].apply(lambda z : z[1])
        mydf['SLD'] = concat_df['temp_output2'].apply(lambda z : z[2])
        mydf['STR'] = concat_df['temp_output2'].apply(lambda z : int(z[3]))
        mydf['IPTW'] = concat_df['Today_Margin'].apply(lambda z : 1 if z > 0 else 0)
        # print("mydf\n", mydf)
        return mydf

    def make_predictions_right_after_training_phase(cat_cus_couple_dataframe, config, day):
        # cat_cus_couple_dataframe, config, day = args
        history_training_results_data = DB_Interaction.get_from_TrainingResults_table(cat_cus_couple_dataframe, config)
        # print("BEFORE | history_training_results_data\n", history_training_results_data.head())
        collection_of_boundaries, history_training_results_data = PredictionController.validate_training_results(history_training_results_data, config)
        # print("AFTER | history_training_results_data\n", history_training_results_data.head())
        mydf = pd.DataFrame()
        mydf['C'] = history_training_results_data['C']
        mydf['CAT'] = history_training_results_data['CAT']
        mydf['M'] = history_training_results_data['M']
        mydf['SWD'] = history_training_results_data['SWD']
        mydf['SLD'] = history_training_results_data['SLD']
        history_training_results_data['temp_output1'] = history_training_results_data.apply(lambda z : PredictionController.validate_predictable_mode(z['M'], z['CAT'], collection_of_boundaries), axis = 1)
        mydf['IP'] = history_training_results_data['temp_output1'].apply(lambda z : z[0])
        mydf['IPW'] = history_training_results_data['temp_output1'].apply(lambda z : z[1])
        predict_full_info_list_right_after_training = mydf.to_dict(orient = 'records')
        DB_Interaction.insert_to_PredictedResults_table(predict_full_info_list_right_after_training, day, config)

    def execute(test_data, config):
        # update_only_full_info_list, predictable_full_info_list = [], []
        num_days = test_data.ReportDate.unique()
        for day in tqdm(num_days, desc = "Prediction"):
            daily_test_data = test_data[test_data.ReportDate == day]
            daily_training_results_data = DB_Interaction.get_from_TrainingResults_table(daily_test_data, config)
            if len(daily_training_results_data.index) == 0:
                continue
            concat_df = daily_test_data.merge(daily_training_results_data, how = 'inner', left_on = ['C', 'CAT'], right_on = ['C', 'CAT'])
            collection_of_boundaries, concat_df = PredictionController.validate_training_results(concat_df, config)
            mydf = PredictionController.process_prediction_phase(collection_of_boundaries, concat_df, config.amplitude)
            # print("mydf\n", mydf.head())
            # has_duplicate = mydf.duplicated()
            # duplicates = mydf[has_duplicate]
            # if len(duplicates.index) > 0:
            #     print("duplicates\n", duplicates)
            predict_full_info_list = mydf.to_dict(orient = 'records')
            DB_Interaction.insert_to_PredictedResults_table(predict_full_info_list, day, config, right_after_prediction = 0)
            DB_Interaction.insert_to_TrainingResults_table(predict_full_info_list, day, config, is_training_phase = 0)
            # print(f"======================================{day} DONE=======================================")