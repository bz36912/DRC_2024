import numpy as np
from car_remote_control import Uart
OPT_DIST = 35 # cm
MAX_X = 100
MAX_Y = 120
TOO_BIG = 50
FRONT_CLIP = 10
FRONT_STOP = 30
FRONT_DIST = 70
FRONT_DIVID = 60
BLIND_SPOT = 10
SHORT = 60
MARGIN = 5
A = 45
B = 0.7

BASE_SPEED_YELLOW = 95
BASE_SPEED_BLUE = 110

def better_path_planner(blueTrans:np.ndarray, yellowTrans:np.ndarray, purpleTrans:np.ndarray, uart:Uart):
    rightBlue = blueTrans[blueTrans[::,0] < MAX_X]
    rightBlue = rightBlue[rightBlue[::,1] < MAX_Y]
    rightBlue = rightBlue[rightBlue[::,1] > 0]
    leftYellow = yellowTrans[yellowTrans[::,0] < MAX_X]
    leftYellow = leftYellow[leftYellow[::,1] < MAX_Y]
    leftYellow = leftYellow[leftYellow[::,1] > 0]

    if rightBlue.size == 0 and leftYellow.size == 0: # no data
        return -5, BASE_SPEED_YELLOW
    if (rightBlue.size > leftYellow.size):
        followLine = rightBlue
        direct = 1
        baseSpeed = BASE_SPEED_BLUE
    else :
        followLine = leftYellow
        direct = -1
        baseSpeed = BASE_SPEED_YELLOW
    
    front = followLine[abs(followLine[::,0]) < FRONT_CLIP]
    front = front[front[::,1] < FRONT_DIST]
    if front.size < 5:
        speed = baseSpeed + 1
        x = followLine[::,0]
        inner = followLine[(direct*(followLine[::,0]))<OPT_DIST-MARGIN]
        inner = inner[((inner[::,1]))<SHORT]
        outer = followLine[(direct*(followLine[::,0]))>OPT_DIST+MARGIN]
        outer = outer[((outer[::,1]))<SHORT]
        if inner.size > 5 or outer.size > 5:
            if inner.size == 0:
                inxmean = OPT_DIST*direct
                inymean = BLIND_SPOT
            else:
                inxmean = np.mean(inner[::,0])
                inymean = np.mean(inner[::,1])
            if outer.size == 0:
                outxmean = OPT_DIST*direct
                outymean = BLIND_SPOT
            else:
                outxmean = np.mean(outer[::,0])
                outymean = np.mean(outer[::,1])
            angle = -B * np.rad2deg(np.arctan([(outxmean-inxmean)/(outymean-inymean)])[0])
        else: 
            angle = 0
    else: 
        speed = baseSpeed + 2
        angle = A*FRONT_DIVID/(np.mean(front[::,1])-FRONT_STOP) * direct

    angle = min(80, max(-80, angle))
    #if (abs(angle)<10):
        #speed = 110

    if (abs(angle) > 70):
        speed = -20
        if uart is not None:
            uart.send_command(0, baseSpeed)
            if angle > 0:
                uart.swing_left()
            else:   
                uart.swing_right()

    #else: 
    #    speed = 130
    return angle, speed



    


