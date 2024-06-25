import numpy as np
import matplotlib.pyplot as plt
from typing import List

OPTIMAL_SIDE_DISTANCE = 40
EACH_STEP = True
SEGMENT_SIZE = 5
MAX_RANGE = 150
CAR_SPEED = 0.3

def MAINTAIN_get_range_quartiles(stepNum, x, y, angle, maxRange):
    #polar form
    r = np.sqrt(x**2 + y**2)
    theta = np.rad2deg(np.arctan2(y, x))
    
    #lower quartile/25th percentile for every 5 degrees of heading
    rangeQuartile = np.zeros_like(angle)
    for index in range(len(angle)):
        selector = abs(theta - angle[index]) < SEGMENT_SIZE / 2
        if (np.sum(selector) > 0):
            rangeQuartile[index] = np.percentile(r[selector], 25)
        else:
            rangeQuartile[index] = maxRange #caps the maximum value
    
    # for debugging and graphical display
    if EACH_STEP:
        ax:List[plt.Axes]
        fig, ax = plt.subplots(1, 2)
        plt.suptitle("At stepNum: " + str(stepNum))
        #displays the rectangular coordinates
        ax[0].scatter(x, y, label = "track", color = "green")
        ax[0].set_title("rectangular coordinates" )
        ax[0].set_xlabel('x (px)')
        ax[0].set_ylabel('y (px)')
        ax[0].axis('scaled')

        #displays the polar coordinates
        ax[1].scatter(theta, r, label = "polar")
        ax[1].scatter(angle, rangeQuartile, label = "rangeQuartile")
        ax[1].set_title("polar coordinates")
        ax[1].set_xlabel('theta (degrees)')
        ax[1].set_ylabel('range (px)')
        plt.legend()
        plt.show()
    return rangeQuartile

def MAINTAIN_process_range_quartile(stepNum, angle, rangeQuartile, maxRange, isLeft):

    #no overlap
    if isLeft: # if following the yellow left track line
        sideAngleIndex = 0
        halfAngle = angle[0:18]
        halfQuartile = rangeQuartile[0:18]
    else:
        sideAngleIndex = -1
        halfAngle = angle[-18:None] # selects the angles on the left of the car
        halfQuartile = rangeQuartile[-18:None]

    if isLeft: # if following the yellow left track line
        reference = OPTIMAL_SIDE_DISTANCE / np.cos(np.deg2rad(halfAngle)) # use trignometry to find the range, which is the hypotenuse
    else:
        reference = OPTIMAL_SIDE_DISTANCE / np.cos(np.deg2rad(halfAngle))

    reference[reference > maxRange] = maxRange # caps the maximum value
    turnNum = np.sum((halfQuartile - reference) * np.abs(halfAngle - halfAngle[sideAngleIndex])) # a weighted average/sum
    maxTurnNum = np.sum((maxRange - reference) * np.abs(halfAngle - halfAngle[sideAngleIndex]))
    turnFactor = turnNum / maxTurnNum #normalise the value, so it is always < 1
    # offsetFactor is larger when the car is further away from from the track line
    # the difference between offsetFactor and turnFactor, is that turnFactor accounts for all values in halfQuartile
    # not just halfQuartile[sideAngleIndex]
    # and turnFactor weighs angles further away from sideAngleIndex more
    offsetFactor = (halfQuartile[sideAngleIndex] - reference[sideAngleIndex]) / maxRange

    TURN_COEFFICIENT = 0.7
    if isLeft: # if following the yellow left track line
        carHeading = -45 * (TURN_COEFFICIENT * turnFactor + (1 - TURN_COEFFICIENT) * offsetFactor)
        # -60 can be adjusted. Avoid adjusting -90, since straight ahead is heading = -90
    else:
        carHeading = 45 * (TURN_COEFFICIENT * turnFactor + (1 - TURN_COEFFICIENT) * offsetFactor)
    
    carHeading = min(carHeading, 45) #caps the angle to a maximum value
    carHeading = max(carHeading, -45)
    adjacentRange = rangeQuartile[np.abs(angle - carHeading) <= SEGMENT_SIZE / 2] # find rangeQuartile value at approx. carHeading degrees
    carRange = adjacentRange[0] * CAR_SPEED # 0.3 limits the speed of car, so we don't crash

    return carRange, carHeading

def MAINTAIN_follow(frame, stepNum, leftPoints, rightPoints):
    #idea: add mask to frame so that distant tape is not picked up
    isLeft = (len(leftPoints) > len(rightPoints))

    if isLeft: #so follow the blue left track line
        (x, y) = leftPoints
        angle = np.arange(85, -15, -SEGMENT_SIZE)
    else:
        (x, y) = rightPoints
        angle = np.arange(-15, -86, -SEGMENT_SIZE)
        

    rangeQuartile = MAINTAIN_get_range_quartiles(stepNum, x, y, angle, MAX_RANGE)
    
    carRange, carHeading = MAINTAIN_process_range_quartile(stepNum, angle, rangeQuartile, MAX_RANGE, isLeft)
    
    return carRange, carHeading

def dummy_path_planner(blueTrans, yellowTrans, purpleTrans): # used for developing the GUI
    angle = 45
    speed = 255
    return 45, 255