import numpy as np
OPTIMAL_SIDE_DISTANCE = 30 # cm
MAX_X = 100
MAX_Y = 120
TOO_BIG = 50

def _region_of_interest(blueTrans:np.ndarray, yellowTrans:np.ndarray, purpleTrans:np.ndarray):
    rightBlue = blueTrans[blueTrans[::,0] > -OPTIMAL_SIDE_DISTANCE]
    rightBlue = rightBlue[rightBlue[::,0] < MAX_X]
    rightBlue = rightBlue[rightBlue[::,1] < MAX_Y]
    rightBlue = rightBlue[rightBlue[::,1] > 0]
    leftYellow = yellowTrans[yellowTrans[::,0] < OPTIMAL_SIDE_DISTANCE]
    leftYellow = leftYellow[leftYellow[::,0] > -MAX_X]
    leftYellow = leftYellow[leftYellow[::,1] < MAX_Y]
    leftYellow = leftYellow[leftYellow[::,1] > 0]
    return rightBlue, leftYellow

COLLISION_IDX = 30/(MAX_Y - 30)**2
APPROACH_IDX = 1.5

def weight_average_path_planner(blueTrans:np.ndarray, yellowTrans:np.ndarray, purpleTrans:np.ndarray):
    # define the region of interest in the xy plane
    rightBlue, leftYellow = _region_of_interest(blueTrans, yellowTrans, purpleTrans)

    if rightBlue.size == 0 and leftYellow.size == 0: # no data
        return 0, 100

    if rightBlue.size > leftYellow.size: # follow the blue
        x = rightBlue[::,0]
        y = rightBlue[::,1]
        weights = np.ones_like(x)
        middleMask = x < OPTIMAL_SIDE_DISTANCE
        weights[middleMask] = COLLISION_IDX * (MAX_Y - y[middleMask])**2
        weights[x > TOO_BIG] = APPROACH_IDX
        error = OPTIMAL_SIDE_DISTANCE - x
        angle = np.average(error, weights=weights)
    else: # follow the yellow line
        x = leftYellow[::,0]
        y = leftYellow[::,1]
        weights = np.ones_like(x)
        middleMask = x > -OPTIMAL_SIDE_DISTANCE
        weights[middleMask] = COLLISION_IDX * (MAX_Y - y[middleMask])
        weights[x < -TOO_BIG] = APPROACH_IDX
        error = -OPTIMAL_SIDE_DISTANCE - x
        angle = np.average(error, weights=weights)

    angle = min(80, max(-80, angle))
    speed = 130
    return angle, speed

MIDDLE_WEIGHT = 20 # max weight applied to -30 < x < 30cm
DECAY_CONSTANT = 0.7
def proximity_path_planner(blueTrans:np.ndarray, yellowTrans:np.ndarray, purpleTrans:np.ndarray):
    rightBlue, leftYellow = _region_of_interest(blueTrans, yellowTrans, purpleTrans)

    if rightBlue.size == 0 and leftYellow.size == 0: # no data
        return 0, 100

    if rightBlue.shape[0] > 200 or rightBlue.shape[0] > leftYellow.shape[0]: # follow the blue
        x = rightBlue[::,0]
        y = rightBlue[::,1]
        weights = np.ones_like(x)
        weights[x < OPTIMAL_SIDE_DISTANCE] = MIDDLE_WEIGHT
        weights = weights * 2.71828**(-DECAY_CONSTANT * (x**2 + y**2) / 100**2)
        error = OPTIMAL_SIDE_DISTANCE - x
        angle = np.mean(weights * error)
    else: # follow the yellow line
        x = leftYellow[::,0]
        y = leftYellow[::,1]
        weights = np.ones_like(x)
        weights[x > -OPTIMAL_SIDE_DISTANCE] = MIDDLE_WEIGHT
        weights = weights * 2.71828**(-DECAY_CONSTANT * (x**2 + y**2) / 100**2)
        error = -OPTIMAL_SIDE_DISTANCE - x
        angle = np.mean(weights * error)

    angle = min(80, max(-80, angle))
    speed = 130
    return angle, speed