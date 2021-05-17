from scipy.stats import shapiro
from scipy.stats.distributions import norm
from Helper.utils import Utilities
from Model.distribution_model import DistributionModel
from DataAccess.database_interaction import DB_Interaction
from tqdm import tqdm
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

import random
class PredictionController():

    def check_Gaussian_distribution(data, config):
        # _, p = shapiro(data)
        # if p > .05 :
        #     # print("Probably Gaussian")
        #     mean, std = norm.fit(data)
        # else:
        #     # print("Probably not Gaussian")
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
            try:
                updated_streak = int(today_margin / abs(today_margin))
                if streak*today_margin > 0:
                    updated_streak = streak + updated_streak
                return updated_mode, updated_a, updated_b, updated_streak
            except ValueError:
                print("today_margin", today_margin)

    def validate_training_results(concat_df, robotConfig):
        collection_of_boundaries = {}
        remove_list = []
        cat_list = concat_df.CAT.to_list()
        for cat_id in cat_list:
            df = concat_df[concat_df.CAT == cat_id]
            if len(df.index) <= 3:
                remove_list.append(cat_id)
                continue
            mean, std = PredictionController.check_Gaussian_distribution(df['M'], robotConfig)
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

    def process_prediction_phase(collection_of_boundaries, concat_df, amplitude, PID):
        concat_df['Today_Margin'] = concat_df['UserWinloss']/concat_df['IBCTurnover']
        concat_df['STR'] = 1
        mydf = pd.DataFrame()
        mydf['C'] = concat_df['C']
        mydf['CAT'] = concat_df['CAT']
        # mydf['AD'] = concat_df['AD'] + 1
        concat_df['temp_output1'] = concat_df.apply(lambda z : PredictionController.validate_predictable_mode(z['M'], z['CAT'], collection_of_boundaries), axis = 1)
        mydf['IP'] = concat_df['temp_output1'].apply(lambda z : z[0])
        mydf['IPW'] = concat_df['temp_output1'].apply(lambda z : z[1])
        # mydf['IPW'] = concat_df['temp_output1'].apply(lambda z : random.randint(0,1))
        concat_df['temp_output2'] = concat_df.apply(lambda z : PredictionController.update_training_results_for_a_singleton(z['SWD'], z['SLD'], z['STR'], z['Today_Margin'], amplitude), axis = 1)
        mydf['M'] = concat_df['temp_output2'].apply(lambda z : z[0])
        mydf['SWD'] = concat_df['temp_output2'].apply(lambda z : z[1])
        mydf['SLD'] = concat_df['temp_output2'].apply(lambda z : z[2])
        mydf['STR'] = concat_df['temp_output2'].apply(lambda z : int(z[3]))
        mydf['IPTW'] = concat_df['Today_Margin'].apply(lambda z : 1 if z > 0 else 0)
        mydf['PID'] = PID
        # print("mydf\n", mydf)
        return mydf

    def make_predictions_right_after_training_phase(cat_cus_couple_dataframe, config, day, PID): # result_of_the_day_before
        # sub_test_data = test_data[['C', 'CAT', 'UserWinloss']]
        # sub_test_data['UserWinloss'] = sub_test_data['UserWinloss'].apply(lambda z : 1 if z > 0 else 0)
        # cat_cus_couple_dataframe, config, day = args
        history_training_results_data = DB_Interaction.get_from_TrainingResults_table(cat_cus_couple_dataframe, config, PID)
        # print("BEFORE | sub_test_data\n", sub_test_data.head())
        # history_training_results_data.to_csv(config.transformed_data_folder + "history_training_results_data.csv", index = False)
        collection_of_boundaries, merged_df = PredictionController.validate_training_results(history_training_results_data, config)
        # print("AFTER | history_training_results_data\n", history_training_results_data.head())
        # history_training_results_data.to_csv(config.transformed_data_folder + "history_training_results_data.csv", index = False)
        # merged_df = pd.merge(history_training_results_data, sub_test_data, on = ['C', 'CAT'], how = 'left')
        # merged_df = pd.merge(result_of_the_day_before, sub_test_data, on = ['C', 'CAT'])
        # answer = merged_df.to_dict(orient = 'records')
        # DB_Interaction.insert_to_PredictedResults_table(answer, day, config)
        # merged_df.to_csv(config.transformed_data_folder + "diego1.csv", index=False)
        # print("make_predictions_right_after_training_phase | merged_df\n", merged_df.head(), "merged_df shape" + str(merged_df.shape), sep = "\n")
        # merged_df['UserWinloss'].fillna(0, inplace=True)
        mydf = pd.DataFrame()
        mydf['C'] = merged_df['C']
        mydf['CAT'] = merged_df['CAT']
        mydf['M'] = merged_df['M']
        mydf['SWD'] = merged_df['SWD']
        mydf['SLD'] = merged_df['SLD']
        merged_df['temp_output1'] = merged_df.apply(lambda z : PredictionController.validate_predictable_mode(z['M'], z['CAT'], collection_of_boundaries), axis = 1)
        mydf['IP'] = merged_df['temp_output1'].apply(lambda z : z[0])
        mydf['IPW'] = merged_df['temp_output1'].apply(lambda z : z[1])
        # mydf['IPTW'] = merged_df['UserWinloss']
        mydf['PID'] = PID
        # history_training_results_data['temp_output1'] = history_training_results_data.apply(lambda z : PredictionController.validate_predictable_mode(z['M'], z['CAT'], collection_of_boundaries), axis = 1)
        # history_training_results_data['IP'] = history_training_results_data['temp_output1'].apply(lambda z : z[0])
        # history_training_results_data['IPW'] = history_training_results_data['temp_output1'].apply(lambda z : z[1])
        # history_training_results_data['IPTW'] = history_training_results_data['UserWinloss']
        # history_training_results_data['PID'] = PID
        predict_full_info_list_right_after_training = mydf.to_dict(orient = 'records')
        DB_Interaction.insert_to_PredictedResults_table(predict_full_info_list_right_after_training, day, config)
        # print("mydf\n", mydf.head())
        return mydf

    def get_answer_from_test_data(test_data, config, PID, test_date, prediction_results):
        print("prediction_results\n", prediction_results.head())
        num_days = test_data.ReportDate.unique()
        for day in tqdm(num_days, desc = "Prediction"):
            daily_test_data = test_data[test_data.ReportDate == day]
            # print("daily_test_data\n", daily_test_data.head())
            concat_df = daily_test_data.merge(prediction_results, how = 'inner', left_on = ['C', 'CAT'], right_on = ['C', 'CAT'])
            # print("concat_df\n", concat_df.head())
            collection_of_boundaries, concat_df = PredictionController.validate_training_results(concat_df, config)
            answer_and_next_prediction = PredictionController.process_prediction_phase(collection_of_boundaries, concat_df, config.amplitude, PID)
            answer_and_next_prediction_full_info_list = answer_and_next_prediction.to_dict(orient = 'records')
            DB_Interaction.insert_to_PredictedResults_table(answer_and_next_prediction_full_info_list, test_date, config, right_after_prediction = 0)
            # DB_Interaction.insert_to_TrainingResults_table(predict_full_info_list, day, config, is_training_phase = 0)
            # print(f"======================================{day} DONE=======================================")