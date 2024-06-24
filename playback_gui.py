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

import datetime
from tkinter import filedialog
from tkVideoPlayer import TkinterVideo
from base_gui_oop import Gui

FILENAME = 'example_code/car_view_test1.mp4'
# FILENAME = 'example_code/QUT_init_data_reduced.mp4'
RESOLUTION = (360, 640, 3)

class PlaybackGui(Gui):
    def __init__(self) -> None:
        # init tkinter
        self.root = tk.Tk()
        self.root.title("Dual Video Feed")
        self.root.protocol("WM_DELETE_WINDOW", self.close_threads)
        # using tkinter Labels, Frames and Widgets
        self.init_plot()
        self.init_gui_elements()

        self.cap = self.init_camera_feed(FILENAME)

        thread = threading.Thread(target=self.thread_entry)
        thread.start()

        self.root.mainloop()
        self.cap.release()
    
    def init_camera_feed(self, fileName):
        cap = cv.VideoCapture(fileName)
        if not cap.isOpened():
            print("Failed to open video feed")
            exit()

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
    while True:
        frame = vid_player.current_img()
        if frame is None:
            time.sleep(0.2)
        else:
            break
    frame = np.array(frame)
    frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)
    # Resize the frame to 1/4 of its original size
    frame = cv.resize(frame, None, fx=0.25, fy=0.25, interpolation=cv.INTER_AREA)
    
    # Convert the frame to a format tkinter can use

    masked = np.copy(frame)
    blueMask, yellowMask, purpleMask = colour_mask(masked)
    blueContour, yellowContour, purpleContour = get_contour(masked, blueMask, yellowMask, purpleMask)
    masked_pil = Image.fromarray(cv.cvtColor(masked, cv.COLOR_BGR2RGB))

    video_label1.config(width=root.winfo_width() // 2)
    vid_player.config(width=root.winfo_width() // 2)
    label_width = max(video_label1.winfo_width() - 5, 1)  # Get the current width of video_label1
    label_height = max(video_label1.winfo_height() - 5, 1) # Get the current height of video_label1
    masked_resized = masked_pil.resize((label_width, label_height), Image.ANTIALIAS)
    masked_imgtk = ImageTk.PhotoImage(image=masked_resized)

    # Update both video labels with the same frame
    video_label1.configure(image=masked_imgtk)
    video_label1.imgtk = masked_imgtk
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

# Video labels
topFrame = tk.Frame(root)
midFrame = tk.Frame(root)
# create the bird's eye graph
canvas = FigureCanvasTkAgg(fig, master=topFrame)
canvas.draw()
canvasWidget = canvas.get_tk_widget()
canvasWidget.pack(side='left')

###########
def load_video2():
    pass

vid_player = TkinterVideo(scaled=True, master=midFrame, bg='green')
vid_player.pack(side='left', expand=True, fill="both")
vid_player.load('example_code/car_view_test1.mp4')
vid_player.play()

video_label1 = Label(midFrame, bg='blue')
video_label1.pack(side='right', expand=True, fill="both")

bottomFrame = tk.Frame(root)
play_pause_btn = tk.Button(bottomFrame, text="Play", command=load_video2)
play_pause_btn.pack(side="left")

skip_plus_5sec = tk.Button(bottomFrame, text="Skip -5 sec", command=lambda: load_video2)
skip_plus_5sec.pack(side="left")

start_time = tk.Label(bottomFrame, text=str(datetime.timedelta(seconds=0)))
start_time.pack(side="left")

progress_value = tk.IntVar(bottomFrame)

progress_slider = tk.Scale(bottomFrame, variable=progress_value, from_=0, to=0, orient="horizontal", command=load_video2)
# progress_slider.bind("<ButtonRelease-1>", seek)
progress_slider.pack(side="left", fill="x", expand=True)

end_time = tk.Label(bottomFrame, text=str(datetime.timedelta(seconds=0)))
end_time.pack(side="left")
skip_plus_5sec = tk.Button(bottomFrame, text="Skip +5 sec", command=lambda: load_video2)
skip_plus_5sec.pack(side="left")

topFrame.pack(side='top')
midFrame.pack(side='top', expand=True, fill="both")
bottomFrame.pack(side='top')
########

# Start the video loop
thread = threading.Thread(target=thread_entry)
thread.start()
time.sleep(0.5)

# Run the application
root.mainloop()

# Release the video capture when the window is closed
cv.destroyAllWindows()