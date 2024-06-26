import cv2 as cv

def init_camera_feed(cap):
    # initialising the video feed
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 240)
    if not cap.isOpened():
        print("Failed to open webcam")
        exit()

# Function to handle mouse events
def mouse_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Clicked at (x={}, y={})".format(x, y))

# Load the image
video = cv.VideoCapture('VID1.mp4')
init_camera_feed(video)
_, frame = video.read()
if frame is None:
    print("bingbong")
    exit()

# Check if the image was loaded successfully
if image is None:
    print("Error: Could not load image.")
    exit()

# Create a window to display the image
cv2.namedWindow('Image')

# Register the mouse click event handler
cv2.setMouseCallback('Image', mouse_click)

# Display the image
cv2.imshow('Image', image)

# Wait for a key press
cv2.waitKey(0)

# Close all OpenCV windows
cv2.destroyAllWindows()
