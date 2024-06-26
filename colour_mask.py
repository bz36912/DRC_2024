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
GRID_SIZE = 15
MIN_CLUMP_SIZE = 35

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
    lowerBlue = np.array([50, 70, 180])
    upperBlue = np.array([130, 255, 255])
    blueMask = cv.inRange(hsv, lowerBlue, upperBlue)

    # lower bound and upper bound for yellow
    lowerYellow = np.array([30, 3, 190])
    upperYellow = np.array([60, 255, 255])
    yellowMask = cv.inRange(hsv, lowerYellow, upperYellow)   #getting a yellow mask     
    
    #lower bound and upper bound for purple color
    lowerPurple = np.array([145, 50, 30])
    upperPurple = np.array([170, 255, 255])
    purpleMask = cv.inRange(hsv, lowerPurple, upperPurple)
    
    return blueMask, yellowMask, purpleMask

def calculate_average_hsv(mask, hsv_image):
    """
    Calculate the average HSV value of the non-zero pixels in the mask.
    """
    masked_hsv = cv.bitwise_and(hsv_image, hsv_image, mask=mask)
    h_values = masked_hsv[:, :, 0][mask > 0]
    s_values = masked_hsv[:, :, 1][mask > 0]
    v_values = masked_hsv[:, :, 2][mask > 0]

    if len(h_values) == 0:
        return (0, 0, 0)
    
    avg_h = np.mean(h_values)
    avg_s = np.mean(s_values)
    avg_v = np.mean(v_values)

    return (avg_h, avg_s, avg_v)

def flood_fill2(x, y, visited, mask):
    stack = [(x, y)]
    component = []

    while stack:
        cx, cy = stack.pop()
        if visited[cy, cx]:
            continue

        visited[cy, cx] = True
        component.append((cx, cy))

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < mask.shape[1] and 0 <= ny < mask.shape[0]:
                if mask[ny, nx] > 0 and not visited[ny, nx]:
                    stack.append((nx, ny))

    return component

