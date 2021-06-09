from RobotClassificationManagement.robot_classification_manager import RobotClassificationManager
from tqdm import tqdm
import time
if __name__=='__main__':

    land_marks = ["2021-04-" + str(x).zfill(2) for x in range(1, 17, 15)]

    # land_marks = ["2021-03-17", "2021-04-16"]

    land_marks = sorted(land_marks)

    is_day_eliminated = 1
    is_live_indicator_eliminated = 0
    is_bettype_eliminated = 0
    is_entire = 0
    PID = 15

    print("land_marks\n", land_marks)

    for idx, land_mark in enumerate(land_marks):

        if idx + 1 >= len(land_marks):
            continue
        PID = PID + idx
        predict_date = land_mark
        test_date = land_marks[idx + 1]

        start_running = RobotClassificationManager.start(PID, predict_date, predict_date)

        str_to_id, id_to_str = RobotClassificationManager.transform_category_mapping(is_day_eliminated = is_day_eliminated, 
                                                                                    is_live_indicator_eliminated = is_live_indicator_eliminated,
                                                                                    is_bettype_eliminated = is_bettype_eliminated)

        start_date_of_training = RobotClassificationManager.get_start_date_of_training(land_mark)

        data, end_training_date = RobotClassificationManager.read_and_preprocess_data(str_to_id, is_training = 1, is_aggregated = 0, is_entire = is_entire, 
                                                                                    start_date = start_date_of_training, is_day_eliminated = is_day_eliminated,
                                                                                    is_live_indicator_eliminated = is_live_indicator_eliminated,
                                                                                    is_bettype_eliminated = is_bettype_eliminated)

        features_df = RobotClassificationManager.transform_data(data, str_to_id, id_to_str)
    
        RobotClassificationManager.save_transformed_data(features_df)

        train_data = RobotClassificationManager.read_transformed_data()

        training_results_full_info_list, cat_cus_couple_dataframe = RobotClassificationManager.train_model(train_data, str_to_id, PID)

        RobotClassificationManager.insert_to_TrainResult_Table(training_results_full_info_list, end_training_date) # "2021-03-31"

        RobotClassificationManager.save_cat_cus_couple_dataframe(cat_cus_couple_dataframe)

        cat_cus_couple_dataframe = RobotClassificationManager.read_cat_cus_couple_dataframe()

        prediction_results = RobotClassificationManager.make_predictions_right_after_training_phase(cat_cus_couple_dataframe, predict_date, PID)

        test_data, _ = RobotClassificationManager.read_and_preprocess_data(str_to_id, is_training = 0, is_aggregated = 1, is_entire = is_entire, 
                                                                        start_date = land_mark, is_day_eliminated = is_day_eliminated, 
                                                                        is_live_indicator_eliminated = is_live_indicator_eliminated,
                                                                        is_bettype_eliminated = is_bettype_eliminated)

        RobotClassificationManager.get_answer_from_test_data(test_data, start_running, PID, test_date, prediction_results)

        # RobotClassificationManager.truncate_TrainResults_table()
