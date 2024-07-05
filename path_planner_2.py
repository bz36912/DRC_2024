import numpy as np
from car_remote_control import Uart
OPTIMAL_SIDE_DISTANCE = 30 # cm

def simple_diff_path_planner(blueTrans:np.ndarray, yellowTrans:np.ndarray, purpleTrans:np.ndarray, uart:Uart):
        # rightBlue = blueTrans[blueTrans[::, 0] > 0]
        # leftYellow = yellowTrans[yellowTrans[::, 0] < 0]
    rightBlue = blueTrans[blueTrans[::,0] > -30]
    rightBlue = rightBlue[rightBlue[::,1] < 120]
    leftYellow = yellowTrans[yellowTrans[::,0] > -30]
    leftYellow = leftYellow[leftYellow[::,1] < 120]
    # leftYellow = yellowTrans
    if rightBlue.size == 0 and leftYellow.size == 0: # no data
        return 0, 130

    if rightBlue.size > leftYellow.size: # follow the blue
        blueMiddle = rightBlue[rightBlue[::,0] < 40]
        x = rightBlue[::,0]
        if blueMiddle.size > 5:
            angle = blueMiddle.size/5
        # refX = OPTIMAL_SIDE_DISTANCE
        # x, y = rightBlue[::, 0], rightBlue[::, 1]
        elif np.mean(x) > 50:
            angle = -np.mean(x)+50
        else:
            angle = 0
    
    else: # follow the yellow
        # refX = -OPTIMAL_SIDE_DISTANCE
        # x, y = leftYellow[::, 0], leftYellow[::, 1]
        yellowMiddle = leftYellow[leftYellow[::,0] > -40]
        x = leftYellow[::,0]
        angle = -yellowMiddle.size
        # refX = OPTIMAL_SIDE_DISTANCE
        # x, y = rightBlue[::, 0], rightBlue[::, 1]
        
    

    # x = x[y < 160]
    # diff = x - refX
    # averageDiff = np.mean(diff)
    # angle = -averageDiffq
    # speed = 150
    angle = min(80, max(-80, angle/5))
    if (abs(angle)<10):
        speed = 110
    elif (abs(angle) > 60):
        speed = -10
        angle = 0
        if (angle > 0):
            uart.swing_left()
        else: 
            uart.swing_right()
    else: 
        speed = 130
    return angle, speed