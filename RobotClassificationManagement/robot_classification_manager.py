import re
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

    def start():
        try:
            start = time.time()
            now = datetime.now()
            current_time = now.strftime("%d/%m/%Y %H:%M:%S")
            message = "%s | Robot Classfication has just started" % ENV
            print(f"========================================={current_time}=====================================================================")
            print(message)
            logging.info(f"========================================={current_time}=====================================================================")
            logging.info(message)
            if agree_to_send_message:
                Telegram_send_message(message)
        except Exception as e:
            message = "%s | start | %s : %s" % (ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
        return start
    
    def transform_category_mapping():
        try:
            start = time.time()
            category_mapping = Utilities.read_data(config.category_mapping_folder, config.category_mapping_file_name)
            str_to_id, id_to_str = Utilities.transform_category_mapping(category_mapping)
            message = "%s | transform_category_mapping %.2f seconds" % (ENV, time.time() - start)
            print(message)
            logging.info(message)
        except Exception as e:
            message = "%s | transform_category_mapping | %s : %s" % (ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
        return str_to_id, id_to_str
    
    def read_and_preprocess_data(str_to_id, is_training):
        try:
            start = time.time()
            data = Utilities.read_data(config.train_data_folder, config.train_data_file_name)
            data = Utilities.preprocess_data(data, str_to_id)
            if is_training:
                bench_mark_date = data.ReportDate.max()
            else:
                bench_mark_date = data.ReportDate.min()
            message = "%s | read_and_preprocess_training_data %.2f seconds" % (ENV, time.time() - start)
            print(message)
            logging.info(message)
        except Exception as e:
            message = "%s | read_and_preprocess_training_data | %s : %s" % (ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
        return data, bench_mark_date
    
    def transform_data(data, id_to_str):
        try:
            start = time.time()
            features_df = DataTransformer.transform(data, id_to_str)
            message = "%s | transform_data %.2f seconds" % (ENV, time.time() - start)
            print(message)
            logging.info(message)
        except Exception as e:
            message = "%s | transform_data | %s : %s" % (ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
        return features_df
    
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
    
    def train_model(train_data, str_to_id):
        try:
            start = time.time()
            print("train_data\n", train_data.head())
            training_results_full_info_list, cat_cus_couple_dataframe = TrainingModelController.train_model(train_data, str_to_id, config.day_threshold, config.split_history_present, config.amplitude)
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
    
    def make_predictions_right_after_training_phase(cat_cus_couple_dataframe, start_predict_date):
        try:
            start = time.time()
            print("cat_cus_couple_dataframe\n", cat_cus_couple_dataframe.head())
            PredictionController.make_predictions_right_after_training_phase(cat_cus_couple_dataframe, config, start_predict_date)
            message = "%s | make_predictions_right_after_training_phase %.2f seconds" % (ENV, time.time() - start)
            print(message)
            logging.info(message)
        except Exception as e:
            message = "%s | make_predictions_right_after_training_phase | %s : %s" % (ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
    
    def make_predictions_from_test_data(preprocessed_test_data, start_running):
        try:
            start = time.time()
            PredictionController.execute(preprocessed_test_data, config)
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