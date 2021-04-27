import configparser
import os


class SystemConfig(object):
    """description of class"""
    def __init__(self, *args, **kwargs):
        path = os.path.dirname(__file__)
        config = configparser.ConfigParser()
        config.read(os.path.join(path, args[0]))
        self.config = config
        self.ENV = args[1]

        # define paths
        self.train_data_folder = self.getDataStrConfig(
            self.config, 'DEFAULT', 'TRAIN_DATA_FOLDER')
        self.train_data_file_name = self.getDataStrConfig(
            self.config, 'DEFAULT', 'TRAIN_DATA_FILE_NAME')
        self.test_data_folder = self.getDataStrConfig(
            self.config, 'DEFAULT', 'TEST_DATA_FOLDER')
        self.test_data_file_name = self.getDataStrConfig(
            self.config, 'DEFAULT', 'TEST_DATA_FILE_NAME')
        self.transformed_data_folder = self.getDataStrConfig(
            self.config, 'DEFAULT', 'TRANSFORMED_DATA_FOLDER')
        self.transformed_data_file_name = self.getDataStrConfig(
            self.config, 'DEFAULT', 'TRANSFORMED_DATA_FILE_NAME')
        self.category_mapping_folder = self.getDataStrConfig(
            self.config, 'DEFAULT', 'CATEGORY_MAPPING_FOLDER')
        self.category_mapping_file_name = self.getDataStrConfig(
            self.config, 'DEFAULT', 'CATEGORY_MAPPING_FILE_NAME')
        self.cus_cat_couple_list_folder = self.getDataStrConfig(
            self.config, 'DEFAULT', 'CUS_CAT_COUPLE_LIST_FOLDER')
        self.cus_cat_couple_list_file_name = self.getDataStrConfig(
            self.config, 'DEFAULT', 'CUS_CAT_COUPLE_LIST_FILE_NAME')

        # define information db SPU
        self.aimluser = self.getDataStrConfig(
            self.config, 'SPU_AIML_DB', 'USERNAME')
        self.aimlpwd = self.getDataStrConfig(
            self.config, 'SPU_AIML_DB', 'PASSWORD')
        self.aimlhost = self.getDataStrConfig(
            self.config, 'SPU_AIML_DB', 'HOST')
        self.aimlport = self.getDataStrConfig(
            self.config, 'SPU_AIML_DB', 'PORT')
        self.aimldb = self.getDataStrConfig(
            self.config, 'SPU_AIML_DB', 'DATABASE_NAME')

        # define Robot config
        self.chunk_size = int(self.getDataStrConfig(
            self.config, 'ROBOTCONFIG', 'CHUNK_SIZE'))
        self.day_threshold = int(self.getDataStrConfig(
            self.config, 'ROBOTCONFIG', 'DAY_THRESHOLD'))
        self.split_history_present = int(self.getDataStrConfig(
            self.config, 'ROBOTCONFIG', 'SPLIT_HISTORY_PRESENT'))
        self.default_mean = float(self.getDataStrConfig(
            self.config, 'ROBOTCONFIG', 'DEFAULT_MEAN'))
        self.default_std = float(self.getDataStrConfig(
            self.config, 'ROBOTCONFIG', 'DEFAULT_STD'))
        # define is transfer data to CTS
        # self.transfer_score = self.getDataBooleanConfig(
        #     self.config, 'ACTION_CTS', 'TRANSFER_DATASCORE')


    @classmethod
    def getDataStrConfig(self, config, parent, child):
        config.sections()
        return config[parent][child]

    @classmethod
    def getDataBooleanConfig(self, config, parent, child):
        config.sections()
        return config[parent].getboolean(child)
