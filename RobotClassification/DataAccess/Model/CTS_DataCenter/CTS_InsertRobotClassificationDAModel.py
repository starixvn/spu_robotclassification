import datetime
import json


class CTS_InsertRobotClassificationDAModel(object):
    def __init__(self,*args):
        self.ip_DailyPrediction: json = args[0]
        # self.ip_ScanDate: datetime = args[1]
        self.op_ErrorMessage = None
        
    def __call__(self):
        return [self.ip_DailyPrediction, self.op_ErrorMessage]
