import cv2

# Open the default camera (index 0)
cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# Capture a frame from the camera
ret, frame = cap.read()

# Check if the frame was captured successfully
if not ret:
    print("Error: Could not capture frame.")
    exit()

# Release the camera
cap.release()

# Save the captured frame as an image
cv2.imwrite('[location to save to]', frame)

# Display a message indicating the image was saved
print("Image saved as captured_image.jpg.")
