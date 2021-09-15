import sys
sys.path.append("C:/Users/diego.nguyen/diegoProj/RobotClassification")
from DataAccess.DataAccessConnection import spu_aiml, cts_datacenter
# from DataAccess.Model.SPU_AIML.SPU_GetTrainResultsDAModel import SPU_GetTrainResultsDAModel
from DataAccess.Model.SPU_AIML.SPU_InsertWinlossPredictionDAModel import SPU_InsertWinlossPredictionDAModel
# from DataAccess.Model.CTS_DataCenter.CTS_InsertRobotClassificationDAModel import CTS_InsertRobotClassificationDAModel
from DataAccess.DataAccessConnection import DataAccessConnection
from DataAccess.CoreDA.BaseDA import BaseDA
from Configuration.Configuration import config
import json
# import pandas as pd
import pickle

connection_spu = DataAccessConnection(spu_aiml)
predict_full_info_list_right_after_training = [{"C":9999, "CAT":2, "M":0.89, "SWD":1.0932e-102, "SLD":-2.43e-103, "IP":1, 
                                                "IPW":1, "PID":0}]

# predict_full_info_list_right_after_training = [{"C":9999, "CAT":2, "M":0.89, "SWD":0, "SLD":0, "IP":1, 
#                                                 "IPW":1, "PID":0}]
# with open("D:/Project/Robot/LOG/" + "test_SP_data.pkl", "r") as f:
#     predict_full_info_list_right_after_training = pickle.load(f)

# mydf = pd.DataFrame(mydf)
# data_SPU = mydf[["C", "CAT", "M", "SWD", "SLD", "IP", "IPW", "PID"]]
# predict_full_info_list_right_after_training = data_SPU.to_dict(orient = 'records')
chunks = [predict_full_info_list_right_after_training[x:x + config.chunk_size] for x in \
            range(0, len(predict_full_info_list_right_after_training), config.chunk_size)]
if config.insert_to_aiml:
    for chunk in chunks:
        chunk = json.dumps(chunk)
        ip_param = SPU_InsertWinlossPredictionDAModel(chunk, "2021-08-31")
        dba_results = BaseDA.execute("SPU_AIML_InsertWinlossPrediction", spu_aiml, ip_param, connection_spu)