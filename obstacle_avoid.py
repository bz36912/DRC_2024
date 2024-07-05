import numpy as np
TOO_CLOSE_DIST = 40 # cm
PURPLE_CUTOFF = 3

def colour_change(blueTrans:np.ndarray, yellowTrans:np.ndarray, purpleTrans:np.ndarray):
    rightBlue = blueTrans[blueTrans[::,0] > -30]
    rightBlue = rightBlue[rightBlue[::,1] < 120]
    leftYellow = yellowTrans[yellowTrans[::,0] > -30]
    leftYellow = leftYellow[leftYellow[::,1] < 120]

    purple_lowest_y = np.min(purpleTrans[::,1])
    newPurple = purpleTrans[purpleTrans[::, 1] < (purple_lowest_y + PURPLE_CUTOFF)]
    purple_highest_x_index = np.argmax(newPurple[::, 0])
    purple_highest_x = newPurple[purple_highest_x_index]

    dist_purple_blue = 21

    if rightBlue.size > 0:
        distances = np.linalg.norm(rightBlue - purple_highest_x, axis = 1)
        dist_purple_blue = np.min(distances)
    
    if rightBlue.size > 0 and dist_purple_blue < TOO_CLOSE_DIST: # go left, purple points get treated as blue points
        newBlue = np.concatenate((rightBlue, newPurple), axis=0)
        return newBlue, leftYellow, True
    else: # go right, purple points get treated as yellow points
        newYellow = np.concatenate((leftYellow, newPurple), axis=0)
        return rightBlue, newYellow, False