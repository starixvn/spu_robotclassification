from RobotClassificationManagement.robot_classification_manager import RobotClassificationManager

if __name__=='__main__':

    start_running = RobotClassificationManager.start()

    str_to_id, id_to_str = RobotClassificationManager.transform_category_mapping()

    data, end_training_date = RobotClassificationManager.read_and_preprocess_data(str_to_id, is_training = 1)

    features_df = RobotClassificationManager.transform_data(data, id_to_str)

    RobotClassificationManager.save_transformed_data(features_df)

    train_data = RobotClassificationManager.read_transformed_data()

    training_results_full_info_list, cat_cus_couple_dataframe = RobotClassificationManager.train_model(train_data, str_to_id)

    RobotClassificationManager.insert_to_TrainResult_Table(training_results_full_info_list, end_training_date)

    RobotClassificationManager.save_cat_cus_couple_dataframe(cat_cus_couple_dataframe)

    cat_cus_couple_dataframe = RobotClassificationManager.read_cat_cus_couple_dataframe()

    test_data, start_predict_date = RobotClassificationManager.read_and_preprocess_data(str_to_id, is_training = 0)

    RobotClassificationManager.make_predictions_right_after_training_phase(cat_cus_couple_dataframe, start_predict_date)

    RobotClassificationManager.make_predictions_from_test_data(test_data, start_running)