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
import cv2
import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk
import time
import threading

# Load the cascade
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# Define a function to update the video feeds
def update_frame():
    _, frame = video.read()
    # Resize the frame to 1/4 of its original size
    frame = cv2.resize(frame, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
    
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    # for (x, y, w, h) in faces:
    #     cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
    
    # Convert the frame to a format tkinter can use
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    imgtk = ImageTk.PhotoImage(image=img)

    # Update both video labels with the same frame
    video_label1.configure(image=imgtk)
    video_label1.imgtk = imgtk
    video_label2.configure(image=imgtk)
    video_label2.imgtk = imgtk


def thread_entry():
    while True:
        update_frame()
        # time.sleep(0.01)

def close_threads():
    global thread
    thread.join()
    root.destroy()

# Initialize the main window
root = tk.Tk()
root.title("Dual Video Feed")
root.protocol("WM_DELETE_WINDOW", close_threads)

# Video labels
video_label1 = Label(root)
video_label1.pack()
video_label2 = Label(root)
video_label2.pack()

# Open video capture
address = "https://192.168.130.148:8080//video" # Replace with the video address
video = cv2.VideoCapture(0)
video.open(address)

# Start the video loop
thread = threading.Thread(target=thread_entry)
thread.start()

# Run the application
root.mainloop()

# Release the video capture when the window is closed
video.release()
cv2.destroyAllWindows()


