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
from colour_mask import colour_mask, check_grid_squares
from example_code.ex_colour_mask import get_contour
from example_code.ex_perspective_transform import perspective_tansform
import cv2 as cv
import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk
import time
import threading
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrow
from car_remote_control import Uart

# Load the cascade
face_cascade = cv.CascadeClassifier("haarcascade_frontalface_default.xml")

def init_camera_feed(cap):
    # initialising the video feed
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 240)
    if not cap.isOpened():
        print("Failed to open webcam")
        exit()

def init_plot():
    ax.grid(True)
    ax.axis('equal')
    ax.set_xlim(-100, 100)  # Set x-axis limit
    ax.set_ylim(0, 140)  # Set y-axis limit
    ax.set_xlabel('X-axis (cm)')
    ax.set_ylabel('Y-axis (cm)')
    ax.set_title("Bird's eye view")
    fig.tight_layout()

# Define a function to update the video feeds
def update_videos():    
    _, frame = video.read()
    if frame is None:
        print("end of video feed")
        exit()
    # Resize the frame to 1/4 of its original size
    frame = cv.resize(frame, None, fx=0.25, fy=0.25, interpolation=cv.INTER_AREA)
    
    # Convert the frame to a format tkinter can use
    img = Image.fromarray(cv.cvtColor(frame, cv.COLOR_BGR2RGB))
    imgtk = ImageTk.PhotoImage(image=img)

    masked = np.copy(frame)
    blueMask, yellowMask, purpleMask = colour_mask(masked)
    blueContour, yellowContour, purpleContour = get_contour(masked, blueMask, yellowMask, purpleMask)

    masked_img = Image.fromarray(cv.cvtColor(masked, cv.COLOR_BGR2RGB))
    masked_imgtk = ImageTk.PhotoImage(image=masked_img)

    # Update both video labels with the same frame
    video_label1.configure(image=masked_imgtk)
    video_label1.imgtk = masked_imgtk
    video_label2.configure(image=imgtk)
    video_label2.imgtk = imgtk
    return blueContour, yellowContour, purpleContour

def update_plot(blueTrans, yellowTrans, purpleTrans, direction, speed):
    blue.set_data(blueTrans[::, 0], blueTrans[::, 1])
    yellow.set_data(yellowTrans[::, 0], yellowTrans[::, 1])
    purple.set_data(purpleTrans[::, 0], purpleTrans[::, 1])
    # Add the arrow in the corner
    max_arrow_length = 2  # Fixed maximum length for the arrow
    arrow_length = max_arrow_length * (speed / 5)  # Scale arrow length based on speed
    
    # global arrow
    arrow.set_data(dx=arrow_length * np.cos(np.radians(direction)), dy=arrow_length * np.sin(np.radians(direction)))
    text.set_text(f"Speed: {speed} @ {direction} deg")

    # Draw the new plot
    canvas.draw()

def thread_entry():
    while True:
        for i in range(20):
            blueContour, yellowContour, purpleContour = update_videos() 
            # pre-recorded video is at 60fps. Hotspot connection can reach 37fps
        direction = 45 # dummy value
        speed = 255 # dummy value
        # perspective transform (to get bird's eye/top view of the track)
        blueTrans = perspective_tansform(blueContour.transpose())
        yellowTrans = perspective_tansform(yellowContour.transpose())
        purpleTrans = perspective_tansform(purpleContour.transpose())
        # plot bird's eye view
        update_plot(blueTrans, yellowTrans, purpleTrans, direction, speed)

def close_threads():
    # may need to close thread in the future
    root.destroy()
    exit()

# Initialize the main window
root = tk.Tk()
root.title("Dual Video Feed")
root.protocol("WM_DELETE_WINDOW", close_threads)

# elements of the bird's eye graph
ax:plt.Axes
fig, ax = plt.subplots()
blue = Line2D([], [], marker='o', linestyle='None', color='b')
yellow = Line2D([], [], marker='o', linestyle='None', color='orange')
purple = Line2D([], [], marker='o', linestyle='None', color='m')
ax.add_line(blue)
arrow = FancyArrow(0, 20, 0.5, 0.5, head_width=5, head_length=7, width=0.5, fc='red', ec='red')
text = ax.text(0, 30, "Speed: @ deg")
ax.add_patch(arrow)
ax._request_autoscale_view()
init_plot()

# create the bird's eye graph
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack()

# Video labels
video_label1 = Label(root)
video_label1.pack(side='right')
video_label2 = Label(root)
video_label2.pack(side='bottom')

# Open video capture
# address = "https://192.168.108.85:8080//video" # Replace with the video address
# video = cv.VideoCapture(0)
# video.open(address)

# video = cv.VideoCapture('example_code/QUT_init_data_reduced.mp4')
video = cv.VideoCapture('example_code/car_view_test1.mp4')
init_camera_feed(video)

# Start the video loop
thread = threading.Thread(target=thread_entry)
thread.start()

# Run the application
root.mainloop()

# Release the video capture when the window is closed
video.release()
cv.destroyAllWindows()