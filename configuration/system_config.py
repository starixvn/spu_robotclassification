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
        self.raw_data_folder = self.getDataStrConfig(
            self.config, 'DEFAULT', 'RAW_DATA_FOLDER')
        self.raw_data_file_name = self.getDataStrConfig(
            self.config, 'DEFAULT', 'RAW_DATA_FILE_NAME')
        self.transformed_data_folder = self.getDataStrConfig(
            self.config, 'DEFAULT', 'TRANSFORMED_DATA_FOLDER')
        self.transformed_data_file_name = self.getDataStrConfig(
            self.config, 'DEFAULT', 'TRANSFORMED_DATA_FILE_NAME')
        self.category_mapping_folder = self.getDataStrConfig(
            self.config, 'DEFAULT', 'CATEGORY_MAPPING_FOLDER')
        self.category_mapping_file_name = self.getDataStrConfig(
            self.config, 'DEFAULT', 'CATEGORY_MAPPING_FILE_NAME')

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
