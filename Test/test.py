# String = "1,3,8"
# Lyst = String.split(',')
# print('Lyst\n',Lyst)
import sys
sys.path.append("C:/Users/diego.nguyen/diegoProj/RobotClassification")
from Model.distribution_model import DistributionModel
# import random
# from Helper.utils import Utilities
# import pandas as pd
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
# from tqdm import tqdm
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
    # cus = DistributionModel(0, 0)
    # streak = 0
    # ii = 0
    # while True:
    #     ii = ii + 1
    #     data = input("Enter winloss, turnover :")
    #     data = data.split(" ")
    #     turnover = float(data[1])
    #     winloss = float(data[0])
    #     # print("turnover = " + str(turnover), "winloss = " + str(winloss), sep = "\n")
    #     margin = winloss/turnover
    #     if streak == 0:
    #         if margin > 0:
    #             streak = 1
    #         else:
    #             streak = -1
    #     else:
    #         if margin*streak > 0:
    #             streak = streak + int(margin/abs(margin))
    #         else:
    #             streak = int(margin/abs(margin))
    #     delta_a, delta_b = Utilities.compute_deltas(margin, streak, 1)
    #     cus.update_hyper_params(delta_a, delta_b)
    #     mode = cus.get_mode()
    #     print("a = {0} | b = {1}".format(cus.a, cus.b))
    #     print("Mode After {0} days = {1} | Streak = {2}".format(ii, mode, streak))
    name = "Diego"
    age = 27
    # message = "Hello My name is %s . I am %s years old" % (name, age)
    message = "Hello My name is %s . I am %s years old" % name, age
    print(message)

