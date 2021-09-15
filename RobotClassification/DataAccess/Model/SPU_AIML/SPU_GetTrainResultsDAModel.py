import json

class SPU_GetTrainResultsDAModel(object):
    def __init__(self,*args):
        self.ip_CustCategoryData: json = args[0]
        self.ip_HyperParamsID: int = args[1]
        self.op_ErrorMessage = None
        
    def __call__(self):
        return [self.ip_CustCategoryData, self.ip_HyperParamsID, self.op_ErrorMessage]