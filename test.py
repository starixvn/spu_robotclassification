# String = "1,3,8"
# Lyst = String.split(',')
# print('Lyst\n',Lyst)

from utils import Utilities
import pandas as pd
import json
from configuration.system_config import SystemConfig
from mysql.connector import MySQLConnection
from scipy.stats import shapiro
from scipy.stats.distributions import norm
from datetime import date
from database_interaction import DB_Interaction
from prediction_controller import PredictionController
ENV = 'LOCAL'
config = SystemConfig(ENV.lower() + '_' + "config.ini", ENV)

if __name__=='__main__':
    # print("config\n", config.aimldb)
    # conn = MySQLConnection(user = config.aimluser, password = config.aimlpwd,
    #                             host = config.aimlhost, port = config.aimlport, database = config.aimldb)
    # cur = conn.cursor()
    # chunk = [{'C':31340, 'CAT':1, 'M':0.93, 'SWD':30., 'SLD':40.0, 'STR':1, 'AD':6}]
    # chunk = [{'C':31340, 'CAT':1, 'M':0.93, 'SWD':30., 'SLD':40.0, 'STR':-1, 'AD':6}]
    # chunk = [{'C':31340, 'CAT':1}, {'C':31340, 'CAT':2}]
    # chunk = [{'C':31340, 'CAT':1, 'M':0.93, 'SWD':30., 'SLD':40.0, 'IP':1, 'IPW':0, 'IPTW':1}]
    # chunk = [{'C':31340, 'CAT':1, 'M':0.93, 'SWD':30., 'SLD':40.0, 'IP':1, 'IPW':0}]
    # chunk = [{"C": 43600693, "CAT": 1, "M": 5.1, "SWD": 5, "SLD": 2, "IP": 1, "IPW": 1, "IPTW": 1}]
    # chunk = [{"C": 43600693, "CAT": 1, "M": 0.15, "SWD": 5, "SLD": 2, "IP": 1, "IPW": 0, "IPTW": 1}]
    # chunk = [{"C": 43600693, "CAT": 9, "M": 0.85, "SWD": 6, "SLD": 3, "IP": 1, "IPW": 1, "IPTW": 0}]
    # jsonList = json.dumps(chunk)
    # print("jsonList\n", jsonList)
    # scan_date = '2021-04-26'
    # _,_, out1 = cur.callproc("SPU_AIML_InsertTrainResults", [jsonList, scan_date, None])
    # _, out1 = cur.callproc("SPU_AIML_GetTrainResults", [jsonList, None])
    # predict_date = '2021-04-26'
    # _,_, out1 = cur.callproc("SPU_AIML_InsertWinlossPrediction", [jsonList, predict_date, None])
    # if out1 is not None:
    #     print(out1)
    # conn.commit()
    # cur.close()
    # conn.close()
    # db_results = [r.fetchall() for r in cur.stored_results()]
    # print("db_results\n", db_results[0])
    # df = pd.DataFrame(db_results[0], columns=['CustId', 'CategoryId', 'Mode', 'A', 'B', 'Streak', 'Active_days'])
    # print(df)
    # data = Utilities.read_data(config.test_data_folder, config.test_data_file_name)
    data = pd.read_csv(config.test_data_folder + config.test_data_file_name, index_col=0)
    print("data\n", data.head())
    data.to_csv(config.test_data_folder + config.test_data_file_name, index=False)
    data = pd.read_csv(config.test_data_folder + config.test_data_file_name)
    print("data\n", data.head())
