import numpy as np
from car_remote_control import Uart
#OPT_DIST optminal distance to mantain the blue line away from the robot
OPT_DIST = 35 # cm
#MAX_X maximun x distance to consider in frame
MAX_X = 100
#MAX_Y maximun y distance to consider in frame 
MAX_Y = 100
#FRONT_CLIP  domain off centre to consider points "in front" of the robot
FRONT_CLIP = 10
#FRONT_STOP value to increase reaction time by increasing precieved closeness to the line 
FRONT_STOP = 30
#FRONT_DIST Maximun distance it can react to as a line infront of the robot
FRONT_DIST = 70
#FRONT_DIVID
FRONT_DIVID = 60
#BLIND_SPOT minimun distance in fornt it can see, used as placeholder when too far from the line 
BLIND_SPOT = 15
#SHORT ?
SHORT = 60
#MARGIN margin of error within keping the line at a distance 
MARGIN = 5
#A multiplier of the front adjustment angle 
A = 45
#B multiplier for the line following agressivness
B = 0.9

# BASE_SPEED_YELLOW base speed for following yellow line 
BASE_SPEED_YELLOW = 95
# BASE_SPEED_BLUE base speed of blue line following 
BASE_SPEED_BLUE = 110

def better_path_planner(blueTrans:np.ndarray, yellowTrans:np.ndarray, purpleTrans:np.ndarray, uart:Uart):
    # filtering data for only value within max_x and max_y and in front fo robot
    rightBlue = blueTrans[blueTrans[::,0] < MAX_X]
    rightBlue = rightBlue[rightBlue[::,1] < MAX_Y]
    rightBlue = rightBlue[rightBlue[::,1] > 0]
    leftYellow = yellowTrans[yellowTrans[::,0] < MAX_X]
    leftYellow = leftYellow[leftYellow[::,1] < MAX_Y]
    leftYellow = leftYellow[leftYellow[::,1] > 0]

    # State machine, folllows blue by default if it can see more blue than yellow 
    # yellow line as backup 
    # if no no line slowly turn to the right to try and see blue line 
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
    
    #clips line array to only points in front of the robot 
    front = followLine[abs(followLine[::,0]) < FRONT_CLIP]
    front = front[front[::,1] < FRONT_DIST]
    # if points in front of robot do front angle turning else default to line following 
    if front.size < 5:
        speed = baseSpeed + 1
        x = followLine[::,0]
        #create two line arrays, one inside the optimal distance one outside 
        inner = followLine[(direct*(followLine[::,0]))<OPT_DIST-MARGIN]
        # inner = inner[((inner[::,1]))<SHORT]
        outer = followLine[(direct*(followLine[::,0]))>OPT_DIST+MARGIN]
        # outer = outer[((outer[::,1]))<SHORT]
        # if there is no points inside/outside optimal distance default to a point on the line and just on the blind spot 
        # else use the mean of the points 
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
            # else if all points within margin drive forward 
            angle = 0
    else: 
        #front angle turning 
        # increase the angle the closer the line gets inversely 
        speed = baseSpeed + 2
        # stops the dist going negative and inverting the direction
        dist = max(np.mean(front[::,1])-FRONT_STOP, 0.1)
        angle = A*FRONT_DIVID/(dist) * direct

    # caps angle at 80
    angle = min(80, max(-80, angle))

    # if angle is too high stops driving forward and trys to turn on the spot
    if (abs(angle) > 70):
        speed = -20
        if uart is not None:
            uart.send_command(0, baseSpeed)
            if angle > 0:
                uart.swing_left()
            else:   
                uart.swing_right()


    return angle, speed



    


