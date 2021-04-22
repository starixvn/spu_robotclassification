from utils import Utilities
from training_model_controller import TrainingModelController
from data_transformer import DataTransformer
from database_interaction import DB_Interaction
from configuration.system_config import SystemConfig
from prediction_controller import PredictionController

import time
ENV = 'LOCAL'
config = SystemConfig(ENV.lower() + '_' + "config.ini", ENV)

if __name__=='__main__':

    start = time.time()
    category_mapping = Utilities.read_data(config.category_mapping_folder, config.category_mapping_file_name)
    cat_map = Utilities.transform_category_mapping(category_mapping)
    print("transform_category_mapping %.2f seconds" % (time.time() - start))
    # start = time.time()
    # data = Utilities.read_data(config.raw_data_folder, config.raw_data_file_name)
    # data = Utilities.preprocess_data(data)
    # print("read_data & preprocess_data",(time.time() - start))
    # start = time.time()
    # features_df = DataTransformer.transform(data)
    # print("transform",(time.time() - start))
    # Utilities.save_data(config.transformed_data_folder, config.transformed_data_file_name, features_df)
    # print("save_data",(time.time() - start))
    start = time.time()
    train_data = Utilities.read_data(config.transformed_data_folder, config.transformed_data_file_name, index_col = 0)
    training_results_full_info_list = TrainingModelController.train_model(train_data, cat_map)
    print("train_model %.2f seconds" % (time.time() - start))
    start = time.time()
    DB_Interaction.insert_to_TrainingResults_table((training_results_full_info_list, config, "2021-04-22"))
    print("insert_to_TrainingResults_table %.2f seconds" % (time.time() - start))

    # training_results_data = DB_Interaction.get_from_TrainingResults_table()

    # test_data = Utilities.read_data()

    # predictable_full_info_list, update_only_full_info_list = PredictionController(training_results_data, test_data, cat_map)

    # DB_Interaction.insert_to_PredictedResults_table(predictable_full_info_list)

    # DB_Interaction.insert_to_TrainingResults_table(update_only_full_info_list)