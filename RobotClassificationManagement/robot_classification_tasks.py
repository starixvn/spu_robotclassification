import os
import json
from Utilities.Category_Mapping_Manager import Category_Mapping_Manager
from Utilities.File_Manager import File_Manager
from Utilities.Data_Preprocessing_Manager import Data_Preprocessing_Manager
from Utilities.data_transformer import DataTransformer
from Controller.training_model_controller import TrainingModelController
from Controller.prediction_controller import PredictionController
from Configuration.Configuration import config
from DataAccess.DataAccessConnection import spu_aiml
from DataAccess.Model.SPU_AIML.SPU_InsertTrainResultsDAModel import SPU_InsertTrainResultsDAModel
from DataAccess.DataAccessConnection import DataAccessConnection
from DataAccess.CoreDA.BaseDA import BaseDA
from Helper.notify import Telegram_send_message
import logging
import time
from datetime import datetime

ENV = 'LOCAL'
logging.basicConfig(filename = config.save_dir_log + config.log_name, level = logging.INFO)
agree_to_send_message = config.agree_to_send_message

class RobotClassificationTasks():

    def start(PID, land_mark, released_answer_date):
        try:
            start_running = time.time()
            now = datetime.now()
            current_time = now.strftime("%d/%m/%Y %H:%M:%S")
            message = "%s | %s | INFO | Robot Classfication has just started" % (config.app_name, ENV)
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
            message = "%s | %s | ERROR | start function : %s %s" % (config.app_name, ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
        
    
    def transform_category_mapping(is_day_eliminated = 0, is_live_indicator_eliminated = 0, is_bettype_eliminated = 0):
        try:
            start = time.time()
            if is_day_eliminated and is_live_indicator_eliminated and is_bettype_eliminated:
                category_mapping = File_Manager.read_data(config.category_mapping_folder, config.vs_sport_only_category_mapping_file_name)
            elif is_day_eliminated and is_live_indicator_eliminated:
                category_mapping = File_Manager.read_data(config.category_mapping_folder, config.day_and_live_indicator_eliminated_category_mapping_file_name)
            elif is_day_eliminated:
                category_mapping = File_Manager.read_data(config.category_mapping_folder, config.day_eliminated_category_mapping_file_name)
            else:
                category_mapping = File_Manager.read_data(config.category_mapping_folder, config.category_mapping_file_name)
            str_to_id, id_to_str = Category_Mapping_Manager.transform_category_mapping(category_mapping, is_day_eliminated, is_live_indicator_eliminated, is_bettype_eliminated)
            message = "%s | %s | INFO | transform_category_mapping %.2f seconds" % (config.app_name, ENV, time.time() - start)
            print(message)
            logging.info(message)
            return str_to_id, id_to_str
        except Exception as e:
            message = "%s | %s | ERROR | transform_category_mapping function : %s %s" % (config.app_name, ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
    
    def read_and_preprocess_data(str_to_id, is_training, is_entire = 1, start_date = None, is_aggregated = 0, 
                                is_day_eliminated = 0, is_live_indicator_eliminated = 0, is_bettype_eliminated = 0):
        try:
            start = time.time()
            if is_training:
                if is_entire:
                    data = File_Manager.read_data(config.train_data_folder, config.train_data_file_name, is_entire, 
                                                config.length_of_training, start_date)
                else:
                    data = File_Manager.read_data(config.train_data_folder_with_breaking_files, config.train_data_file_name, is_entire, 
                                                config.length_of_training, start_date)
                dead_line = data.ReportDate.max()
                bench_mark_date = data.ReportDate.max()        
            else:
                if is_entire:
                    data = File_Manager.read_data(config.test_data_folder, config.test_data_file_name, is_entire, 
                                                config.length_of_testing, start_date)
                else:
                    data = File_Manager.read_data(config.test_data_folder_with_breaking_files, config.test_data_file_name, is_entire, 
                                                config.length_of_testing, start_date)
                dead_line = data.ReportDate.max()
                # data = data[data.ReportDate <= test_dead_line]
                bench_mark_date = data.ReportDate.min()
            data = Data_Preprocessing_Manager.preprocess_data(data, str_to_id, is_training = is_training,
                                                            is_aggregated = is_aggregated, 
                                                            dead_line = dead_line,
                                                            min_bet_count = config.min_bet_count_training, 
                                                            is_day_eliminated = is_day_eliminated, 
                                                            is_live_indicator_eliminated = is_live_indicator_eliminated, 
                                                            is_bettype_eliminated = is_bettype_eliminated)   
            message = "%s | %s | INFO | read_and_preprocess_training_data %.2f seconds" % (config.app_name, ENV, time.time() - start)
            print(message)
            logging.info(message)

            return data, bench_mark_date
        except Exception as e:
            message = "%s | %s | ERROR | read_and_preprocess_training_data function : %s %s" % (config.app_name, ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
    
    def transform_data(data, str_to_id, id_to_str):
        try:
            start = time.time()
            features_df = DataTransformer.transform(data, str_to_id, id_to_str)
            message = "%s | %s | INFO | transform_data %.2f seconds" % (config.app_name, ENV, time.time() - start)
            print(message)
            logging.info(message)
            return features_df
        except Exception as e:
            message = "%s | %s | ERROR | transform_data function : %s %s" % (config.app_name, ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
    
    @staticmethod
    def save_transformed_data(features_df):
        try:
            start = time.time()
            File_Manager.save_data(config.transformed_data_folder, config.transformed_data_file_name, features_df)
            message = "%s | %s | INFO | save_transformed_data %.2f seconds" % (config.app_name, ENV, time.time() - start)
            print(message)
            logging.info(message)
        except Exception as e:
            message = "%s | %s | ERROR | save_transformed_data function: %s %s" % (config.app_name, ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
    
    @staticmethod
    def read_transformed_data():
        try:
            start = time.time()
            train_data = File_Manager.read_data(config.transformed_data_folder, config.transformed_data_file_name)
            print("Transformed data\n", train_data.sample(10))
            message = "%s | %s | INFO | read_transformed_data %.2f seconds" % (config.app_name, ENV, time.time() - start)
            print(message)
            logging.info(message)
        except Exception as e:
            message = "%s | %s | ERROR | read_transformed_data function : %s %s" % (config.app_name, ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
        return train_data
    
    @staticmethod
    def train_model(train_data, str_to_id, PID):
        try:
            start = time.time()
            training_results_full_info_list, cat_cus_couple_dataframe = TrainingModelController.train_model(train_data, str_to_id, config.day_threshold, config.split_history_present, config.amplitude, PID)
            message = "%s | %s | INFO | train_model %.2f seconds" % (config.app_name, ENV, time.time() - start)
            print(message)
            logging.info(message)
        except Exception as e:
            message = "%s | %s | ERROR | train_model function : %s %s" % (config.app_name, ENV, type(e).__name__, e.args)
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
            # DB_Interaction.insert_to_TrainingResults_table(training_results_full_info_list, end_training_date, config)
            chunks = [training_results_full_info_list[x:x + config.chunk_size] for x in \
                    range(0, len(training_results_full_info_list), config.chunk_size)]
            connection_spu = DataAccessConnection(spu_aiml)
            for chunk in chunks:
                # time_start3 = time.time()
                chunk = json.dumps(chunk)
                ip_param = SPU_InsertTrainResultsDAModel(chunk, end_training_date)
                BaseDA.execute("SPU_AIML_InsertTrainResults",spu_aiml,ip_param,connection_spu)

            message = "%s | %s | INFO | insert_to_TrainResult_Table %.2f seconds" % (config.app_name, ENV, time.time() - start)
            print(message)
            logging.info(message)
        except Exception as e:
            message = "%s | %s | ERROR | insert_to_TrainResult_Table function : %s %s" % (config.app_name, ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
    
    @staticmethod
    def save_cat_cus_couple_dataframe(cat_cus_couple_dataframe):
        try:
            start = time.time()
            File_Manager.save_data(config.cus_cat_couple_list_folder, config.cus_cat_couple_list_file_name, cat_cus_couple_dataframe)
            message = "%s | %s | INFO | save_list_cus_cat %.2f seconds" % (config.app_name, ENV, time.time() - start)
            print(message)
            logging.info(message)
        except Exception as e:
            message = "%s | %s | ERROR | save_list_cus_cat function : %s %s" % (config.app_name, ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
    
    @staticmethod
    def read_cat_cus_couple_dataframe():
        try:
            start = time.time()
            cat_cus_couple_dataframe = File_Manager.read_data(config.cus_cat_couple_list_folder, config.cus_cat_couple_list_file_name)
            message = "%s | %s | INFO | read_cat_cus_couple_dataframe %.2f seconds" % (config.app_name, ENV, time.time() - start)
            print(message)
            logging.info(message)
        except Exception as e:
            message = "%s | %s | ERROR | read_cat_cus_couple_dataframe function : %s %s" % (config.app_name, ENV, type(e).__name__, e.args)
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
            message = "%s | %s | INFO | make_predictions_right_after_training_phase %.2f seconds" % (config.app_name, ENV, time.time() - start)
            print(message)
            logging.info(message)
            return mydf
        except Exception as e:
            message = "%s | %s | ERROR | make_predictions_right_after_training_phase function : %s %s" % (config.app_name, ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
        # return output
    
    def get_answer_from_test_data(preprocessed_test_data, start_running, PID, test_date, prediction_results):
        try:
            start = time.time()
            PredictionController.get_answer_from_test_data(preprocessed_test_data, config, PID, test_date, prediction_results)
            message = "%s | %s | INFO | preprocess_test_data_and_make_predictions %.2f seconds" % (config.app_name, ENV, time.time() - start)
            print(message)
            logging.info(message)
            message = "%s | %s | INFO | Robot Classification completed in %.2f seconds" % (config.app_name, ENV, time.time() - start_running)
            print(message)
            logging.info(message)
            if agree_to_send_message:
                Telegram_send_message(message)
        except Exception as e:
            message = "%s | %s | ERROR | preprocess_test_data_and_make_predictions function : %s %s" % (config.app_name, ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError
    
    # def truncate_TrainResults_table():
    #     try:
    #         start = time.time()
    #         DB_Interaction.truncate_TrainResults_table(config)
    #         message = "%s | truncate_TrainResults_table %.2f seconds" % (ENV, time.time() - start)
    #         print(message)
    #         logging.info(message)
    #         if agree_to_send_message:
    #             Telegram_send_message(message)
    #     except Exception as e:
    #         message = "%s | truncate_TrainResults_table | %s : %s" % (ENV, type(e).__name__, e.args)
    #         print(message)
    #         logging.error(message)
    #         if agree_to_send_message:
    #             Telegram_send_message(message)
    #         raise ValueError
    
    def get_start_date_of_training(land_mark):
        try:
            start = time.time()
            list_of_files = os.listdir(config.train_data_folder_with_breaking_files)
            index_of_land_mark = list_of_files.index(land_mark + ".csv")
            start_date_of_training_index = index_of_land_mark - config.length_of_training
            start_date_of_training = list_of_files[start_date_of_training_index].replace(".csv", "")
            message = "%s | %s | INFO | get_start_date %s %.2f seconds" % (config.app_name, ENV, start_date_of_training, time.time() - start)
            print(message)
            logging.info(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            return start_date_of_training
        except Exception as e:
            message = "%s | %s | ERROR | get_start_date function : %s %s" % (config.app_name, ENV, type(e).__name__, e.args)
            print(message)
            logging.error(message)
            if agree_to_send_message:
                Telegram_send_message(message)
            raise ValueError