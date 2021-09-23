from Utilities.File_Manager import File_Manager
from scipy.stats import shapiro
from scipy.stats.distributions import norm
from sklearn.metrics import accuracy_score
from Model.distribution_model import DistributionModel
from Utilities.BColors import BColors
from DataAccess.DataAccessConnection import spu_aiml, cts_datacenter
from DataAccess.Model.SPU_AIML.SPU_GetTrainResultsDAModel import SPU_GetTrainResultsDAModel
from DataAccess.Model.SPU_AIML.SPU_InsertWinlossPredictionDAModel import SPU_InsertWinlossPredictionDAModel
from DataAccess.Model.CTS_DataCenter.CTS_InsertRobotClassificationDAModel import CTS_InsertRobotClassificationDAModel
from DataAccess.DataAccessConnection import DataAccessConnection
from DataAccess.CoreDA.BaseDA import BaseDA
from tqdm import tqdm
import pandas as pd
import json
import warnings
import datetime
warnings.filterwarnings("ignore")

import random
class PredictionController():

    def check_Gaussian_distribution(data, config):
        if config.is_hard_classified:
            mean, std = config.default_mean, config.default_std
        else:
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
    
    @staticmethod
    def is_prediction_wrong(train_nega_wl, test_nega_wl, train_posi_wl, test_posi_wl,
                            mode, wl, winning_threshold):
        if (mode - winning_threshold)*wl < 0 :
            if (wl > 0 and test_posi_wl >= abs(train_nega_wl)) or \
                (wl < 0 and abs(test_nega_wl) >= train_posi_wl):
                return 1
            else:
                return 0
        else:
            return 0
    
    @staticmethod
    def is_truth_win_after_consideration(is_predict_win, is_prediction_wrong):
        if is_prediction_wrong:
            return 1 - is_predict_win
        else:
            return is_predict_win


    def process_prediction_phase(concat_df, PID, winning_threshold, is_raw, amplitude = 1, collection_of_boundaries = None):
        # concat_df['Today_Margin'] = concat_df['TestingUserWinloss']/concat_df['IBCTurnover']
        concat_df['STR'] = 1
        mydf = pd.DataFrame()
        mydf['C'] = concat_df['C']
        mydf['CAT'] = concat_df['CAT']
        # mydf['AD'] = concat_df['AD'] + 1
        # concat_df['temp_output1'] = concat_df.apply(lambda z : PredictionController.validate_predictable_mode(z['M'], z['CAT'], collection_of_boundaries), axis = 1)
        mydf['IP'] = 0 #concat_df['temp_output1'].apply(lambda z : z[0])
        mydf['IPW'] = concat_df["IPW"] # concat_df['temp_output1'].apply(lambda z : z[1])
        # mydf['IPW'] = concat_df['temp_output1'].apply(lambda z : random.randint(0,1))
        # concat_df['temp_output2'] = concat_df.apply(lambda z : PredictionController.update_training_results_for_a_singleton(z['SWD'], z['SLD'], z['STR'], z['Today_Margin'], amplitude), axis = 1)
        mydf['M'] = 0.5  # concat_df['temp_output2'].apply(lambda z : z[0])
        mydf['SWD'] = concat_df["TestingPositiveWinlossPerDay"]  # concat_df['temp_output2'].apply(lambda z : z[1])
        mydf['SLD'] = concat_df["TestingNegativeWinlossPerDay"] #concat_df['temp_output2'].apply(lambda z : z[2])
        mydf['STR'] = 1 # concat_df['temp_output2'].apply(lambda z : int(z[3]))
        if is_raw:
            mydf["IPTW"] = concat_df["TestingUserWinloss"].apply(lambda z: 1 if z > 0 else 0)
        else:
            print("CONSIDERATION HAS BEEN AVAILABLE !!!!")
            mydf['IsPredictionWrong'] = concat_df.apply(lambda z : PredictionController.is_prediction_wrong(
                                                                                                    z['SLD']
                                                                                                    ,z['TestingNegativeWinlossPerDay']
                                                                                                    ,z['SWD']
                                                                                                    ,z['TestingPositiveWinlossPerDay']
                                                                                                    ,z['M']
                                                                                                    ,z['TestingUserWinloss']
                                                                                                    ,winning_threshold
                                                                                                    ),
                                                axis = 1)
            mydf["IPTW"] = mydf.apply(lambda z : PredictionController.is_truth_win_after_consideration(z["IPW"],
                                                                                                        z["IsPredictionWrong"]),
                                                                                                    axis = 1)
        y_true = mydf.IPTW
        y_pred = mydf.IPW
        mydf['PID'] = PID
        accuracy = accuracy_score(y_true, y_pred)
        print(str(BColors.WARNING) + "accuracy_score = " + str(accuracy) + str(BColors.ENDC))
        return mydf, accuracy
    
    def consolidate_classified_results(mydf):
        observed_robots = mydf[mydf.IP == 0]
        good_robots = mydf[(mydf.IP == 1) & (mydf.IPW == 0)]
        bad_robots = mydf[(mydf.IP == 1) & (mydf.IPW == 1)]
        return len(observed_robots), len(good_robots), len(bad_robots)

    def make_predictions_right_after_training_phase(cat_cus_couple_dataframe, config, day, PID): # result_of_the_day_before

        ### build from_Date, to_Date
        from_Date = day
        datetime_object = datetime.datetime.strptime(from_Date, '%Y-%m-%d')
        to_Date = datetime_object + datetime.timedelta(days = config.length_of_testing - 1)
        to_Date = to_Date.strftime('%Y-%m-%d')
        ### =============================

        cat_cus_couple_dataframe = cat_cus_couple_dataframe.drop_duplicates()
        get_objects = cat_cus_couple_dataframe[["C", "CAT"]].to_dict(orient = 'records')
        jsonList = json.dumps(get_objects)

        connection_spu = DataAccessConnection(spu_aiml)
        ip_param = SPU_GetTrainResultsDAModel(jsonList, PID)
        dba_results = BaseDA.execute("SPU_AIML_GetTrainResults", spu_aiml, ip_param, connection_spu)
        df = pd.DataFrame(dba_results[0], columns = ['C', 'CAT', 'M', 'SWD', 'SLD', 'STR', 'AD'])
        df['M'] = df['M'].astype(float)
        df['SWD'] = df['SWD'].astype(float)
        df['SLD'] = df['SLD'].astype(float)
        history_training_results_data = df
        # print("BEFORE | sub_test_data\n", sub_test_data.head())
        # history_training_results_data.to_csv(config.transformed_data_folder + "history_training_results_data.csv", index = False)
        will_be_classified = history_training_results_data[history_training_results_data.AD >= config.day_threshold]
        not_be_eligible_for_classification = history_training_results_data[history_training_results_data.AD < config.day_threshold]
        not_be_eligible_for_classification = len(not_be_eligible_for_classification)
        # collection_of_boundaries, merged_df = PredictionController.validate_training_results(history_training_results_data, config)
        # print("AFTER | history_training_results_data\n", history_training_results_data.head())
        # history_training_results_data.to_csv(config.transformed_data_folder + "history_training_results_data.csv", index = False)
        merged_df = pd.merge(will_be_classified, cat_cus_couple_dataframe, on = ['C', 'CAT'], how = 'inner')
        
        mydf = pd.DataFrame()
        mydf['C'] = merged_df['C']
        mydf['CAT'] = merged_df['CAT']
        mydf['M'] = merged_df['M']
        mydf['SWD'] = merged_df['SWD']
        mydf['SLD'] = merged_df['SLD']
        # merged_df['temp_output1'] = merged_df.apply(lambda z : PredictionController.validate_predictable_mode(z['M'], z['CAT'], collection_of_boundaries), axis = 1)
        # mydf['IP'] = merged_df['temp_output1'].apply(lambda z : z[0])
        winning_threshold = config.default_mean + config.default_std
        print("HEAD of merged_df\n",merged_df.head(3))
        if config.observed_mode:
            mydf['IP'] = merged_df.apply(lambda z : 1 if (z["M"] - winning_threshold)*z["AccWL"] > 0 else 0, axis = 1)
        else:
            mydf['IP'] = merged_df.apply(lambda z : 1 if z["M"] > winning_threshold or z["M"] < 1 - winning_threshold \
                                        else 0, axis = 1)
        # mydf['IPW'] = merged_df['temp_output1'].apply(lambda z : z[1])
        mydf['IPW'] = merged_df['M'].apply(lambda z : 1 if z >= winning_threshold else 0)
        # mydf['IPTW'] = merged_df['UserWinloss']
        mydf['PID'] = PID
        mydf['FD'] = from_Date
        mydf['TD'] = to_Date
        ### =========================================================================================
        observed, good, bad = PredictionController.consolidate_classified_results(mydf)
        ### =========================================================================================
        # if not config.is_test_insert_CTS:
        data_SPU = mydf[["C", "CAT", "M", "SWD", "SLD", "IP", "IPW", "PID"]]
        predict_full_info_list_right_after_training = data_SPU.to_dict(orient = 'records')
        chunks = [predict_full_info_list_right_after_training[x:x + config.chunk_size] for x in \
                    range(0, len(predict_full_info_list_right_after_training), config.chunk_size)]
        if config.insert_to_aiml:
            for chunk in chunks:
                chunk = json.dumps(chunk)
                ip_param = SPU_InsertWinlossPredictionDAModel(chunk, day)
                dba_results = BaseDA.execute("SPU_AIML_InsertWinlossPrediction", spu_aiml, ip_param, connection_spu)
        ### =========================================================================================

        ### =========================================================================================
        data_CTS = mydf[["C", "CAT", "FD", "TD", "IP", "IPW"]]
        data_CTS = data_CTS.rename(columns={"CAT":"CID"})
        predict_full_info_list_right_after_training = data_CTS.to_dict(orient = 'records')
        chunks = [predict_full_info_list_right_after_training[x:x + config.chunk_size] for x in \
                    range(0, len(predict_full_info_list_right_after_training), config.chunk_size)]
        connection_cts = DataAccessConnection(cts_datacenter)
        if config.insert_to_cts:
            for chunk in chunks:
                chunk = json.dumps(chunk)
                ip_param = CTS_InsertRobotClassificationDAModel(chunk)
                dba_results = BaseDA.execute("CTS_DC_RobotClassification_Insert", cts_datacenter, ip_param, connection_cts)
        ### =========================================================================================

        return data_SPU, not_be_eligible_for_classification, observed, good, bad, len(data_CTS)

    def get_answer_from_test_data(test_data, config, PID, test_date):
        # print("prediction_results\n", prediction_results.head())
        # num_days = test_data.ReportDate.unique()
        file_name = str(PID) + ".csv"
        prediction_results = File_Manager.read_data(config.prediction_results_folder, file_name, is_entire = 1)
        concat_df = test_data.merge(prediction_results, how = 'inner', left_on = ['C', 'CAT'], right_on = ['C', 'CAT'])
        concat_df = concat_df[concat_df.IP == 1]
        print("concat_df = " + str(concat_df.shape))
        # collection_of_boundaries, concat_df = PredictionController.validate_training_results(test_data, config)
        answers, accuracy = PredictionController.process_prediction_phase(concat_df, PID, 
                                                                            config.default_mean + config.default_std, config.is_raw)
        print("answers\n", answers.head())
        print("answers = " + str(answers.shape))                                                                
        answers_full_info_list = answers.to_dict(orient = 'records')
        # DB_Interaction.insert_to_PredictedResults_table(answer_and_next_prediction_full_info_list, test_date, config, right_after_prediction = 0)
        # DB_Interaction.insert_to_TrainingResults_table(predict_full_info_list, day, config, is_training_phase = 0)
        # print(f"======================================{day} DONE=======================================")
        # print("concat_df\n", concat_df.head())
        # print("Number of C-CAT\n", concat_df.groupby(["C", "CAT"]).first().reset_index().shape)
        # answers.to_csv(f"D:/Project/Robot/TRANSFORMED_DATA/accuracy_testing.csv", index = False)
        chunks = [answers_full_info_list[x:x + config.chunk_size] for x in \
                    range(0, len(answers_full_info_list), config.chunk_size)]
        # DB_Interaction.insert_to_PredictedResults_table(predict_full_info_list_right_after_training, day, config)
        # print("mydf\n", mydf.head())

        connection_spu = DataAccessConnection(spu_aiml)
        if config.insert_to_aiml:
            for chunk in chunks:
                print("LENGTH OF CHUNK = " + str(len(chunk)))
                chunk = json.dumps(chunk)
                ip_param = SPU_InsertWinlossPredictionDAModel(chunk, test_date)
                BaseDA.execute("SPU_AIML_InsertWinlossPrediction", spu_aiml, ip_param, connection_spu)
        return accuracy