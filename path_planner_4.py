import numpy as np
from car_remote_control import Uart
OPT_DIST = 30 # cm
MAX_X = 100
MAX_Y = 120
TOO_BIG = 50
FRONT_CLIP = 10
FRONT_DIST = 50
SHORT = 60
MARGIN = 5
A = 1
B = 1

def better_path_planner(blueTrans:np.ndarray, yellowTrans:np.ndarray, purpleTrans:np.ndarray, uart:Uart):
    rightBlue = blueTrans[blueTrans[::,0] < MAX_X]
    rightBlue = rightBlue[rightBlue[::,1] < MAX_Y]
    rightBlue = rightBlue[rightBlue[::,1] > 0]
    leftYellow = yellowTrans[yellowTrans[::,0] < MAX_X]
    leftYellow = leftYellow[leftYellow[::,1] < MAX_Y]
    leftYellow = leftYellow[leftYellow[::,1] > 0]

    if rightBlue.size == 0 and leftYellow.size == 0: # no data
        return 0, 130
    if rightBlue.size > leftYellow.size:
        followLine = rightBlue
        direct = 1
    else :
        followLine = leftYellow
        direct = -1
    
    front = followLine[abs(followLine[::,1]) < FRONT_CLIP]
    if front.size < 5:
        x = followLine[::,0]
        inner = followLine[(direct*(followLine[::,0]))<OPT_DIST-MARGIN]
        inner = inner[((inner[::,1]))<SHORT]
        outer = followLine[(direct*(followLine[::,0]))>OPT_DIST+MARGIN]
        outer = outer[((outer[::,1]))<SHORT]
        if inner.size > 5 or outer.size > 5:
            if inner.size == 0:
                inmean = OPT_DIST
            else:
                inmean = np.mean(inner)
            if outer.size == 0:
                outmean = OPT_DIST
            else:
                outmean = np.mean(outer)
            angle = (outmean - inmean)*B*direct
        else: 
            angle = 0
    else: 
        angle = A*FRONT_DIST/np.mean(front[::,1]) * direct

    angle = min(80, max(-80, angle))
    if (abs(angle)<10):
        speed = 110
    elif (abs(angle) > 60):
        speed = -10
        if uart is not None:
            if angle < 0:
                uart.swing_left()
            else:   
                uart.swing_right()
    else: 
        speed = 130
    return angle, speed



    


