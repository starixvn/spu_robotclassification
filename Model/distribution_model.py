import numpy as np
# import matplotlib.pyplot as plt
from math import gamma

class DistributionModel():
    def __init__(self, init_num_win, init_num_lose,a = 2, 
                b = 2, points = 101, width = 15 ,height = 5):
        self.init_num_win = init_num_win
        self.init_num_lose = init_num_lose
        self.a = a
        self.b = b
        self.A = self.init_num_win + self.a
        self.B = self.init_num_lose + self.b
        self.C = self.A + self.B
        self.points = points
        self.muy_arr = np.linspace(0, 1, self.points)
        self.width = width
        self.height = height

    def get_posterior(self):
        """Actually this is beta function"""
        numerator = gamma(self.C)*self.muy_arr**(self.A-1)*(1-self.muy_arr)**(self.B-1)
        denominator = gamma(self.A)*gamma(self.B)
        return numerator / denominator



    def update_hyper_params(self, delta_a, delta_b):
        self.obser_win = delta_a
        self.obser_lose = delta_b
        self.a = self.a + self.obser_win
        self.b = self.b + self.obser_lose
        self.A = self.init_num_win+self.a
        self.B = self.init_num_lose+self.b
        self.C = self.A + self.B

    def visualize_current_posterior(self):

        posterior = self.get_posterior()

        print("a = %.2f | b = %.2f" % (self.a,self.b) )

        mode = self.get_mode()
        std = self.get_std()

        plt.figure(figsize=(self.width, self.height))
        plt.xticks(ticks=np.linspace(0, 1, int(.5*(self.points-1)+1)))

        if not self.obser_win and not self.obser_lose:
            print("No Additional Observations")
            plt.plot(self.muy_arr, posterior)

        else:
            print("Has been Recorded !")
            plt.plot(self.muy_arr, posterior)
        plt.title("Mode %.4f | STD %.4f" % (mode, std),fontsize=30)
        plt.show()
    
    
    def compute_deltas(self, margin, outstanding_TO_score, outstanding_BC_score, streak, amplitude):
        """
        >>> Input   :   margin      , a float number in range[-1,1]
                        streak      , an integer
        >>> Output  :   delta_a     , a float number
                        delta_b     , a float number
        """
        if abs(margin) > 1:
            margin = int(margin/abs(margin))
        if margin > 0:
            # return amplitude*margin*(1 + outstanding_TO_score*abs(streak)), 0 
            return amplitude*(margin+2*outstanding_TO_score)/3*(1 + (streak - 1)/10), 0
        else:
            return 0, amplitude*(abs(margin)+2*outstanding_TO_score)/3*(1 + (abs(streak) - 1)/10) # 

    def get_mode(self):
        try :
            return (self.A-1) / (self.C-2)
        except ZeroDivisionError:
            print(self.a, self.b)
            return None

    def get_std(self):
        return np.sqrt( (self.A)*(self.B) / (self.C)**2 / (self.C+1) )
