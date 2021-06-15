import pandas as pd
from tqdm import tqdm
import os

class File_Manager():

    @staticmethod
    def read_data(location, file_name, is_entire = 1, length_of_assessment = None, start_date = None):
        
        try:
            if is_entire:
                data =  pd.read_csv(location + file_name)
            else:
                list_files = sorted(os.listdir(location))
                start_file_index = list_files.index(start_date + ".csv")
                end_file = list_files[start_file_index + length_of_assessment - 1]
                list_target_files = list_files[start_file_index:start_file_index + length_of_assessment]
                data = pd.concat([pd.read_csv(location + fn) for fn in tqdm(list_target_files, desc = "Concat Files")], ignore_index = True)
            max_train_date = data.winlostdate.max()
            data.rename(columns = {"winlostdate":"ReportDate",
                                    "custid":"CustId",
                                    "sporttype":"SporttypeId",
                                    "bettype":"BettypeId",
                                    "liveindicator":"IsLive"}, inplace = True)
            data['ReportDate'] = data['ReportDate'].apply(lambda z : z.split(' ')[0])
            print("HEAD of data\n", data.head())
            print("TAIL of data\n", data.tail())
        except IndexError:
            data = None
        except AttributeError:
            data =  pd.read_csv(location + file_name)
        return data
    
    @staticmethod
    def save_data(location, file_name, dataframe):
        dataframe.to_csv(location + file_name, index = False)