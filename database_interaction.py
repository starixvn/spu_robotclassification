from mysql.connector import MySQLConnection
import json

class DB_Interaction():
    def insert_to_TrainingResults_table(args):
        training_results_full_info_list, config, date_insert = args
        chunks = [training_results_full_info_list[x:x + config.chunk_size] for x in range(0, len(training_results_full_info_list), config.chunk_size)]
        conn = MySQLConnection(user = config.aimluser, password = config.aimlpwd,
                                host = config.aimlhost, port = config.aimlport, database = config.aimldb)
        cur = conn.cursor()
        for chunk in chunks:
            jsonList = json.dumps(chunk)
            _,_, out1 = cur.callproc("SPU_AIML_InsertTrainResults", [jsonList, date_insert, None])
            if out1 is not None:
                print(out1)
            conn.commit()
        cur.close()
        conn.close()

    def get_from_TrainingResults_table():
        pass

    def insert_to_PredictedResults_table():
        pass
    
    def insert_to_PredictionAccuracy_table():
        pass