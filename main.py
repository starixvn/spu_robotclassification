import time
from RobotClassificationManagement.RC_Manager import RC_Manager

if __name__=='__main__':
    
    start_running = RC_Manager.get_predictions()
    # start_running = time.time()
    RC_Manager.get_answer(start_running)
    
