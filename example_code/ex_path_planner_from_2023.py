import numpy as np
import matplotlib.pyplot as plt
from typing import List
import cv2 as cv

from ex_colour_mask import colour_mask

OPTIMAL_SIDE_DISTANCE = 40
EACH_STEP = True
SEGMENT_SIZE = 5
MAX_RANGE = 150

# colours
GREEN = (0, 255, 0)  # in BGR.
RED = (0, 0, 255)
BLUE= (255, 0, 0)
ORANGE = (0, 128, 255)
PURPLE = (255, 51, 153)
YELLOW = (0, 255, 255)

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
    
    return rangeQuartile

def MAINTAIN_process_range_quartile(stepNum, angle, rangeQuartile, maxRange, isLeft):
    if isLeft: # if following the blue left track line
        sideAngleIndex = -1
        halfAngle = angle[-18:None] # selects the angles on the left of the car
        halfQuartile = rangeQuartile[-18:None]
    else:
        sideAngleIndex = 0
        halfAngle = angle[0:18]
        halfQuartile = rangeQuartile[0:18]

    if isLeft: # if following the blue left track line
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
    if isLeft: # if following the blue left track line
        carHeading = -45 * (TURN_COEFFICIENT * turnFactor + (1 - TURN_COEFFICIENT) * offsetFactor) - 90
        # -60 can be adjusted. Avoid adjusting -90, since straight ahead is heading = -90
    else:
        carHeading = 45 * (TURN_COEFFICIENT * turnFactor + (1 - TURN_COEFFICIENT) * offsetFactor) - 90
    
    carHeading = min(carHeading, -45) #caps the angle to a maximum value
    carHeading = max(carHeading, -135)
    adjacentRange = rangeQuartile[np.abs(angle - carHeading) <= SEGMENT_SIZE / 2] # find rangeQuartile value at approx. carHeading degrees
    carRange = adjacentRange[0] * 0.3 # 0.3 limits the speed of car, so we don't crash

    return carRange, carHeading

def MAINTAIN_follow(frame, stepNum, leftPoints, rightPoints):
    isLeft = (len(leftPoints) > len(rightPoints))

    if isLeft: #so follow the blue left track line
        (x, y) = leftPoints
    else:
        (x, y) = rightPoints
        
    angle = np.arange(-5, -176, -SEGMENT_SIZE)
    rangeQuartile = MAINTAIN_get_range_quartiles(stepNum, x, y, angle, MAX_RANGE)
    
    carRange, carHeading = MAINTAIN_process_range_quartile(stepNum, angle, rangeQuartile, MAX_RANGE, isLeft)
    
    return carRange, carHeading

def convert_to_real_life_frame(points, shapeOfFrame):
    """ the real-life frame is the reality
    display frame is the scale of the png image made in MS paint

    Args:
        points (array): input coordinates of MS paint
        shapeOfFrame (array): the dimension of MS paint image in pixels

    Returns:
        array: real-life coordinates
    """
    points = np.array(points)
    points = points // 10 # since ten pixels represent 1cm
    points[0] -= shapeOfFrame[1] // 2 # offset the x-axis by half of frame width, 
    # so we can see both the left and right
    return points

def convert_to_display_frame(points, shapeOfFrame):
    points = np.array(points)
    points = points * 10 # since ten pixel represent 1cm
    points[0] += shapeOfFrame[1] // 2
    return points

if __name__ == "__main__":
    frame = cv.imread("./basic_sim_with_paint/turn_right.png")
    frame = cv.flip(frame, 0) # so the x-axis is at the bottom not the top of the frame. 
    # For images (0, 0) is at the top left corner, instead of the bottom left corner (which is for a typical graph)

    blueMask, yellowMask, purpleMask = colour_mask(frame)

    leftPoints = cv.Canny(yellowMask, 60, 180) # edge detection
    leftPoints = np.nonzero(leftPoints) # returns a tuple of np.arrays. First array is x and second is for y.
    realLeft = convert_to_real_life_frame(leftPoints, frame.shape)

    rightPoints = cv.Canny(blueMask, 60, 180)
    rightPoints = np.nonzero(rightPoints)
    realRight = convert_to_real_life_frame(rightPoints, frame.shape)

    carRange, carHeading = MAINTAIN_follow(frame, 0, realLeft, realRight)
    print(f"heading: {carHeading} degrees, carRange: {carRange}")
    x = carRange * np.sin(np.deg2rad(carHeading))
    y = carRange * np.cos(np.deg2rad(carHeading))
    dis_x, dis_y = convert_to_display_frame([x, y], frame.shape)
    cv.line(frame, tuple(convert_to_display_frame([0, 0], frame.shape)), (round(dis_x), round(dis_y)), GREEN, 3) # marks the prediction of the path planner
    cv.circle(frame, tuple(convert_to_display_frame([0, 0], frame.shape)), 10, GREEN, -1) # marks the location of the car

    frame = cv.flip(frame, 0) # flip it back
    cv.imshow('frame', frame)
    cv.waitKey(0) # press any key to end program
    print('end')