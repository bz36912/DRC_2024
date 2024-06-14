import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

#### CONSTANTS
GREEN = (0, 255, 0)  # in BGR.
RED = (0, 0, 255)
BLUE= (255, 0, 0)
ORANGE = (0, 128, 255)
PURPLE = (255, 51, 153)
YELLOW = (0, 255, 255)

# the colour green will be marked by red outline. Purple by yellow outline and so on.
# basically the complementary colour pairs on the colour wheel
COMPLEMENTARY = {GREEN:RED, RED:GREEN, PURPLE:YELLOW, YELLOW:PURPLE, BLUE:ORANGE}
#### end of CONSTANTS

def init_camera_feed(cap):
    # initialising the video camera on computer
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 240)
    if not cap.isOpened():
        print("Failed to open webcam")
        exit()

def colour_mask(frame):
    #convert to hsv colorspace
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    #lower bound and upper bound for blue
    lowerBlue = np.array([100, 70, 80])
    upperBlue = np.array([130, 255, 255])
    blueMask = cv.inRange(hsv, lowerBlue, upperBlue)

    # lower bound and upper bound for yellow
    lowerYellow = np.array([28, 40, 100])
    upperYellow = np.array([42, 255, 255])
    yellowMask = cv.inRange(hsv, lowerYellow, upperYellow)   #getting a yellow mask     
    
    #lower bound and upper bound for purple color
    lowerPurple = np.array([130, 50, 30])
    upperPurple = np.array([170, 255, 255])
    purpleMask = cv.inRange(hsv, lowerPurple, upperPurple)
    
    return blueMask, yellowMask, purpleMask

def draw_contour(mask, colour, frame):
    """
    marks the locations of the colour, by tracing an outline around the colour.
    contour is just another word for the outline/edge of an area.
    mask: contains pixels of the colour in frame
    colour: the name/identifier of the colour
    frame: the original image
    """
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE) #find contour/outline of a colour
    contourArray = np.zeros((0, 2)) #just an empty array
    for contour in contours:
        area = cv.contourArea(contour)
        if area > 400: #only include large areas of the colour
            contourArray = np.concatenate((contourArray, np.squeeze(contour)))
            cv.drawContours(frame, [contour], 0, COMPLEMENTARY[colour], 2) 
            # Ib will use cv.drawContours to display the countour on GUI for debugging

    return contourArray # Bryce wants this for his perspective transform part. The array's shape is N X 2
    # N is the number of points that defines the outline. The first coloum is x and second is y-coordinate.

def get_contour(frame, blueMask, yellowMask, purpleMask):
    blueContour = draw_contour(blueMask, BLUE, frame)
    yellowContour = draw_contour(yellowMask, YELLOW, frame)
    purpleContour = draw_contour(purpleMask, PURPLE, frame) 
    return blueContour, yellowContour, purpleContour

if __name__ == "__main__":
    # cap = cv.VideoCapture(0) # representing the camera feed using the laptop's built-in camera
    # cap = cv.VideoCapture('what_track_n_obstacles_look_like.mp4')
    cap = cv.VideoCapture('2023_video_2.mp4')

    init_camera_feed(cap)

    while True:
    # for i in range(1):
        # get a frame from the video feed
        ret, frame = cap.read()
        # frame = cv.imread("./image.png")
        frame = cv.flip(frame, 1)

        blueMask, yellowMask, purpleMask = colour_mask(frame)
        blueContour, yellowContour, purpleContour = get_contour(frame, blueMask, yellowMask, purpleMask)
        cv.imshow('frame with contour', frame)

        # c = cv.waitKey(0) # blocking waiting

        if cv.waitKey(1) == ord('q'): # press q to close the window and program. Non-blocking wait.
            break

    cap.release()
    cv.destroyAllWindows()