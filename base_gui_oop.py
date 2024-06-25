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
import cv2 as cv
import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk
import threading
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrow

from car_remote_control import Uart
from path_planner_1 import dummy_path_planner
from colour_mask import colour_mask, check_grid_squares
from example_code.ex_colour_mask import get_contour
from example_code.ex_perspective_transform import perspective_tansform
from queue import Queue

class Gui():
    ADDRESS = "https://192.168.221.107:8080//video" # Replace with the video address
    # IMPORTANT: set IP WebCam's resolution to 640X360, to reduce lag and the GUI screen fits.
    RESOLUTION = (360, 640, 3)
    PLOT_GRAPH_EVERY_N_CYCLE = 10
    def __init__(self) -> None:
        matplotlib.use('TkAgg')
        cv.CascadeClassifier("haarcascade_frontalface_default.xml") # Load the cascade
        # init tkinter
        self.root = tk.Tk()
        self.root.title("Dual Video Feed")
        self.root.protocol("WM_DELETE_WINDOW", self.close_threads)
        # using tkinter Labels, Frames and Widgets
        self.init_plot()
        self.init_gui_elements()

        self.cap = self.init_camera_feed(self.ADDRESS)
        
        thread = threading.Thread(target=self.thread_entry)
        thread.start()

        self.root.mainloop()
        if self.cap is not None:
            self.cap.release()

    def init_camera_feed(self, address):
        cap = cv.VideoCapture(0)
        cap.open(address)
        return cap
    
    def init_plot(self):
        # add elements to the plot
        self.ax:plt.Axes
        self.fig, self.ax = plt.subplots()
        self.blue = Line2D([], [], marker='o', linestyle='None', color='b')
        self.yellow = Line2D([], [], marker='o', linestyle='None', color='orange')
        self.purple = Line2D([], [], marker='o', linestyle='None', color='m')
        self.ax.add_line(self.blue)
        self.ax.add_line(self.yellow)
        self.ax.add_line(self.purple)
        self.text = self.ax.text(0, 30, "Speed: @ deg")
        self.arrow = FancyArrow(0, 0, 0.5, 0.5, head_width=5, head_length=7, width=0.5, fc='red', ec='red')
        self.ax.add_patch(self.arrow)
        self.ax._request_autoscale_view()

        # format the axes and graph
        self.ax.grid(True)
        self.ax.axis('equal')
        self.ax.set_xlim(-100, 100)  # Set x-axis limit
        self.ax.set_ylim(-20, 120)  # Set y-axis limit
        self.ax.set_xlabel('X-axis (cm)')
        self.ax.set_ylabel('Y-axis (cm)')
        self.ax.set_title("Bird's eye view")
        self.fig.tight_layout()

    def get_next_video_frame(self):
        _, frame = self.cap.read()
        if frame is None:
            print("end of video feed")
            exit()
        assert frame.shape == self.RESOLUTION, "ERROR in Gui::Gui: video resolution is incorrect."
        return frame
    
    def display_video_frame(self, frame, videoLabel):
        img = Image.fromarray(cv.cvtColor(frame, cv.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)
        videoLabel.configure(image=imgtk)
        videoLabel.imgtk = imgtk

    def update_plot(self, blueTrans, yellowTrans, purpleTrans, direction, speed):
        # plot the location of track and obstacles
        self.blue.set_data(blueTrans[::, 0], blueTrans[::, 1])
        self.yellow.set_data(yellowTrans[::, 0], yellowTrans[::, 1])
        self.purple.set_data(purpleTrans[::, 0], purpleTrans[::, 1])

        # Add the arrow onto the graph indicate the decison of the path planner
        max_arrow_length = 2  # Fixed maximum length for the arrow
        arrow_length = max_arrow_length * (speed / 5)  # Scale arrow length based on speed
        self.arrow.set_data(dx=arrow_length * np.cos(np.radians(direction)), dy=arrow_length * np.sin(np.radians(direction)))
        self.text.set_text(f"Speed: {speed} @ {direction} deg")

        # Draw the new plot
        self.canvas.draw()

    def get_and_display_colour_contour(self, frame):
        """Jack Lord can add his code here to integrate colour masking with the GUI
        """
        masked = np.copy(frame)
        blueMask, yellowMask, purpleMask = colour_mask(masked)
        blueContour, yellowContour, purpleContour = get_contour(masked, blueMask, yellowMask, purpleMask)

        self.display_video_frame(masked, self.video_label1)
        return blueContour, yellowContour, purpleContour

    def thread_entry(self, update_video_label2=True):
        """Updates the GUI with live video feed.
        Automatically runs when the program starts and is called by __init__()

        Args:
            update_video_label2 (bool, optional): Set to True, if you want this function to update
            video_label2 (raw video feed without any annotatation). Set to False, if another function
            (e.g. TkinterVideo's play() used by the child class, PlaybackGui) updates video_label2, and you
            need to avoid clashes between this function and the other function.
            Defaults to True.
        """
        cycle = 0
        while True:
            frame = self.get_next_video_frame()
            # pre-recorded video is at 60fps. Hotspot connection can reach 25fps (sometimes 37fps)
            blueContour, yellowContour, purpleContour = self.get_and_display_colour_contour(frame)
            if update_video_label2:
                self.display_video_frame(frame, self.video_label2)
            # perspective transform (to get bird's eye/top view of the track)
            blueTrans = perspective_tansform(blueContour.transpose())
            yellowTrans = perspective_tansform(yellowContour.transpose())
            purpleTrans = perspective_tansform(purpleContour.transpose())
            direction, speed = dummy_path_planner(blueTrans, yellowTrans, purpleTrans)
            direction += 90 # for the path planner, 0 is up. But the graph has 0 pointing to the right.
            if cycle % self.PLOT_GRAPH_EVERY_N_CYCLE == 0:
                # plot bird's eye view
                self.update_plot(blueTrans, yellowTrans, purpleTrans, direction, speed)
            cycle += 1

    def close_threads(self):
        # may need to close thread in the future
        self.root.destroy()
        exit()

    def init_gui_elements(self):
        """must be called after self.init_plot(), which creates self.fig 
        which is needed by self.canvas
        """
        self.topFrame = tk.Frame(self.root)
        self.secondFrame = tk.Frame(self.root) # the frame below the top frame
        # create the bird's eye graph
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.secondFrame)
        self.canvas.draw()
        # Video labels
        self.video_label1 = Label(self.topFrame, bg='green')
        self.video_label2 = Label(self.topFrame, bg='blue')

        # layout of the elements
        self.canvas.get_tk_widget().pack(side='left')
        self.video_label1.pack(side='right', expand=True, fill='both')
        self.video_label2.pack(side='left', expand=True, fill='both')
        self.topFrame.pack(side='top')
        self.topFrame.config(height=self.RESOLUTION[0])
        self.secondFrame.pack(side='top', expand=True, fill="both")

if __name__ == "__main__":
    gui = Gui()