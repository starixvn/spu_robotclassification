from RobotClassificationManagement.robot_classification_tasks import RobotClassificationTasks

class RC_Manager():

    @staticmethod
    def run():

        land_marks = ["2021-04-" + str(x).zfill(2) for x in range(1, 17, 14)]

        # land_marks = ["2021-03-17", "2021-04-16"]

        land_marks = sorted(land_marks)

        is_day_eliminated = 1
        is_live_indicator_eliminated = 0
        is_bettype_eliminated = 0
        is_entire = 0
        PID = 0

        print("land_marks\n", land_marks)

        for idx, land_mark in enumerate(land_marks):

            if idx + 1 >= len(land_marks):
                continue
            PID = PID + idx
            predict_date = land_mark
            test_date = land_marks[idx + 1]

            start_running = RobotClassificationTasks.start(PID, predict_date, predict_date)

            str_to_id, id_to_str = RobotClassificationTasks.transform_category_mapping(is_day_eliminated = is_day_eliminated, 
                                                                                        is_live_indicator_eliminated = is_live_indicator_eliminated,
                                                                                        is_bettype_eliminated = is_bettype_eliminated)

            start_date_of_training = RobotClassificationTasks.get_start_date_of_training(land_mark)

            data, end_training_date = RobotClassificationTasks.read_and_preprocess_data(str_to_id, is_training = 1, is_aggregated = 0, is_entire = is_entire, 
                                                                                        start_date = start_date_of_training, is_day_eliminated = is_day_eliminated,
                                                                                        is_live_indicator_eliminated = is_live_indicator_eliminated,
                                                                                        is_bettype_eliminated = is_bettype_eliminated)

            features_df = RobotClassificationTasks.transform_data(data, str_to_id, id_to_str)
        
            RobotClassificationTasks.save_transformed_data(features_df)

            train_data = RobotClassificationTasks.read_transformed_data()

            training_results_full_info_list, cat_cus_couple_dataframe = RobotClassificationTasks.train_model(train_data, str_to_id, PID)

            RobotClassificationTasks.insert_to_TrainResult_Table(training_results_full_info_list, end_training_date) # "2021-03-31"

            RobotClassificationTasks.save_cat_cus_couple_dataframe(cat_cus_couple_dataframe)

            cat_cus_couple_dataframe = RobotClassificationTasks.read_cat_cus_couple_dataframe()

            prediction_results = RobotClassificationTasks.make_predictions_right_after_training_phase(cat_cus_couple_dataframe, predict_date, PID)

            test_data, _ = RobotClassificationTasks.read_and_preprocess_data(str_to_id, is_training = 0, is_aggregated = 1, is_entire = is_entire, 
                                                                            start_date = land_mark, is_day_eliminated = is_day_eliminated, 
                                                                            is_live_indicator_eliminated = is_live_indicator_eliminated,
                                                                            is_bettype_eliminated = is_bettype_eliminated)

            RobotClassificationTasks.get_answer_from_test_data(test_data, start_running, PID, test_date, prediction_results)

            # RobotClassificationTasks.truncate_TrainResults_table()