from RobotClassificationManagement.robot_classification_manager import RobotClassificationManager
from tqdm import tqdm
import time
if __name__=='__main__':

    str_to_id, id_to_str = RobotClassificationManager.transform_category_mapping()

    # data, end_training_date = RobotClassificationManager.read_and_preprocess_data(str_to_id, is_training = 1)

    # features_df = RobotClassificationManager.transform_data(data, id_to_str)

    # RobotClassificationManager.save_transformed_data(features_df)

    train_data = RobotClassificationManager.read_transformed_data()

    test_data, start_predict_date = RobotClassificationManager.read_and_preprocess_data(str_to_id, is_training = 0)

    for PID in range(10004,10005):

        start_running = RobotClassificationManager.start(PID)

        robotConfig = RobotClassificationManager.get_robot_config()

        # start_running = time.time()

        RobotClassificationManager.insert_to_RobotClassifyHyperParams_table(robotConfig)


        #===========================================================================================================================================

        training_results_full_info_list, cat_cus_couple_dataframe = RobotClassificationManager.train_model(robotConfig, train_data, str_to_id, PID)

        RobotClassificationManager.insert_to_TrainResult_Table(training_results_full_info_list, "2021-03-31")

        RobotClassificationManager.save_cat_cus_couple_dataframe(cat_cus_couple_dataframe)

        cat_cus_couple_dataframe = RobotClassificationManager.read_cat_cus_couple_dataframe()

        RobotClassificationManager.make_predictions_right_after_training_phase(robotConfig, cat_cus_couple_dataframe, start_predict_date, PID)

        RobotClassificationManager.make_predictions_from_test_data(robotConfig, test_data, start_running, PID)