def grid_square_component2(component):
        squares = set()
        for (cx, cy) in component:
            gx, gy = (cx // GRID_SIZE) * GRID_SIZE, (cy // GRID_SIZE) * GRID_SIZE
            squares.add((gx, gy))
        return list(squares)

def check_grid_squares2(frame, mask, colour, hsv_image):
    # This one is for checking the hsv values
    height, width = frame.shape[:2]
    visited = np.zeros_like(mask, dtype=bool)
    for y in range(0, height, GRID_SIZE):
        for x in range(0, width, GRID_SIZE):
            if mask[y, x] > 0 and not visited[y, x]:
                component = flood_fill2(x, y, visited, mask)
                if len(component) > 0:

                    #if len(component) < MIN_CLUMP_SIZE:
                    #    continue

                    # Create a mask for the component
                    component_mask = np.zeros_like(mask)
                    for cx, cy in component:
                        component_mask[cy, cx] = 255
                    
                    # Calculate the average HSV value of the clump
                    avg_hsv = calculate_average_hsv(component_mask, hsv_image)
                    avg_hsv_text = f"H: {avg_hsv[0]:.1f}, S: {avg_hsv[1]:.1f}, V: {avg_hsv[2]:.1f}"
                    
                    # Draw bounding box and text
                    x_coords, y_coords = zip(*component)
                    x_min, x_max = min(x_coords), max(x_coords)
                    y_min, y_max = min(y_coords), max(y_coords)
                    cv.rectangle(frame, (x_min, y_min), (x_max + GRID_SIZE, y_max + GRID_SIZE), COMPLEMENTARY[colour], 2)
                    cv.putText(frame, avg_hsv_text, (x_min, y_min - 5), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)

def check_grid_squares3(frame, mask, colour):
    # This one is for removing small clumps
    height, width = frame.shape[:2]
    visited = np.zeros_like(mask, dtype=bool)
    
    def flood_fill(x, y):
        stack = [(x, y)]
        component = []

        while stack:
            cx, cy = stack.pop()
            if visited[cy, cx]:
                continue

            visited[cy, cx] = True
            component.append((cx, cy))

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < width and 0 <= ny < height:
                    if mask[ny, nx] > 0 and not visited[ny, nx]:
                        stack.append((nx, ny))

        return component
    
    def grid_square_component(component):
        squares = set()
        for (cx, cy) in component:
            gx, gy = (cx // GRID_SIZE) * GRID_SIZE, (cy // GRID_SIZE) * GRID_SIZE
            squares.add((gx, gy))
        return list(squares)
    
    clump_centers = []

    for y in range(0, height, GRID_SIZE):
        for x in range(0, width, GRID_SIZE):
            if mask[y, x] > 0 and not visited[y, x]:
                component = flood_fill(x, y)
                grid_squares = grid_square_component(component)
                clump_size = len(grid_squares)
                if len(grid_squares) < MIN_CLUMP_SIZE:
                    continue  # Skip small clumps
                
                for (gx, gy) in grid_squares:
                    non_zero_count = cv.countNonZero(mask[gy:gy+GRID_SIZE, gx:gx+GRID_SIZE])
                    if non_zero_count > (GRID_SIZE * GRID_SIZE) / 6:
                        cv.rectangle(frame, (gx, gy), (gx + GRID_SIZE, gy + GRID_SIZE), COMPLEMENTARY[colour], 2)

                if grid_squares:
                    center_x = sum([gx for gx, gy in grid_squares]) // len(grid_squares)
                    center_y = sum([gy for gx, gy in grid_squares]) // len(grid_squares)
                    clump_centers.append((center_x, center_y, clump_size))

    for center_x, center_y, clump_size in clump_centers:
        cv.putText(frame, str(clump_size), (center_x, center_y), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

def check_grid_squares4(frame, mask, colour):
    # This one is for turning small clumps red
    height, width = frame.shape[:2]
    visited = np.zeros_like(mask, dtype=bool)
    
    def flood_fill(x, y):
        stack = [(x, y)]
        component = []

        while stack:
            cx, cy = stack.pop()
            if visited[cy, cx]:
                continue

            visited[cy, cx] = True
            component.append((cx, cy))

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < width and 0 <= ny < height:
                    if mask[ny, nx] > 0 and not visited[ny, nx]:
                        stack.append((nx, ny))

        return component
    
    def grid_square_component(component):
        squares = set()
        for (cx, cy) in component:
            gx, gy = (cx // GRID_SIZE) * GRID_SIZE, (cy // GRID_SIZE) * GRID_SIZE
            squares.add((gx, gy))
        return list(squares)
    
    clump_centers = []

    for y in range(0, height, GRID_SIZE):
        for x in range(0, width, GRID_SIZE):
            if mask[y, x] > 0 and not visited[y, x]:
                component = flood_fill(x, y)
                grid_squares = grid_square_component(component)
                clump_size = len(grid_squares)
                color_to_draw = (0, 0, 255) if clump_size < MIN_CLUMP_SIZE else COMPLEMENTARY[colour]

                for (gx, gy) in grid_squares:
                    non_zero_count = cv.countNonZero(mask[gy:gy+GRID_SIZE, gx:gx+GRID_SIZE])
                    if non_zero_count > (GRID_SIZE * GRID_SIZE) / 6:
                        cv.rectangle(frame, (gx, gy), (gx + GRID_SIZE, gy + GRID_SIZE), color_to_draw, 2)

                if grid_squares:
                    center_x = sum([gx for gx, gy in grid_squares]) // len(grid_squares)
                    center_y = sum([gy for gx, gy in grid_squares]) // len(grid_squares)
                    clump_centers.append((center_x, center_y, clump_size))

    for center_x, center_y, clump_size in clump_centers:
        cv.putText(frame, str(clump_size), (center_x, center_y), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)


def check_grid_squares(frame, mask, colour):
    # This one is the default one
    height, width = frame.shape[:2]
    for y in range(0, height, GRID_SIZE):
        for x in range(0, width, GRID_SIZE):
            # Define the grid square
            grid_square = mask[y:y+GRID_SIZE, x:x+GRID_SIZE]
            non_zero_count = cv.countNonZero(grid_square)
            
            # If a significant portion of the grid square contains the target color, draw a rectangle
            if non_zero_count > (GRID_SIZE * GRID_SIZE) / 6:  # Adjust threshold as needed
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
        perimeter = cv.arcLength(contour,True)

        rect = cv.minAreaRect(contour)  # Get the minimum area rectangle
        box = cv.boxPoints(rect)
        box = np.int0(box)
        # Calculate width and height of the rotated rectangle
        width = rect[1][0]
        height = rect[1][1]
        aspect_ratio = float(width) / height if height != 0 else 0
        perimeter_area_ratio = 10* perimeter/area  if area !=0 else 0 # we want this to be lower

        cv.putText(frame, f"A: {perimeter_area_ratio:.2f}", (int(rect[0][0]), int(rect[0][1])), 
                        cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        if perimeter_area_ratio > 0.65: #only include large areas of the colour
            contourArray = np.concatenate((contourArray, contour.reshape(-1, 2)))
            cv.drawContours(frame, [contour], 0, COMPLEMENTARY[colour], 2) 
            # Ib will use cv.drawContours to display the countour on GUI for debugging
        else:
            #contourArray = np.concatenate((contourArray, np.squeeze(contour)))
            cv.drawContours(frame, [contour], 0, (0, 0, 255), 2) 
    return contourArray # Bryce wants this for his perspective transform part. The array's shape is N X 2
    # N is the number of points that defines the outline. The first coloum is x and second is y-coordinate.

def get_contour(frame, blueMask, yellowMask, purpleMask):
    blueContour = draw_contour(blueMask, BLUE, frame)
    yellowContour = draw_contour(yellowMask, YELLOW, frame)
    purpleContour = draw_contour(purpleMask, PURPLE, frame) 
    return blueContour, yellowContour, purpleContour

if __name__ == "__main__":
    # cap = cv.VideoCapture(0) # representing the camera feed using the laptop's built-in camera
    # cap = cv.VideoCapture('example_code\QUT_init_data_reduced.mp4')
    # cap = cv.VideoCapture('example_code\car_view_test1.mp4')
    # cap = cv.VideoCapture('example_code\AEB_data2.mp4')
    cap = cv.VideoCapture('example_code/2023_video_1.mp4')
    init_camera_feed(cap)

    while True:
        # get a frame from the video feed
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame.")
            break

        frame = cv.flip(frame, 1)

        hsv_image = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        blueMask, yellowMask, purpleMask = colour_mask(frame)
        
        blueContour, yellowContour, purpleContour = get_contour(frame, blueMask, yellowMask, purpleMask)
        '''
        check_grid_squares2(frame, blueMask, BLUE, hsv_image)
        check_grid_squares2(frame, yellowMask, YELLOW, hsv_image)
        check_grid_squares2(frame, purpleMask, PURPLE, hsv_image)
        
        check_grid_squares4(frame, blueMask, BLUE)
        check_grid_squares4(frame, yellowMask, YELLOW)
        check_grid_squares4(frame, purpleMask, PURPLE)
        '''
        height, width = frame.shape[:2]
        #frame = cv.resize(frame, (width//2, height//2), interpolation=cv.INTER_AREA)
        cv.imshow('frame with contour', frame)

        if cv.waitKey(1) & 0xFF == ord('q'): # press q to close the window and program
            break

    cap.release()
    cv.destroyAllWindows()