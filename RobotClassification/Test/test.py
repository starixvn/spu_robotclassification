# String = "1,3,8"
# Lyst = String.split(',')
# print('Lyst\n',Lyst)
import sys
sys.path.append("C:/Users/diego.nguyen/diegoProj/RobotClassification")
# from Model.distribution_model import DistributionModel
# import random
#from Utilities.File_Manager import File_Manager
import pandas as pd
# import numpy as np
# import json
# from configuration.system_config import SystemConfig
from mysql.connector import MySQLConnection
from Configuration.Configuration import config
# from scipy.stats.distributions import norm
# from datetime import date
# from DataAccess.database_interaction import DB_Interaction
# from Controller.prediction_controller import PredictionController
# from Helper.data_transformer import DataTransformer
from Helper.notify import Telegram_send_message
from tqdm import tqdm
import datetime
from RobotClassificationManagement.robot_classification_tasks import RobotClassificationTasks
from Utilities.File_Manager import File_Manager
# ENV = 'LOCAL'
# systemConfig = SystemConfig(ENV.lower() + '_' + "config.ini", ENV)
# def print_key(key):
#     try:
#         # print(mydict[key])
#         a = 1/0
#     except ZeroDivisionError:
#         return None
import os
import shutil
import json
class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
if __name__=='__main__':
    arrival = "/home/vndata4ai/RobotClassification/"
    # fn = "result_t6.csv"
    # test_path = "robotTicket_06_14_2021_03_08_10.csv"
    departure =  "/home/vnteam/Robot/BACK_UP/" 

    # data = File_Manager.read_data(location, None, 0, 30, "2021-04-15")
    # data = RobotClassificationTasks.read_and_preprocess_data()
    # File_Manager.save_data(saving_location, "train.csv", data, 0)
    # train_dates = dates[:-15]
    # for day in tqdm(train_dates, desc="Train"):
    # for day in tqdm(dates, desc="Break"):
    #     df = data[data.winlostdate == day]
    #     day = day.split(" ")[0]
    #     df.to_csv(location + "breaking_files/" + day + ".csv", index = False)
    
    # data = pd.read_csv(file_path, skiprows = [1], skipfooter = 1)
    # # day = "2021-06-1"
    # print("head data\n", data.head())
    # test_dates = data.winlostdate.unique()
    # # # # test_dates = dates[-15:]
    # for day in tqdm(test_dates, desc="Test"):
    #     df = data[data.winlostdate == day]
    #     day = day.split(" ")[0]
    #     if day == "2021-05-30" or day == "2021-05-31":
    #         print("day = %s" % day)
    #         df.to_csv(arrival + day + ".csv", index = False)
    # print(f"{bcolors.FAIL}Warning: No active frommets remain. Continue?{bcolors.ENDC}")

    # land_marks = RobotClassificationTasks.get_land_marks()
    # ls = os.listdir(departure)
    # for fn in ls:
        # os.rename(arrival + fn, departure + fn)
        # if fn.startswith("robotTicket"):
        # if fn.startswith("2021-04") or fn.startswith("2021-05"):
        # os.rename(departure + fn, arrival + fn)
        # mile_stone = fn.rsplit("_", 3)[0]
        # mile_stone = mile_stone.split("_", 1)[1]
        # datetime_object = datetime.datetime.strptime(mile_stone, "%m_%d_%Y")
        # land_mark = datetime_object.strftime("%Y-%m-%d")
        # shutil.copy(departure + fn, arrival + fn)
    # message = "Long's brother is setting up daily jobs for RC!"
    # Telegram_send_message(message)
    # a = [1,3,2]
    # a = sorted(a, reverse = True)
    # a.pop()
    # print("a = %s" % len(a))
    # conn = MySQLConnection(user = "ctsServiceAdmin", password = "ctsServiceAdmin@CTS2209#",
    #                         host = "10.40.40.58", port = "3306", database = "CTS_DataCenter")
    # # conn = MySQLConnection(user = "darius.vn", password = "1qaz@Wsx3edc",
    # #                         host = "10.18.200.72", port = "3306", database = "CTS_DataCenter")
    # cursor = conn.cursor()
    # chunk = [{"C": 111, "CID": 23, "IP": 1, "IPW": 0, "FD": "2021-07-01", "TD": "2021-07-15"}]
    # jsonList = json.dumps(chunk)
    # _, out1 = cursor.callproc("CTS_DataCenter.CTS_DC_RobotClassification_Insert", [jsonList, None])
    # if out1 is not None:
    #     print(out1)
    # conn.commit()
    # cursor.close()
    # conn.close()
    str_to_id, id_to_str = RobotClassificationTasks.transform_category_mapping(is_day_eliminated = 1, 
                                                                        is_live_indicator_eliminated = 0,
                                                                        is_bettype_eliminated = 0)
    
    data, _ = RobotClassificationTasks.read_and_preprocess_data(str_to_id, is_training = 1, is_aggregated = 1, is_entire = 0, 
                                                                    start_date = "2021-05-03", 
                                                                    is_day_eliminated = 1, 
                                                                    is_live_indicator_eliminated = 0, 
                                                                    is_bettype_eliminated = 0)
    # data = File_Manager.read_data(config.train_data_folder_with_breaking_files, config.train_data_file_name, 0, 
    #                                             config.length_of_training, "2021-05-02")
    print("data\n", data.head())


