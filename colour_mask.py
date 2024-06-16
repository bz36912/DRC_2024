"""Jack Lord is doing it
It gets a frame from the raw video feed.
Identifies yellow, blue and purple regions. One side of the track is marked by yellow tape and other
by blue. The obstable (boxes) are purple.

"""
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

# Grid size
GRID_SIZE = 10

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
    lowerBlue = np.array([100, 100, 80])
    upperBlue = np.array([130, 255, 255])
    blueMask = cv.inRange(hsv, lowerBlue, upperBlue)

    # lower bound and upper bound for yellow
    lowerYellow = np.array([20, 3, 100])
    upperYellow = np.array([50, 255, 255])
    yellowMask = cv.inRange(hsv, lowerYellow, upperYellow)   #getting a yellow mask     
    
    #lower bound and upper bound for purple color
    lowerPurple = np.array([130, 50, 30])
    upperPurple = np.array([170, 255, 255])
    purpleMask = cv.inRange(hsv, lowerPurple, upperPurple)
    
    return blueMask, yellowMask, purpleMask

def check_grid_squares(frame, mask, colour):
    height, width = frame.shape[:2]
    for y in range(0, height, GRID_SIZE):
        for x in range(0, width, GRID_SIZE):
            # Define the grid square
            grid_square = mask[y:y+GRID_SIZE, x:x+GRID_SIZE]
            non_zero_count = cv.countNonZero(grid_square)
            
            # If a significant portion of the grid square contains the target color, draw a rectangle
            if non_zero_count > (GRID_SIZE * GRID_SIZE) / 5:  # Adjust threshold as needed
                cv.rectangle(frame, (x, y), (x + GRID_SIZE, y + GRID_SIZE), COMPLEMENTARY[colour], 2)

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


            rect = cv.minAreaRect(contour)  # Get the minimum area rectangle
            box = cv.boxPoints(rect)
            box = np.int0(box)
            # Calculate width and height of the rotated rectangle
            width = rect[1][0]
            height = rect[1][1]
            aspect_ratio = float(width) / height if height != 0 else 0


            if 4 < aspect_ratio < 10 or 4 < 1/aspect_ratio < 10:  # Adjust the range as needed
                contourArray = np.concatenate((contourArray, np.squeeze(contour)))
                cv.drawContours(frame, [box], 0, COMPLEMENTARY[colour], 2)
                cv.putText(frame, f"AR: {aspect_ratio:.2f}", (int(rect[0][0]), int(rect[0][1])), 
                        cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    return contourArray # Bryce wants this for his perspective transform part. The array's shape is N X 2
    # N is the number of points that defines the outline. The first coloum is x and second is y-coordinate.

def get_contour(frame, blueMask, yellowMask, purpleMask):
    blueContour = draw_contour(blueMask, BLUE, frame)
    yellowContour = draw_contour(yellowMask, YELLOW, frame)
    purpleContour = draw_contour(purpleMask, PURPLE, frame) 
    return blueContour, yellowContour, purpleContour

if __name__ == "__main__":
    #cap = cv.VideoCapture(0) # representing the camera feed using the laptop's built-in camera
    cap = cv.VideoCapture('example_code/test_video_1.mp4')
    init_camera_feed(cap)

    while True:
        # get a frame from the video feed
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame.")
            break

        frame = cv.flip(frame, 1)

        blueMask, yellowMask, purpleMask = colour_mask(frame)
        
        #blueContour, yellowContour, purpleContour = get_contour(frame, blueMask, yellowMask, purpleMask)
        check_grid_squares(frame, blueMask, BLUE)
        check_grid_squares(frame, yellowMask, YELLOW)
        check_grid_squares(frame, purpleMask, PURPLE)
        cv.imshow('frame with contour', frame)

        if cv.waitKey(1) & 0xFF == ord('q'): # press q to close the window and program
            break

    cap.release()
    cv.destroyAllWindows()