from scipy.stats import shapiro
from scipy.stats.distributions import norm
from utils import Utilities
from model import GB_classify

class PredictionController():

    def check_Gaussian_distribution(data):
        _, p = shapiro(data)
        if p > .05 :
            print("Probably Gaussian")
            mean, std = norm.fit(data)
        else:
            print("Probably not Gaussian")
            mean, std = .6, .3
        return mean, std

    def predict_for_a_singleton(today_mode, upper_bound, lower_bound):
        if today_mode >= upper_bound:
            win_lose_guess = 1
        elif today_mode <= lower_bound:
            win_lose_guess = 0
        return win_lose_guess
    
    def update_training_results_for_a_singleton(a, b, streak, today_margin):
        delta_a, delta_b = Utilities.compute_deltas(streak, today_margin)
        updated_a = a + delta_a
        updated_b = b + delta_b
        classifier = GB_classify(0, 0, updated_a, updated_b)
        updated_mode = classifier.get_mode()
        updated_streak = today_margin / abs(today_margin)
        if streak*today_margin > 0:
            updated_streak = streak + updated_streak
        return updated_mode, updated_a, updated_b, updated_streak

    def validate_training_results(training_results_data):
        mean, std = PredictionController.check_Gaussian_distribution(training_results_data['mode'])
        upper_bound = mean + std
        lower_bound = mean - std
        predictable_dataframe = training_results_data[(training_results_data['mode'] >= upper_bound) | (training_results_data['mode'] <= lower_bound)]
        predictable_dict = predictable_dataframe[['CustId', 'CategoryId', 'mode', 'a', 'b', 'streak']].set_index(['CustId', 'CategoryId']).to_dict(orient = 'index')
        predictable_list = predictable_dataframe['CustId'].to_list()
        return predictable_dict, predictable_list, upper_bound, lower_bound

    def unpack_data(row, predictable_dict, cat_map):
        predict_date = row.ReportDate
        custid = row.CustId
        category = cat_map[row.SporttypeId + row.BettypeId + row.IsLive + row.Day]['CategoryID']
        today_margin = row.IBCWinloss / row.IBCTurnover
        singleton_mode = predictable_dict[(custid, category)]['mode']
        singleton_a, singleton_b = predictable_dict[(custid, category)]['a'], predictable_dict[(custid, category)]['b']
        singleton_streak = predictable_dict[(custid, category)]['streak']
        return predict_date, category, custid, singleton_a, singleton_b, singleton_mode, today_margin, singleton_streak

    def execute(training_results_data, test_data, cat_map):
        update_only_full_info_list, predictable_full_info_list = [], []
        predictable_dict, predictable_list, upper_bound, lower_bound = PredictionController.validate_training_results(training_results_data)
        for row in test_data.itertuples():
            predict_date, category, custid, singleton_a, singleton_b, singleton_mode, today_margin, singleton_streak = PredictionController.unpack_data(row, predictable_dict, cat_map)
            updated_mode, updated_a, updated_b, updated_streak = PredictionController.update_training_results_for_a_singleton(singleton_a, singleton_b, singleton_streak, today_margin)
            if custid in predictable_list:
                singleton_win_or_lose_guess = PredictionController.predict_for_a_singleton(singleton_mode, upper_bound, lower_bound)
                predictable_full_info_list.append({'CustId':custid, 'CategoryId':category, 'mode':updated_mode, 'predict_date':predict_date, 
                                                    'a':updated_a, 'b':updated_b, 'streak':updated_streak, 'predict':singleton_win_or_lose_guess})

            update_only_full_info_list.append({'CustId':custid, 'CategoryId':category, 'mode':updated_mode, 
                                                'a':updated_a, 'b':updated_b, 'streak':updated_streak})
        return predictable_full_info_list, update_only_full_info_list