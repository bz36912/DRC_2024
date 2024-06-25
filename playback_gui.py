import cv2 as cv
import tkinter as tk
import time
import threading
import numpy as np
import datetime
from tkVideoPlayer import TkinterVideo

from base_gui_oop import Gui
from path_planner_1 import dummy_path_planner
from colour_mask import colour_mask, check_grid_squares
from example_code.ex_colour_mask import get_contour
from example_code.ex_perspective_transform import perspective_tansform

class PlaybackGui(Gui):
    FILEPATH = 'example_code/car_view_test1.mp4' # Replace with the video address
    # IMPORTANT: this class will scale the video resolution to 640X360, to reduce lag and the GUI screen fits,
    # using self.vid_player.bind() in self.play_pause()
    PLOT_GRAPH_EVERY_N_CYCLE = 10
    def __init__(self) -> None:
        self.vid_player = None # self.play_pause() also helps to initialise the video GUI element
        super().__init__() # run tk.Tk.mainloop(), so this function blocks

    def thread_entry(self):
        pass # disable the thread in the parent class

    def init_camera_feed(self, address):
        return None # disable the function in the parent class
    
    def get_next_video_frame(self):
        frame = None
        while frame is None:
            time.sleep(0.01)
            frame = self.vid_player.current_img()
            # print("current_img is None")
        frame = np.array(frame)
        frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)
        return frame

    def init_gui_elements(self):
        super().init_gui_elements()
        # video control buttons and seek bar
        self.bottomFrame = tk.Frame(self.root)
        self.play_pause_btn = tk.Button(self.bottomFrame, text="Play", command=self.play_pause)
        self.skip_minus_5sec = tk.Button(self.bottomFrame, text="Skip -5 sec", command=lambda: self.skip(-5))
        self.start_time = tk.Label(self.bottomFrame, text=str(datetime.timedelta(seconds=0)))
        self.progress_value = tk.IntVar(self.bottomFrame)
        self.progress_slider = tk.Scale(self.bottomFrame, variable=self.progress_value, from_=0, to=0, orient="horizontal", command=self.seek)
        self.end_time = tk.Label(self.bottomFrame, text=str(datetime.timedelta(seconds=0)))
        self.skip_plus_5sec = tk.Button(self.bottomFrame, text="Skip +5 sec", command=lambda: self.skip(5))
        
        # layout of the bottom frame
        self.play_pause_btn.pack()
        self.skip_minus_5sec.pack(side="left")
        self.start_time.pack(side="left")
        self.progress_slider.pack(side="left", fill="x", expand=True)
        self.end_time.pack(side="left")
        self.skip_plus_5sec.pack(side="left")
        self.bottomFrame.pack(side='bottom', fill="x", expand=True)

    def start_video_thread(self):
        """is trigger when the play button is pressed.
        Is it equivalent to the thread_entry() for parent class, Gui(), which triggers automatically without button press.
        """
        super().thread_entry(update_video_label2=False)
        # video_label2 is replaced by TkinterVideo's self.vid_player.play() function.

    ### functionalities, trigger when a button or seek bar is clicked ###
    def play_pause(self):
        """ pauses and plays """
        if self.vid_player is None: # the initialising the raw video feed when the button is FIRST clicked
            # raw video feed
            self.video_label2.pack_forget()
            self.vid_player = TkinterVideo(scaled=True, master=self.topFrame, bg='blue')
            self.vid_player.bind("<<Loaded>>", lambda e: e.widget.config(width=self.RESOLUTION[1], height=self.RESOLUTION[0]))
            self.vid_player.pack(side='left')
            self.vid_player.load(self.FILEPATH)
            self.vid_player.play()
            self.play_pause_btn["text"] = "Pause"

            self.vid_player.bind("<<Duration>>", self.update_duration)
            self.vid_player.bind("<<SecondChanged>>", self.update_scale)
            self.vid_player.bind("<<Ended>>", self.video_ended)

            thread = threading.Thread(target=self.start_video_thread)
            thread.start()
            return

        if self.vid_player.is_paused():
            self.vid_player.play()
            self.play_pause_btn["text"] = "Pause"
        else:
            self.vid_player.pause()
            self.play_pause_btn["text"] = "Play"
    
    def seek(self, value):
        """ used to seek a specific timeframe """
        self.vid_player.seek(int(value))

    def skip(self, value: int):
        """ skip seconds """
        self.vid_player.seek(int(self.progress_slider.get())+value)
        self.progress_value.set(self.progress_slider.get() + value)

    ### event handling ###
    def video_ended(self, event):
        """ handle video ended """
        self.progress_slider.set(self.progress_slider["to"])
        self.play_pause_btn["text"] = "Play"
        self.progress_slider.set(0)

    def update_duration(self, event):
        """ updates the duration after finding the duration """
        duration = self.vid_player.video_info()["duration"]
        self.end_time["text"] = str(datetime.timedelta(seconds=duration))
        self.progress_slider["to"] = duration


    def update_scale(self, event):
        """ updates the scale value """
        self.progress_value.set(self.vid_player.current_duration())

if __name__ == "__main__":
    gui = PlaybackGui()