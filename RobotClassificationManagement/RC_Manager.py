import time
from RobotClassificationManagement.robot_classification_tasks import RobotClassificationTasks

class RC_Manager():

    @staticmethod
    def run(is_day_eliminated = 1, is_live_indicator_eliminated = 0, is_bettype_eliminated = 0, is_entire = 0):

        start_running = time.time()

        str_to_id, id_to_str = RobotClassificationTasks.transform_category_mapping(is_day_eliminated = is_day_eliminated, 
                                                                                    is_live_indicator_eliminated = is_live_indicator_eliminated,
                                                                                    is_bettype_eliminated = is_bettype_eliminated)

        land_marks = RobotClassificationTasks.get_land_marks()

        # print("land_marks\n", land_marks)

        for predict_date, PID in land_marks.items():
            _ = RC_Manager.get_answers(predict_date, str_to_id, start_running, is_entire)
            # if start_date_of_answer is None:
            RC_Manager.get_predictions(predict_date, PID, str_to_id, id_to_str, is_entire)
   
    @staticmethod
    def get_predictions(predict_date, PID, str_to_id, id_to_str, is_entire):

        RobotClassificationTasks.start(PID, predict_date, is_training = True)

        start_date_of_training, _ = RobotClassificationTasks.get_start_date(predict_date)

        data, _ = RobotClassificationTasks.read_and_preprocess_data(str_to_id, is_training = 1, is_aggregated = 0, is_entire = is_entire, 
                                                                    start_date = start_date_of_training)

        features_df = RobotClassificationTasks.transform_data(data, str_to_id, id_to_str)
    
        RobotClassificationTasks.save_transformed_data(features_df)

        train_data = RobotClassificationTasks.read_transformed_data()

        training_results_full_info_list, cat_cus_couple_dataframe = RobotClassificationTasks.train_model(train_data, str_to_id, PID)

        RobotClassificationTasks.insert_to_TrainResult_Table(training_results_full_info_list, predict_date) # "2021-03-31"

        RobotClassificationTasks.save_cat_cus_couple_dataframe(cat_cus_couple_dataframe)

        cat_cus_couple_dataframe = RobotClassificationTasks.read_cat_cus_couple_dataframe()

        prediction_results = RobotClassificationTasks.make_predictions_right_after_training_phase(cat_cus_couple_dataframe, predict_date, PID)

        RobotClassificationTasks.save_prediction_results(prediction_results, PID)
    
    @staticmethod
    def get_answers(predict_date, str_to_id, start_running, is_entire):

        start_date_of_answer, PID = RobotClassificationTasks.get_start_date(predict_date, is_training = False)

        RobotClassificationTasks.start(PID, start_date_of_answer, is_training = False)

        if start_date_of_answer is None:
            return None
        else:
            test_data, test_date = RobotClassificationTasks.read_and_preprocess_data(str_to_id, is_training = 0, is_aggregated = 1, is_entire = is_entire, 
                                                                                    start_date = start_date_of_answer)
            
            RobotClassificationTasks.get_answer_from_test_data(test_data, start_running, PID, test_date)

            return start_date_of_answer