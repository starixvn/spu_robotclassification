import os
from Helper.utils import Utilities
from Helper.data_transformer import DataTransformer
from Controller.training_model_controller import TrainingModelController
from Controller.prediction_controller import PredictionController
from configuration.system_config import SystemConfig
from DataAccess.database_interaction import DB_Interaction
from Helper.notify import Telegram_send_message
import logging
import time
from datetime import datetime

ENV = 'LOCAL'
config = SystemConfig(ENV.lower() + '_' + "config.ini", ENV)
logging.basicConfig(filename = config.save_dir_log + config.log_name, level = logging.INFO)
agree_to_send_message = config.agree_to_send_message

class RobotClassificationManager():

    def start(PID, land_mark, released_answer_date):
        try:
            start_running = time.time()
            now = datetime.now()
            current_time = now.strftime("%d/%m/%Y %H:%M:%S")
            message = "%s | Robot Classfication has just started" % ENV
            print(f"========================================= PID = {PID} | {current_time} | Predict for {land_mark} =====================================================================")
            print(f"========================================= released_answer_date {released_answer_date} =====================================================================")
            print(message)
            logging.info(f"========================================= PID = {PID} | {current_time} | Predict for {land_mark} =====================================================================")
            logging.info(f"========================================= released_answer_date {released_answer_date} =====================================================================")
            logging.info(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            return start_running
        except Exception as e:
            message = "%s | start | %s : %s" % (ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
        
    
    def transform_category_mapping(is_day_eliminated = 0):
        # try:
            start = time.time()
            if is_day_eliminated:
                category_mapping = Utilities.read_data(config.category_mapping_folder, config.day_eliminated_category_mapping_file_name)
            else:
                category_mapping = Utilities.read_data(config.category_mapping_folder, config.category_mapping_file_name)
            str_to_id, id_to_str = Utilities.transform_category_mapping(category_mapping, is_day_eliminated)
            message = "%s | transform_category_mapping %.2f seconds" % (ENV, time.time() - start)
            print(message)
            logging.info(message)
            return str_to_id, id_to_str
        # except Exception as e:
        #     message = "%s | transform_category_mapping | %s : %s" % (ENV, type(e).__name__, e.args)
        #     print(message)
        #     logging.error(message)
        #     if agree_to_send_message:
        #         Telegram_send_message(message)
        #     raise ValueError
    
    def read_and_preprocess_data(str_to_id, is_training, is_entire = 1, start_date = None, is_aggregated = 0, is_day_eliminated = 0):
        try:
            start = time.time()
            if is_training:
                if is_entire:
                    data = Utilities.read_data(config.train_data_folder, config.train_data_file_name, is_entire, config.length_of_training, start_date)
                else:
                    data = Utilities.read_data(config.train_data_folder_with_breaking_files, config.train_data_file_name, is_entire, config.length_of_training, start_date)
                bench_mark_date = data.ReportDate.max()      
                data = Utilities.preprocess_data(data, str_to_id, min_bet_count = config.min_bet_count_training, is_day_eliminated = is_day_eliminated) 
                print("Train data\n", data.tail())       
            else:
                if is_entire:
                    data = Utilities.read_data(config.test_data_folder, config.test_data_file_name, is_entire, config.length_of_testing, start_date)
                else:
                    data = Utilities.read_data(config.test_data_folder_with_breaking_files, config.test_data_file_name, is_entire, config.length_of_testing, start_date)
                test_dead_line = data.ReportDate.max()
                # data = data[data.ReportDate <= test_dead_line]
                bench_mark_date = data.ReportDate.min()
                if is_aggregated:
                    data = Utilities.preprocess_data(data, str_to_id, is_aggregated, dead_line = test_dead_line, min_bet_count = config.min_bet_count_testing, is_day_eliminated = is_day_eliminated)
                else:
                    data = Utilities.preprocess_data(data, str_to_id, min_bet_count = config.min_bet_count_testing, is_day_eliminated = is_day_eliminated)
                print("Test data\n", data.tail()) 
            message = "%s | read_and_preprocess_training_data %.2f seconds" % (ENV, time.time() - start)
            print(message)
            logging.info(message)

            return data, bench_mark_date
        except Exception as e:
            message = "%s | read_and_preprocess_training_data | %s : %s" % (ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
    
    def transform_data(data, str_to_id, id_to_str):
        try:
            start = time.time()
            features_df = DataTransformer.transform(data, str_to_id, id_to_str)
            message = "%s | transform_data %.2f seconds" % (ENV, time.time() - start)
            print(message)
            logging.info(message)
            return features_df
        except Exception as e:
            message = "%s | transform_data | %s : %s" % (ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
    
    def save_transformed_data(features_df):
        try:
            start = time.time()
            Utilities.save_data(config.transformed_data_folder, config.transformed_data_file_name, features_df)
            message = "%s | save_transformed_data %.2f seconds" % (ENV, time.time() - start)
            print(message)
            logging.info(message)
        except Exception as e:
            message = "%s | save_transformed_data | %s : %s" % (ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
    
    def read_transformed_data():
        try:
            start = time.time()
            train_data = Utilities.read_data(config.transformed_data_folder, config.transformed_data_file_name)
            message = "%s | read_transformed_data %.2f seconds" % (ENV, time.time() - start)
            print(message)
            logging.info(message)
        except Exception as e:
            message = "%s | read_transformed_data | %s : %s" % (ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
        return train_data
    
    def train_model(train_data, str_to_id, PID):
        try:
            start = time.time()
            training_results_full_info_list, cat_cus_couple_dataframe = TrainingModelController.train_model(train_data, str_to_id, config.day_threshold, config.split_history_present, config.amplitude, PID)
            message = "%s | train_model %.2f seconds" % (ENV, time.time() - start)
            print(message)
            logging.info(message)
        except Exception as e:
            message = "%s | train_model | %s : %s" % (ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
        return training_results_full_info_list, cat_cus_couple_dataframe
    
    def insert_to_TrainResult_Table(training_results_full_info_list, end_training_date):
        try:
            start = time.time()
            DB_Interaction.insert_to_TrainingResults_table(training_results_full_info_list, end_training_date, config)
            message = "%s | insert_to_TrainResult_Table %.2f seconds" % (ENV, time.time() - start)
            print(message)
            logging.info(message)
        except Exception as e:
            message = "%s | insert_to_TrainResult_Table | %s : %s" % (ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
    
    def save_cat_cus_couple_dataframe(cat_cus_couple_dataframe):
        try:
            start = time.time()
            Utilities.save_data(config.cus_cat_couple_list_folder, config.cus_cat_couple_list_file_name, cat_cus_couple_dataframe)
            message = "%s | save_list_cus_cat %.2f seconds" % (ENV, time.time() - start)
            print(message)
            logging.info(message)
        except Exception as e:
            message = "%s | save_list_cus_cat | %s : %s" % (ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
    
    def read_cat_cus_couple_dataframe():
        try:
            start = time.time()
            cat_cus_couple_dataframe = Utilities.read_data(config.cus_cat_couple_list_folder, config.cus_cat_couple_list_file_name)
            message = "%s | read_cat_cus_couple_dataframe %.2f seconds" % (ENV, time.time() - start)
            print(message)
            logging.info(message)
        except Exception as e:
            message = "%s | read_cat_cus_couple_dataframe | %s : %s" % (ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
        return cat_cus_couple_dataframe
    
    def make_predictions_right_after_training_phase(cat_cus_couple_dataframe, start_predict_date, PID):
        try:
            start = time.time()
            print("cat_cus_couple_dataframe\n", cat_cus_couple_dataframe.head())
            mydf = PredictionController.make_predictions_right_after_training_phase(cat_cus_couple_dataframe, config, start_predict_date, PID)
            message = "%s | make_predictions_right_after_training_phase %.2f seconds" % (ENV, time.time() - start)
            print(message)
            logging.info(message)
            return mydf
        except Exception as e:
            message = "%s | make_predictions_right_after_training_phase | %s : %s" % (ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
    
    def get_answer_from_test_data(preprocessed_test_data, start_running, PID, test_date, prediction_results):
        try:
            start = time.time()
            PredictionController.get_answer_from_test_data(preprocessed_test_data, config, PID, test_date, prediction_results)
            message = "%s | preprocess_test_data_and_make_predictions %.2f seconds" % (ENV, time.time() - start)
            print(message)
            logging.info(message)
            message = "%s | Robot Classification completed in %.2f seconds" % (ENV, time.time() - start_running)
            print(message)
            logging.info(message)
            if agree_to_send_message:
                Telegram_send_message(message)
        except Exception as e:
            message = "%s | preprocess_test_data_and_make_predictions | %s : %s" % (ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
    
    def truncate_TrainResults_table():
        try:
            start = time.time()
            DB_Interaction.truncate_TrainResults_table(config)
            message = "%s | truncate_TrainResults_table %.2f seconds" % (ENV, time.time() - start)
            print(message)
            logging.info(message)
            if agree_to_send_message:
                Telegram_send_message(message)
        except Exception as e:
            message = "%s | truncate_TrainResults_table | %s : %s" % (ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
    
    def get_start_date_of_training(land_mark):
        try:
            start = time.time()
            list_of_files = os.listdir(config.train_data_folder_with_breaking_files)
            index_of_land_mark = list_of_files.index(land_mark + ".csv")
            start_date_of_training_index = index_of_land_mark - config.length_of_training
            start_date_of_training = list_of_files[start_date_of_training_index].replace(".csv", "")
            message = "%s | get_start_date %s %.2f seconds" % (ENV, start_date_of_training, time.time() - start)
            print(message)
            logging.info(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            return start_date_of_training
        except Exception as e:
            message = "%s | get_start_date | %s : %s" % (ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError