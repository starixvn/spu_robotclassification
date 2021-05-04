import random

class RobotConfig():
    """description of class"""
    def __init__(self):
        # self.day_threshold = random.randint(1,20)
        # self.split_history_present = random.random()
        # self.amplitude = random.randint(1,10)
        # self.default_mean = random.random()
        # self.default_std = .5*random.random()

        # self.day_threshold = 1
        # self.split_history_present = .2268
        # self.amplitude = 1
        # self.default_mean = .5526
        # self.default_std = .0625

        self.day_threshold = 5
        self.split_history_present = 0
        self.amplitude = 1
        self.default_mean = .5
        self.default_std = .5