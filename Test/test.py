# String = "1,3,8"
# Lyst = String.split(',')
# print('Lyst\n',Lyst)
# import sys
# sys.path.append("C:/Users/diego.nguyen/diegoProj/RobotClassification")
# from Model.distribution_model import DistributionModel
# import random
# from Helper.utils import Utilities
import pandas as pd
# import numpy as np
# import json
# from configuration.system_config import SystemConfig
# from mysql.connector import MySQLConnection
# from scipy.stats import shapiro
# from scipy.stats.distributions import norm
# from datetime import date
# from DataAccess.database_interaction import DB_Interaction
# from Controller.prediction_controller import PredictionController
# from Helper.data_transformer import DataTransformer
# from Helper.notify import Telegram_send_message
from tqdm import tqdm
# from RobotClassificationManagement.robot_classification_manager import RobotClassificationManager
# ENV = 'LOCAL'
# systemConfig = SystemConfig(ENV.lower() + '_' + "config.ini", ENV)
# def print_key(key):
#     try:
#         # print(mydict[key])
#         a = 1/0
#     except ZeroDivisionError:
#         return None
if __name__=='__main__':
    location = "D:/Project/Robot/TRAIN_DATA/"
    train_path = "robotTicket_0415_0531_2021.csv"
    # test_path = "robotTicket_06_14_2021_03_08_10.csv"
    # saving_location = 

    data = pd.read_csv(location + train_path, skiprows = [1], skipfooter = 1)
    dates = data.winlostdate.unique()
    dates = sorted(dates)
    # train_dates = dates[:-15]
    # for day in tqdm(train_dates, desc="Train"):
    for day in tqdm(dates, desc="Break"):
        df = data[data.winlostdate == day]
        day = day.split(" ")[0]
        df.to_csv(location + "breaking_files/" + day + ".csv", index = False)
    
    # test_data = pd.read_csv(location + test_path, skiprows = [1], skipfooter = 1)
    # test_dates = test_data.winlostdate.unique()
    # test_dates = dates[-15:]
    # for day in tqdm(test_dates, desc="Test"):
    #     df = data[data.winlostdate == day]
    #     df.to_csv("/home/vnteam/Robot/TEST_DATA/" + day + ".csv", index = False)

