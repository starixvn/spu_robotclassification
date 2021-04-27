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

    start = time.time()
    data = Utilities.read_data(config.train_data_folder, config.train_data_file_name)
    data = Utilities.preprocess_data(data, cat_map)
    print("read_data & preprocess_data %.2f seconds" % (time.time() - start))

    start = time.time()
    features_df = DataTransformer.transform(data)
    print("transform",(time.time() - start))

    Utilities.save_data(config.transformed_data_folder, config.transformed_data_file_name, features_df)
    print("save_data",(time.time() - start))

    start = time.time()
    train_data = Utilities.read_data(config.transformed_data_folder, config.transformed_data_file_name)
    training_results_full_info_list, cat_cus_couple_dataframe = TrainingModelController.train_model(train_data, cat_map, config.day_threshold, config.split_history_present)
    print("train_model %.2f seconds" % (time.time() - start))

    start = time.time()
    DB_Interaction.insert_to_TrainingResults_table(training_results_full_info_list, data.ReportDate.max(), config)
    print("insert_to_TrainingResults_table %.2f seconds" % (time.time() - start))

    Utilities.save_data(config.cus_cat_couple_list_folder, config.cus_cat_couple_list_file_name, cat_cus_couple_dataframe)

    cat_cus_couple_dataframe = Utilities.read_data(config.cus_cat_couple_list_folder, config.cus_cat_couple_list_file_name)
    print("cat_cus_couple_dataframe\n", cat_cus_couple_dataframe.head())

    test_data = Utilities.read_data(config.test_data_folder, config.test_data_file_name)

    PredictionController.make_predictions_right_after_training_phase((cat_cus_couple_dataframe, config, test_data.ReportDate.min()))

    test_data = Utilities.preprocess_data(test_data, cat_map)

    print("AFTER PREPROCESS | test_data\n", test_data.head())

    PredictionController.execute(test_data, config)