import time
from RobotClassificationManagement.robot_classification_tasks import RobotClassificationTasks

class RC_Manager():

    @staticmethod
    def get_predictions(is_day_eliminated = 1, is_live_indicator_eliminated = 0, is_bettype_eliminated = 0, is_entire = 0):

        start_running = time.time()

        str_to_id, id_to_str = RobotClassificationTasks.transform_category_mapping(is_day_eliminated = is_day_eliminated, 
                                                                                    is_live_indicator_eliminated = is_live_indicator_eliminated,
                                                                                    is_bettype_eliminated = is_bettype_eliminated)

        land_marks = RobotClassificationTasks.get_land_marks(is_training = True)

        # print("land_marks\n", land_marks)

        for PID, predict_date in land_marks.items():

            RobotClassificationTasks.start(PID, predict_date, is_training = True)

            start_date_of_training = RobotClassificationTasks.get_start_date_of_training(predict_date)

            data, _ = RobotClassificationTasks.read_and_preprocess_data(str_to_id, is_training = 1, is_aggregated = 0, is_entire = is_entire, 
                                                                        start_date = start_date_of_training, is_day_eliminated = is_day_eliminated,
                                                                        is_live_indicator_eliminated = is_live_indicator_eliminated,
                                                                        is_bettype_eliminated = is_bettype_eliminated)

            features_df = RobotClassificationTasks.transform_data(data, str_to_id, id_to_str)
        
            RobotClassificationTasks.save_transformed_data(features_df)

            train_data = RobotClassificationTasks.read_transformed_data()

            training_results_full_info_list, cat_cus_couple_dataframe = RobotClassificationTasks.train_model(train_data, str_to_id, PID)

            RobotClassificationTasks.insert_to_TrainResult_Table(training_results_full_info_list, predict_date) # "2021-03-31"

            RobotClassificationTasks.save_cat_cus_couple_dataframe(cat_cus_couple_dataframe)

            cat_cus_couple_dataframe = RobotClassificationTasks.read_cat_cus_couple_dataframe()

            prediction_results = RobotClassificationTasks.make_predictions_right_after_training_phase(cat_cus_couple_dataframe, predict_date, PID)

            RobotClassificationTasks.save_prediction_results(prediction_results, PID)
        
        return start_running

    @staticmethod
    def get_answer(start_running, is_day_eliminated = 1, is_live_indicator_eliminated = 0, is_bettype_eliminated = 0, is_entire = 0):

        str_to_id, _ = RobotClassificationTasks.transform_category_mapping(is_day_eliminated = is_day_eliminated, 
                                                                            is_live_indicator_eliminated = is_live_indicator_eliminated,
                                                                            is_bettype_eliminated = is_bettype_eliminated)
        
        land_marks = RobotClassificationTasks.get_land_marks(is_training = False)

        for PID, land_mark in land_marks.items():

            RobotClassificationTasks.start(PID, land_mark, is_training = False)

            test_data, test_date = RobotClassificationTasks.read_and_preprocess_data(str_to_id, is_training = 0, is_aggregated = 1, is_entire = is_entire, 
                                                                                    start_date = land_mark, is_day_eliminated = is_day_eliminated, 
                                                                                    is_live_indicator_eliminated = is_live_indicator_eliminated,
                                                                                    is_bettype_eliminated = is_bettype_eliminated)
            
            RobotClassificationTasks.get_answer_from_test_data(test_data, start_running, PID, test_date)