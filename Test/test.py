# String = "1,3,8"
# Lyst = String.split(',')
# print('Lyst\n',Lyst)
import random
import sys
sys.path.append("C:/Users/diego.nguyen/diegoProj/RobotClassification")
from Helper.utils import Utilities
import pandas as pd
import numpy as np
import json
from configuration.system_config import SystemConfig
from mysql.connector import MySQLConnection
from scipy.stats import shapiro
from scipy.stats.distributions import norm
from datetime import date
from DataAccess.database_interaction import DB_Interaction
from Controller.prediction_controller import PredictionController
from Helper.data_transformer import DataTransformer
from Helper.notify import Telegram_send_message
from tqdm import tqdm
from RobotClassificationManagement.robot_classification_manager import RobotClassificationManager
ENV = 'LOCAL'
systemConfig = SystemConfig(ENV.lower() + '_' + "config.ini", ENV)
def print_key(key):
    try:
        # print(mydict[key])
        a = 1/0
    except ZeroDivisionError:
        return None
if __name__=='__main__':
    # df = Utilities.read_data(config.category_mapping_folder, config.day_eliminated_category_mapping_file_name)
    # print(df)
    str_to_id, id_to_str = RobotClassificationManager.transform_category_mapping(is_day_eliminated=1)
    # print("id_to_str\n", id_to_str)
    # start_date_of_training = RobotClassificationManager.get_start_date_of_training(land_mark)

    data, end_training_date = RobotClassificationManager.read_and_preprocess_data(str_to_id, is_training = 1, is_aggregated = 0, is_entire = 1, is_day_eliminated=1)
    print("data\n", data.head())
    features_df = RobotClassificationManager.transform_data(data, str_to_id, id_to_str)
    print("features_df\n", features_df.head())
