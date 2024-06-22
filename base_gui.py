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
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Load the cascade
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# Define a function to update the video feeds
def update_frame():
    _, frame = video.read()
    # Resize the frame to 1/4 of its original size
    frame = cv2.resize(frame, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
    
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

def close_threads():
    global thread
    thread.join()
    root.destroy()

def update_plot(coords, direction, speed):
    # Clear the previous plot
    ax.cla()
    
    for (x, y) in coords:
        ax.scatter(x, y, color='blue')  # Set all points to be blue
    
    # Add the arrow in the corner
    max_arrow_length = 2  # Fixed maximum length for the arrow
    arrow_length = max_arrow_length * (speed / 100)  # Scale arrow length based on speed
    
    ax.arrow(0, 0, arrow_length * np.cos(np.radians(direction)), arrow_length * np.sin(np.radians(direction)),
             head_width=0.2, head_length=0.3, fc='red', ec='red')
    
    ax.grid(True)
    ax.set_xlim(-2, 10)  # Set x-axis limit
    ax.set_ylim(-2, 10)  # Set y-axis limit
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_title('Scatter plot of points')
    
    # Draw the new plot
    canvas.draw()
    
    # Update the speed and direction display
    speed_dir_label.config(text=f"Speed: {speed}, Direction: {direction} degrees")

# Initialize the main window
root = tk.Tk()
root.title("Dual Video Feed")
root.protocol("WM_DELETE_WINDOW", close_threads)

# Video labels
video_label1 = Label(root)
video_label1.pack()
video_label2 = Label(root)
video_label2.pack()

# Create a figure
fig, ax = plt.subplots()

# Create a canvas for the plot and add it to the Tkinter window
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack()

# Label to display speed and direction
speed_dir_label = Label(root, text="Speed: , Direction: ")
speed_dir_label.pack()

# Example of how to call update_plot with new data
def simulate_data_update():
    coords = [(np.random.randint(0, 10), np.random.randint(0, 10)) for _ in range(10)]
    direction = np.random.randint(0, 360)
    speed = np.random.randint(0, 100)
    update_plot(coords, direction, speed)
    root.after(1000, simulate_data_update)

# Start updating the plot with new data
simulate_data_update()

# Open video capture
address = "https://192.168.0.150:8080//video" # Replace with the video address
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





