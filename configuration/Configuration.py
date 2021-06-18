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
        self.save_dir_log = self.getDataStrConfig(
            self.config, 'DEFAULT', 'SAVE_DIR_LOG')
        self.log_name = self.getDataStrConfig(
            self.config, 'DEFAULT', 'LOG_NAME')
        self.train_data_folder = self.getDataStrConfig(
            self.config, 'DEFAULT', 'TRAIN_DATA_FOLDER')
        self.train_data_folder_with_breaking_files = self.getDataStrConfig(
            self.config, 'DEFAULT', 'TRAIN_DATA_FOLDER_WITH_BREAKING_FILES')
        self.train_data_file_name = self.getDataStrConfig(
            self.config, 'DEFAULT', 'TRAIN_DATA_FILE_NAME')
        self.test_data_folder_with_breaking_files = self.getDataStrConfig(
            self.config, 'DEFAULT', 'TEST_DATA_FOLDER_WITH_BREAKING_FILES')
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
        self.date_to_PID_folder = self.getDataStrConfig(
            self.config, 'DEFAULT', 'DATE_TO_PID_FOLDER')
        self.date_to_PID_file_name = self.getDataStrConfig(
            self.config, 'DEFAULT', 'DATE_TO_PID_FILE_NAME')
        self.predicted_date_folder = self.getDataStrConfig(
            self.config, 'DEFAULT', 'PREDICTED_DATE_FOLDER')
        self.predicted_date_file_name = self.getDataStrConfig(
            self.config, 'DEFAULT', 'PREDICTED_DATE_FILE_NAME')
        self.prediction_results_folder = self.getDataStrConfig(
            self.config, 'DEFAULT', 'PREDICTION_RESULTS_FOLDER')
        self.day_eliminated_category_mapping_file_name = self.getDataStrConfig(
            self.config, 'DEFAULT', 'DAY_ELIMINATED_CATEGORY_MAPPING_FILE_NAME')
        self.day_and_live_indicator_eliminated_category_mapping_file_name = self.getDataStrConfig(
            self.config, 'DEFAULT', 'DAY_AND_LIVE_INDICATOR_ELIMINATED_CATEGORY_MAPPING_FILE_NAME')
        self.vs_sport_only_category_mapping_file_name = self.getDataStrConfig(
            self.config, 'DEFAULT', 'VS_SPORT_ONLY_CATEGORY_MAPPING_FILE_NAME')
        self.cus_cat_couple_list_folder = self.getDataStrConfig(
            self.config, 'DEFAULT', 'CUS_CAT_COUPLE_LIST_FOLDER')
        self.cus_cat_couple_list_file_name = self.getDataStrConfig(
            self.config, 'DEFAULT', 'CUS_CAT_COUPLE_LIST_FILE_NAME')
        self.app_name = self.getDataStrConfig(self.config, 'DEFAULT', 'APP_NAME')

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
        
        # define information db CTS
        self.ctsuser = self.getDataStrConfig(
            self.config, 'CTS_DataCenter_DB', 'USERNAME')
        self.ctspwd = self.getDataStrConfig(
            self.config, 'CTS_DataCenter_DB', 'PASSWORD')
        self.ctshost = self.getDataStrConfig(
            self.config, 'CTS_DataCenter_DB', 'HOST')
        self.ctsport = self.getDataStrConfig(
            self.config, 'CTS_DataCenter_DB', 'PORT')
        self.ctsdb = self.getDataStrConfig(
            self.config, 'CTS_DataCenter_DB', 'DATABASE_NAME')

        # define Robot config
        self.chunk_size = int(self.getDataStrConfig(
            self.config, 'ROBOTCONFIG', 'CHUNK_SIZE'))
        self.is_hard_classified = int(self.getDataStrConfig(
            self.config, 'ROBOTCONFIG', 'IS_HARD_CLASSIFIED'))
        self.day_threshold = int(self.getDataStrConfig(
            self.config, 'ROBOTCONFIG', 'DAY_THRESHOLD'))
        self.split_history_present = int(self.getDataStrConfig(
            self.config, 'ROBOTCONFIG', 'SPLIT_HISTORY_PRESENT'))
        self.amplitude = int(self.getDataStrConfig(
            self.config, 'ROBOTCONFIG', 'AMPLITUDE'))
        self.default_mean = float(self.getDataStrConfig(
            self.config, 'ROBOTCONFIG', 'DEFAULT_MEAN'))
        self.default_std = float(self.getDataStrConfig(
            self.config, 'ROBOTCONFIG', 'DEFAULT_STD'))
        self.test_dead_line = self.getDataStrConfig(
            self.config, 'ROBOTCONFIG', 'TEST_DEAD_LINE')
        self.min_bet_count_training = int(self.getDataStrConfig(
            self.config, 'ROBOTCONFIG', 'MIN_BET_COUNT_TRAINING'))
        self.min_bet_count_testing = int(self.getDataStrConfig(
            self.config, 'ROBOTCONFIG', 'MIN_BET_COUNT_TESTING'))
        self.length_of_training = int(self.getDataStrConfig(
            self.config, 'ROBOTCONFIG', 'LENGTH_OF_TRAINING'))
        self.length_of_testing = int(self.getDataStrConfig(
            self.config, 'ROBOTCONFIG', 'LENGTH_OF_TESTING'))
        
        # define if a telegramm message is sent
        self.agree_to_send_message = self.getDataBooleanConfig(
            self.config, 'ACTION_TELEGRAM', 'AGREE_TO_SEND_MESSAGE')
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

ENV = 'LOCAL'
config = SystemConfig(ENV.lower() + '_' + "config.ini", ENV)