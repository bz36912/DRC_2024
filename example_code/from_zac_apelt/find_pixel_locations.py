import cv2
WIDTH = 29.5

# Function to handle mouse events
def mouse_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Clicked at (x={}, y={})".format(x, y))

# Load the image
image = cv2.imread('./30cm.jpg',cv2.IMREAD_COLOR)

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
