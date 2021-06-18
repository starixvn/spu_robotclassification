import numpy as np
import pandas as pd
from Utilities.Data_Preprocessing_Manager import Data_Preprocessing_Manager
from Model.distribution_model import DistributionModel

class TrainingModelController():

    @staticmethod
    def build_prior(history):
        m, l = len(history[history>0]), len(history[history<0])
        cus = DistributionModel(m, l)
        return cus

    @staticmethod
    def build_posterior(cus, present, outstanding_TO_array, outstanding_BC_array, amplitude):

        if present[0] > 0:
            streak = 1
        else:
            streak = -1
        outstanding_TO_score = outstanding_TO_array[0]
        outstanding_BC_score = outstanding_BC_array[0]
        delta_a, delta_b = cus.compute_deltas(present[0], outstanding_TO_score, outstanding_BC_score, streak, amplitude)
        cus.update_hyper_params(delta_a,delta_b)
        for day in range(1, len(present)):
            outstanding_TO_score = outstanding_TO_array[day]
            outstanding_BC_score = outstanding_BC_array[day]
            if present[day]*present[day-1] > 0:
                streak += int(present[day]/abs(present[day]))
                delta_a,delta_b = cus.compute_deltas(present[day], outstanding_TO_score, outstanding_BC_score, streak, amplitude)
                cus.update_hyper_params(delta_a, delta_b)
            else:
                if present[day] > 0:
                    streak = 1
                else:
                    streak = -1
                delta_a, delta_b = cus.compute_deltas(present[day], outstanding_TO_score, outstanding_BC_score, streak, amplitude)
                cus.update_hyper_params(delta_a, delta_b)
        return cus, streak

    @staticmethod
    def process_a_margin_array(margin_array, outstanding_TO_array, outstanding_BC_array, split, amplitude):
        """
        Process profile for a single customer
        Also apply winning/losing streak !
        >>> Input   :   margin_array            , a numpy array containing margin versus days of a customer
                        outstanding_TO_array    , a numpy array containing outstanding score with respect to Tunrover
                        split                   , a float how much percent of array used to establish prior
        
        >>> Output  :   mode          , a float number tells the value of peak of beta distribution
                        std           , a float number tells the standard deivation
        """
        num_effective_days = len(margin_array)
        split_point = int(np.floor(split*num_effective_days))
        history, present = margin_array[:split_point], margin_array[split_point:]
        outstanding_TO_array = outstanding_TO_array[split_point:]
        cus = TrainingModelController.build_prior(history)
        cus, streak = TrainingModelController.build_posterior(cus, present, outstanding_TO_array, outstanding_BC_array, amplitude)
        mode = cus.get_mode()
        return mode, cus.a, cus.b, streak, num_effective_days

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
        # print("cat_df\n", cat_df.head())
        training_results_daily_info_list = []
        cat_cus_couple_daily_list = []
        for custid in cat_df.index:
            turn_over_sequence = cat_df.loc[custid, category + 'TO_sequence']
            turn_over_accummulated = float(cat_df.loc[custid, category + 'TO_accummulated'])
            # if turn_over_accummulated < 1e-3:
            turn_over_accummulated = round(turn_over_accummulated, 4)
            bet_count_accummulated = int(cat_df.loc[custid, category + 'BC_accummulated'])
            win_loss_sequence = cat_df.loc[custid, category + 'WL_sequence']
            
            
            num_active_days = cat_df.loc[custid, category + '_num_active_days']
            if num_active_days == 0:
                continue
            # outstanding_BC = cat_df.loc[custid, category + 'BC_out'] / num_active_days
            outstanding_BC_sequence = cat_df.loc[custid, category + 'BC_out']
            outstanding_BC_array = np.array([float(x) for x in outstanding_BC_sequence.split(',') if x != ''])
            outstanding_BC = np.mean(outstanding_BC_array)
            # outstanding_TO = cat_df.loc[custid, category + 'TO_out'] / num_active_days
            outstanding_TO_sequence = cat_df.loc[custid, category + 'TO_out']
            outstanding_TO_array = np.array([float(x) for x in outstanding_TO_sequence.split(',') if x != ''])
            outstanding_TO = np.mean(outstanding_TO_array)
            # internal_BC = cat_df.loc[custid, category + 'BC_in'] / num_active_days
            # internal_TO = cat_df.loc[custid, category + 'TO_in'] / num_active_days
            internal_BC_sequence = cat_df.loc[custid, category + 'BC_in']
            internal_BC_array = np.array([float(x) for x in internal_BC_sequence.split(',') if x != ''])
            internal_BC = np.mean(internal_BC_array)
            internal_TO_sequence = cat_df.loc[custid, category + 'TO_in']
            internal_TO_array = np.array([float(x) for x in internal_TO_sequence.split(',') if x != ''])
            internal_TO = np.mean(internal_TO_array)
            turn_over_array = np.array([float(x) for x in turn_over_sequence.split(',') if x != ''])
            win_loss_array = np.array([float(x) for x in win_loss_sequence.split(',') if x != ''])
            accummulated_win_loss = np.sum(win_loss_array)
            training_negative_WL_per_day = round(np.mean(win_loss_array[win_loss_array < 0]), 4)
            training_positive_WL_per_day = round(np.mean(win_loss_array[win_loss_array > 0]), 4)
            margin_array = win_loss_array / turn_over_array

            # round 1 filter
            filtered_margin_array =  margin_array #margin_array[margin_array != 0]
            outstanding_TO_array = outstanding_TO_array #outstanding_TO_array[margin_array != 0]

            # round 2 filter
            # if len(filtered_margin_array) >= threshold_activ_days :
            mode, _, _, streak, num_active_days = TrainingModelController.process_a_margin_array(filtered_margin_array, outstanding_TO_array, outstanding_BC_array, split, amplitude)
            training_results_daily_info_list.append({'C':custid, 'M':mode, 'SWD':training_positive_WL_per_day, 'SLD':training_negative_WL_per_day, 'STR':streak, 'CAT':categoryID, 
                                                    'AD':num_active_days, 'PID':PID,"OBC":outstanding_BC, "OTO":outstanding_TO, "IBC":internal_BC, "ITO":internal_TO})
            cat_cus_couple_daily_list.append({"CAT":categoryID, "C":custid, "AccWL":accummulated_win_loss})
        # print("training_results_daily_info_list\n", training_results_daily_info_list[:5])
        return training_results_daily_info_list, cat_cus_couple_daily_list

    def train_model(transformed_train_data, str_to_id, day_threshold, split_history_present, amplitude, PID):
        training_results_full_info_list = []
        cat_cus_couple_full_list = []
        categories = str_to_id.keys()
        transformed_train_data = transformed_train_data.set_index('C')
        # test_arr = transformed_train_data.loc[13515302, "s1b1NLWL_sequence"]
        # print("test_arr = " + test_arr)
        no_gain_count = 0
        for category in categories:
            cat_df = Data_Preprocessing_Manager.filter_categorie(category, transformed_train_data)
            if len(cat_df.index) == 0:
                no_gain_count += 1
                print(f"No gain from this category {no_gain_count} !")
                continue
            categoryID = str_to_id[category]['CategoryID']
            training_results_daily_info_list, cat_cus_couple_daily_list = TrainingModelController.create_full_info_training_results(category, cat_df, categoryID, day_threshold, split_history_present, amplitude, PID)
            training_results_full_info_list += training_results_daily_info_list
            cat_cus_couple_full_list += cat_cus_couple_daily_list
        training_results_full_info_df = pd.DataFrame(training_results_full_info_list)
        training_results_full_info_df = training_results_full_info_df.dropna()
        training_results_full_info_list = training_results_full_info_df.to_dict(orient = 'records')
        print("cat_cus_couple_full_list = " + str(cat_cus_couple_full_list[:5]))
        print("training_results_full_info_df\n", training_results_full_info_df.sample(5))
        return training_results_full_info_list, pd.DataFrame(cat_cus_couple_full_list)
