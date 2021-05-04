from Helper.utils import Utilities
from Helper.data_transformer import DataTransformer
from Controller.training_model_controller import TrainingModelController
from Controller.prediction_controller import PredictionController
from configuration.system_config import SystemConfig
from configuration.robot_config import RobotConfig
from DataAccess.database_interaction import DB_Interaction
from Helper.notify import Telegram_send_message
import logging
import time
from datetime import datetime

ENV = 'LOCAL'
systemConfig = SystemConfig(ENV.lower() + '_' + "config.ini", ENV)
logging.basicConfig(filename = systemConfig.save_dir_log + systemConfig.log_name, level = logging.INFO)
agree_to_send_message = systemConfig.agree_to_send_message

class RobotClassificationManager():

    def get_robot_config():
        try:
            start = time.time()
            robotConfig = RobotConfig()
            # agree_to_send_message = config.agree_to_send_message
            message = "%s | get_config %.2f seconds" % (ENV, time.time() - start)
            print(message)
            logging.info(message)
        except Exception as e:
            message = "%s | get_config | %s : %s" % (ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
        return robotConfig

    @staticmethod
    def start(PID):
        try:
            start_running = time.time()
            now = datetime.now()
            current_time = now.strftime("%d/%m/%Y %H:%M:%S")
            message = "%s | Robot Classfication has just started" % ENV
            print(f"========================================={PID}/1000 | {current_time}=====================================================================")
            print(message)
            logging.info(f"========================================={PID}/1000 | {current_time}=====================================================================")
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
        return start_running

    @staticmethod
    def insert_to_RobotClassifyHyperParams_table(robotConfig):
        try:
            start = time.time()
            DB_Interaction.insert_to_RobotClassifyHyperParams_table(robotConfig, systemConfig)
            message = "%s | insert_to_RobotClassifyHyperParams_table %.2f seconds" % (ENV, time.time() - start)
            print(message)
            logging.info(message)
            if agree_to_send_message:
                Telegram_send_message(message)
        except Exception as e:
            message = "%s | insert_to_RobotClassifyHyperParams_table | %s : %s" % (ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
        return start
    
    @staticmethod
    def transform_category_mapping():
        try:
            start = time.time()
            category_mapping = Utilities.read_data(systemConfig.category_mapping_folder, systemConfig.category_mapping_file_name)
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
    
    @staticmethod
    def read_and_preprocess_data(str_to_id, is_training):
        try:
            start = time.time()
            if is_training:
                data = Utilities.read_data(systemConfig.train_data_folder, systemConfig.train_data_file_name)
                data = Utilities.preprocess_data(data, str_to_id)
                bench_mark_date = data.ReportDate.max()
            else:
                data = Utilities.read_data(systemConfig.test_data_folder, systemConfig.test_data_file_name)
                data = Utilities.preprocess_data(data, str_to_id)
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
    
    @staticmethod
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
    
    @staticmethod
    def save_transformed_data(features_df):
        try:
            start = time.time()
            Utilities.save_data(systemConfig.transformed_data_folder, systemConfig.transformed_data_file_name, features_df)
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
    
    @staticmethod
    def read_transformed_data():
        try:
            start = time.time()
            train_data = Utilities.read_data(systemConfig.transformed_data_folder, systemConfig.transformed_data_file_name)
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
    
    @staticmethod
    def train_model(robotConfig, train_data, str_to_id, PID):
        try:
            start = time.time()
            # print("train_data\n", train_data.head())
            training_results_full_info_list, cat_cus_couple_dataframe = TrainingModelController.train_model(train_data, str_to_id, robotConfig.day_threshold, robotConfig.split_history_present, robotConfig.amplitude, PID)
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
    
    @staticmethod
    def insert_to_TrainResult_Table(training_results_full_info_list, end_training_date):
        try:
            start = time.time()
            DB_Interaction.insert_to_TrainingResults_table(training_results_full_info_list, end_training_date, systemConfig)
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
    
    @staticmethod
    def save_cat_cus_couple_dataframe(cat_cus_couple_dataframe):
        try:
            start = time.time()
            Utilities.save_data(systemConfig.cus_cat_couple_list_folder, systemConfig.cus_cat_couple_list_file_name, cat_cus_couple_dataframe)
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
    
    @staticmethod
    def read_cat_cus_couple_dataframe():
        try:
            start = time.time()
            cat_cus_couple_dataframe = Utilities.read_data(systemConfig.cus_cat_couple_list_folder, systemConfig.cus_cat_couple_list_file_name)
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
    
    @staticmethod
    def make_predictions_right_after_training_phase(robotConfig, cat_cus_couple_dataframe, start_predict_date, PID):
        try:
            start = time.time()
            # print("cat_cus_couple_dataframe\n", cat_cus_couple_dataframe.head())
            # output = PredictionController.make_predictions_right_after_training_phase(cat_cus_couple_dataframe, systemConfig, robotConfig, start_predict_date, PID)
            PredictionController.make_predictions_right_after_training_phase(cat_cus_couple_dataframe, systemConfig, robotConfig, start_predict_date, PID)
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
        # return output
    
    @staticmethod
    def make_predictions_from_test_data(robotConfig, preprocessed_test_data, start_running, PID):
        try:
            start = time.time()
            PredictionController.execute(preprocessed_test_data, systemConfig, robotConfig, PID)
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