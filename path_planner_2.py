import numpy as np
OPTIMAL_SIDE_DISTANCE = 30 # cm

def simple_diff_path_planner(blueTrans:np.ndarray, yellowTrans:np.ndarray, purpleTrans:np.ndarray):
        # rightBlue = blueTrans[blueTrans[::, 0] > 0]
        # leftYellow = yellowTrans[yellowTrans[::, 0] < 0]
    rightBlue = blueTrans[blueTrans[::,0] > -30]
    rightBlue = rightBlue[rightBlue[0,::] < 120]
    leftYellow = yellowTrans
    if rightBlue.size == 0 and leftYellow.size == 0: # no data
        return 0, 90

    if rightBlue.size > leftYellow.size: # follow the blue
        blueMiddle = rightBlue[rightBlue[::,0] < 30]
        x = rightBlue[::,0]
        if blueMiddle.size > 5:
            angle = blueMiddle.size
        # refX = OPTIMAL_SIDE_DISTANCE
        # x, y = rightBlue[::, 0], rightBlue[::, 1]
        elif np.mean(x) > 50:
    
    else: # follow the yellow
        refX = -OPTIMAL_SIDE_DISTANCE
        x, y = leftYellow[::, 0], leftYellow[::, 1]

    x = x[y < 160]
    diff = x - refX
    averageDiff = np.mean(diff)
    angle = -averageDiff
    speed = 150
    angle = min(80, max(-80, angle))
    return angle, speed