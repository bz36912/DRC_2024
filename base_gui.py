"""Ib is doing it
It is for visualising the data, which help us to debug and develop the data processing and
self-driving algorithm.
It helps us to see what the car is seeing so we can better understand its behaviour.
The GUI shows:
    - the raw video feed
    - annotated feed with contours/outlines from colour masking
    - after perspective transform and an arrow showing the direction (angle) and speed (length of arrow)
        the path planner directs the car to drive in

this is some text
"""

import colour_mask
import cv2, time
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

video = cv2.VideoCapture(0)
address = "https://192.168.67.34:8080/video"
video.open(address)

while True:
    check, frame = video.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face = face_cascade.detectMultiScale(gray, 
                                         scaleFactor=1.1, 
                                         minNeighbors=5)
    for x, y, w, h in face:
        img = cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0),3)
    cv2.imshow("gottcha", frame)
    key=cv2.waitKey(1)

    if key == ord('q'):
        break
video.release()
cv2.destroyAllWindows