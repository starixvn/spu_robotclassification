from mysql.connector import MySQLConnection
import json
import pandas as pd
from tqdm import tqdm

class DB_Interaction():

    @staticmethod
    def insert_to_TrainingResults_table(training_results_full_info_list, date_insert, config, is_training_phase = 1):
        chunks = [training_results_full_info_list[x:x + config.chunk_size] for x in range(0, len(training_results_full_info_list), config.chunk_size)]
        conn = MySQLConnection(user = config.aimluser, password = config.aimlpwd,
                                host = config.aimlhost, port = config.aimlport, database = config.aimldb)
        cur = conn.cursor()
        if is_training_phase:
            for chunk in tqdm(chunks, desc = "Insert Training-Results-Table"):
                jsonList = json.dumps(chunk)
                # print("jsonList\n", jsonList)
                _,_, out1 = cur.callproc("SPU_AIML_InsertTrainResults", [jsonList, date_insert, None])
                if out1 is not None:
                    print(out1, jsonList)
                conn.commit()
        else:
            for chunk in chunks:
                jsonList = json.dumps(chunk)
                # print("jsonList\n", jsonList)
                _,_, out1 = cur.callproc("SPU_AIML_InsertTrainResults", [jsonList, date_insert, None])
                if out1 is not None:
                    print("insert_to_TrainingResults_table", out1, jsonList)
                conn.commit()
        cur.close()
        conn.close()

    def get_from_TrainingResults_table(test_data, config, PID):
        # test_data, config = args
        mydata = test_data[['C', 'CAT']]
        # print("mydata\n", mydata.head())
        # mydata.rename(columns = {'CustId':'C', 'CategoryId':'CAT'}, inplace = True)
        mydata = mydata.drop_duplicates()
        get_objects = mydata.to_dict(orient = 'records')
        jsonList = json.dumps(get_objects)
        # print("jsonList\n", jsonList)
        conn = MySQLConnection(user = config.aimluser, password = config.aimlpwd,
                                host = config.aimlhost, port = config.aimlport, database = config.aimldb)
        cur = conn.cursor()
        _,_, out1 = cur.callproc("SPU_AIML_GetTrainResults", [jsonList, PID, None])
        if out1 is not None:
            print(out1, jsonList)
        db_results = [r.fetchall() for r in cur.stored_results()]
        conn.commit()
        cur.close()
        conn.close()
        # print("db_results\n", db_results)
        df = pd.DataFrame(db_results[0], columns = ['C', 'CAT', 'M', 'SWD', 'SLD', 'STR', 'AD'])
        df['M'] = df['M'].astype(float)
        df['SWD'] = df['SWD'].astype(float)
        df['SLD'] = df['SLD'].astype(float)
        # print("df\n", df.head())
        return df

    @staticmethod
    def insert_to_PredictedResults_table(predict_full_info_list, date_insert, config, right_after_prediction = 1):
        chunks = [predict_full_info_list[x:x + config.chunk_size] for x in range(0, len(predict_full_info_list), config.chunk_size)]
        conn = MySQLConnection(user = config.aimluser, password = config.aimlpwd,
                                host = config.aimlhost, port = config.aimlport, database = config.aimldb)
        cur = conn.cursor()
        if right_after_prediction:
            for chunk in tqdm(chunks, desc = "Insert Winloss-Prediction-Table"):
                jsonList = json.dumps(chunk)
                # print("jsonList\n", jsonList)
                _,_, out1 = cur.callproc("SPU_AIML_InsertWinlossPrediction", [jsonList, date_insert, None])
                if out1 is not None:
                    print("insert_to_PredictedResults_table", out1, jsonList)
                conn.commit()
        else:
            for chunk in chunks:
                jsonList = json.dumps(chunk)
                _,_, out1 = cur.callproc("SPU_AIML_InsertWinlossPrediction", [jsonList, date_insert, None])
                if out1 is not None:
                    print("insert_to_PredictedResults_table", out1, jsonList)
                conn.commit()
        cur.close()
        conn.close()
    
    def truncate_TrainResults_table(config):
        conn = MySQLConnection(user = config.aimluser, password = config.aimlpwd,
                                host = config.aimlhost, port = config.aimlport, database = config.aimldb)
        cur = conn.cursor()

        cur.callproc("SPU_AIML.SPU_AIML_DBA_Truncate_Table", ["TrainResults"])
        conn.commit()
        cur.close()
        conn.close()