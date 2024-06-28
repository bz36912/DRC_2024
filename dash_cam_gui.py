from base_gui_oop import Gui
import cv2 as cv
from datetime import datetime

class DashCamGui(Gui):
    def __init__(self, startVideo=True) -> None:
        format_str = "%d_%b_%y_%H_%M_%S"
        filename = "dash_cam/" + datetime.now().strftime(format_str) + ".mp4"
        # self.recorder = cv.VideoWriter(filename, cv.VideoWriter_fourcc(*'MPEG'), 30, (640, 360))
        self.recorder = cv.VideoWriter(
		        filename, cv.VideoWriter_fourcc(*'MP4V'), 25.0, (640, 360))
        super().__init__(startVideo)
        
    def close_threads(self):
        # may need to close thread in the future
        cv.destroyAllWindows()
        print("about to release recorder")
        self.recorder.release()
        if self.cap is not None:
            self.cap.release()
        self.root.destroy()
        exit()

    def get_next_video_frame(self):
        frame = super().get_next_video_frame()
        self.recorder.write(frame)
        return frame
    
if __name__ == "__main__":
    gui = DashCamGui()