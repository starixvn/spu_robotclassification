import numpy as np
import pandas as pd
from Helper.utils import Utilities
from Model.distribution_model import DistributionModel

class TrainingModelController():

    @staticmethod
    def build_prior(history):
        m, l = len(history[history>0]), len(history[history<0])
        cus = DistributionModel(m, l)
        return cus

    @staticmethod
    def build_posterior(cus, present, amplitude):
        streak = 1
        delta_a, delta_b = Utilities.compute_deltas(present[0], streak, amplitude)
        cus.update_hyper_params(delta_a,delta_b)
        for day in range(1, len(present)):
            if present[day]*present[day-1] > 0:
                streak = streak + 1
                delta_a, delta_b = Utilities.compute_deltas(present[day], streak, amplitude)
                cus.update_hyper_params(delta_a, delta_b)
            else:
                streak = 1
                delta_a, delta_b = Utilities.compute_deltas(present[day] ,streak, amplitude)
                cus.update_hyper_params(delta_a, delta_b)
        return cus, streak

    @staticmethod
    def process_a_margin_array(margin_array, split, amplitude):
        """
        Process profile for a single customer
        Also apply winning/losing streak !
        >>> Input   :   margin_array  , a numpy array containing margin versus days of a customer
                        split         , a float how much percent of array used to establish prior
        
        >>> Output  :   mode          , a float number tells the value of peak of beta distribution
                        std           , a float number tells the standard deivation
        """
        num_effective_days = len(margin_array)
        split_point = int(np.floor(split*num_effective_days))
        history, present = margin_array[:split_point], margin_array[split_point:]
        cus = TrainingModelController.build_prior(history)
        cus, streak = TrainingModelController.build_posterior(cus, present, amplitude)
        mode = cus.get_mode()
        return mode, cus.a, cus.b, streak, num_effective_days

    @staticmethod
    def create_full_info_training_results(category, cat_df, categoryID, threshold_activ_days, split, amplitude, PID):
        """
        Compute mode and standard deviation for each customer with a given dataset

        >>> Input   :   category              , string
                        cat_df                , dataframe of a certain category
                        threshold_activ_days  , integer that reflects the minimal number of days to filter
                        split                 , float that reflects how much percent of array used to establish prior
        
        >>> Output  :   all_draw_num          , number of customer with all results are draw
                        too_few_num           , number of customer whose number active days < threshold_activ_days
                        peak_std_dict         , dictionary whose key is custid , value is peak and std of its distribution
                        peak_std_df           , dataframe of peak_std_dict
        """
        training_results_daily_info_list = []
        cat_cus_couple_daily_list = []
        for custid in cat_df.index:
            turn_over_sequence = cat_df.loc[custid, category + 'TO_sequence']
            win_loss_sequence = cat_df.loc[custid, category + 'WL_sequence']
            turn_over_array = np.array([float(x) for x in turn_over_sequence.split(',') if x != ''])
            win_loss_array = np.array([float(x) for x in win_loss_sequence.split(',') if x != ''])
            margin_array = win_loss_array / turn_over_array

            # round 1 filter
            filtered_margin_array =  margin_array[margin_array != 0]

            # round 2 filter
            if len(filtered_margin_array) >= threshold_activ_days :
                mode, a, b, streak, num_active_days = TrainingModelController.process_a_margin_array(filtered_margin_array, split, amplitude)
                if mode is None:
                    continue
                training_results_daily_info_list.append({'C':custid, 'M':mode, 'SWD':a, 'SLD':b, 'STR':streak, 'CAT':categoryID, 'AD':num_active_days, 'PID':PID})
                cat_cus_couple_daily_list.append({"CAT":categoryID, "C":custid})
        df = pd.DataFrame(training_results_daily_info_list)
        # df = df.dropna()
        # print("df\n", df.head())
        if len(df.index) == 0:
            cat_cus_couple_daily_list = []
        training_results_daily_info_list = df.to_dict(orient = 'records')
        return training_results_daily_info_list, cat_cus_couple_daily_list

    @staticmethod
    def train_model(transformed_train_data, str_to_id, day_threshold, split_history_present, amplitude, PID):
        training_results_full_info_list = []
        cat_cus_couple_full_info_list = []
        categories = str_to_id.keys()
        transformed_train_data = transformed_train_data.set_index('C')
        # print("transformed_train_data\n", transformed_train_data.head())
        for category in categories:
            cat_df = Utilities.filter_categorie(category, transformed_train_data)
            # print("cat_df\n", cat_df.head())
            categoryID = str_to_id[category]['CategoryID']
            training_results_daily_info_list, cat_cus_couple_daily_list = TrainingModelController.create_full_info_training_results(category, cat_df, categoryID, day_threshold, split_history_present, amplitude, PID)
            training_results_full_info_list += training_results_daily_info_list
            cat_cus_couple_full_info_list += cat_cus_couple_daily_list
        # print("training_results_full_info_list\n", training_results_full_info_list)
        return training_results_full_info_list, pd.DataFrame(cat_cus_couple_full_info_list)