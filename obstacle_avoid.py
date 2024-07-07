import numpy as np
import time
from path_planner_4 import FRONT_DIST

TOO_CLOSE_DIST = 40 # cm
PURPLE_CUTOFF = 3
BLUE = True
YELLOW = False
memory = [None, time.time()] # the first element is the colour, 
# and second element is the time when the colour was determined

def colour_change(blueTrans:np.ndarray, yellowTrans:np.ndarray, purpleTrans:np.ndarray):
    rightBlue = blueTrans[blueTrans[::,0] > -30]
    rightBlue = rightBlue[rightBlue[::,1] < 120]
    leftYellow = yellowTrans[yellowTrans[::,0] > -30]
    leftYellow = leftYellow[leftYellow[::,1] < 120]

    purple_lowest_y = np.min(purpleTrans[::,1])
    newPurple = purpleTrans[purpleTrans[::, 1] < (purple_lowest_y + PURPLE_CUTOFF)]
    purple_highest_x_index = np.argmax(newPurple[::, 0])
    purple_highest_x = newPurple[purple_highest_x_index]

    dist_purple_blue = 21 # intialise to a random value

    ### decision based on multiple frames using the memory global variable
    global memory

    nearBlue = rightBlue[rightBlue[::,1] < FRONT_DIST] # imported from path_planner_4
    if nearBlue.size > 0:
        distances = np.linalg.norm(nearBlue - purple_highest_x, axis = 1)
        dist_purple_blue = np.min(distances)

        if dist_purple_blue < TOO_CLOSE_DIST:
            memory = [BLUE, time.time()]
            newBlue = np.concatenate((rightBlue, purpleTrans), axis=0)
            return newBlue, leftYellow, True
        else:
            memory = [YELLOW, time.time()]
            newYellow = np.concatenate((leftYellow, purpleTrans), axis=0)
            return rightBlue, newYellow, False
    else: # no enough data in current frame
        if time.time() - memory[1] > 1: # remember for 1 sec
            if memory[0] is not None:
                print("colour_change(): end of remembering state", memory[0])
            memory[0] = None
        
        if memory[0] == BLUE:
            newBlue = np.concatenate((rightBlue, purpleTrans), axis=0)
            return newBlue, leftYellow, True
        else: # includes the case when both current frame and memory failed to predict due to lack of data
            newYellow = np.concatenate((leftYellow, purpleTrans), axis=0)
            return rightBlue, newYellow, False
    
    # if rightBlue.size > 0 and dist_purple_blue < TOO_CLOSE_DIST: # go left, purple points get treated as blue points
    #     newBlue = np.concatenate((rightBlue, purpleTrans), axis=0)
    #     return newBlue, leftYellow, True
    # else: # go right, purple points get treated as yellow points
    #     newYellow = np.concatenate((leftYellow, purpleTrans), axis=0)
    #     return rightBlue, newYellow, False
