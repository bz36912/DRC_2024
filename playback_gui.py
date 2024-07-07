import cv2 as cv
import tkinter as tk
import time
import threading
import numpy as np
import datetime
from tkVideoPlayer import TkinterVideo

from base_gui_oop import Gui

class PlaybackGui(Gui):
    # FILEPATH = 'example_code/QUT_init_data_reduced.mp4' # Replace with the video address
    # FILEPATH = 'dash_cam/05_Jul_24_11_26_33.mp4'
    # FILEPATH = 'dash_cam/obstacle_moved_by_hand.mp4'
    FILEPATH = 'dash_cam/ob_2.mp4'
    # IMPORTANT: this class will scale the video resolution to 640X360, to reduce lag and the GUI screen fits,
    # using self.vid_player.bind() in self.play_pause()
    PLOT_GRAPH_EVERY_N_CYCLE = 1
    DISPLAY_VIDEO = True
    def __init__(self) -> None:
        self.vid_player = None # self.play_pause() also helps to initialise the video GUI element
        super().__init__(startVideo=False) # run tk.Tk.mainloop(), so this function blocks
        # startVideo=False, since we want the video to play after play button is pressed, rather than
        # automatically play since the start of the program

    def init_camera_feed(self, address):
        """ disable the function in the parent class, since the video feed is coming 
        from pre-recorded video using TkinterVideo instead of live video.

        Args:
            address (_type_): ignored

        Returns:
            None: None
        """
        return None
    
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
        # create video control buttons and seek bar
        self.play_pause_btn = tk.Button(self.secondFrame, text="Play", command=self.play_pause)
        self.skip_minus_5sec = tk.Button(self.secondFrame, text="Skip -5 sec", command=lambda: self.skip(-5))
        self.start_time = tk.Label(self.secondFrame, text=str(datetime.timedelta(seconds=0)))
        self.progress_value = tk.IntVar(self.secondFrame)
        self.progress_slider = tk.Scale(self.secondFrame, variable=self.progress_value, from_=0, to=0, orient="horizontal", command=self.seek)
        self.end_time = tk.Label(self.secondFrame, text=str(datetime.timedelta(seconds=0)))
        self.skip_plus_5sec = tk.Button(self.secondFrame, text="Skip +5 sec", command=lambda: self.skip(5))
        
        # layout of video control buttons and seek bar
        self.play_pause_btn.pack()
        self.skip_minus_5sec.pack(side="left")
        self.start_time.pack(side="left")
        self.progress_slider.pack(side="left", fill="x", expand=True)
        self.end_time.pack(side="left")
        self.skip_plus_5sec.pack(side="left")

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

            thread = threading.Thread(target=self.start_video_thread_entry)
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