import cv2
import numpy as np


# You then want to relate the pixel locations (where you clicked) to the real locations (how deep and how left or right in whatever units the point is in reality) in this form:
pts1 = np.float32([[43,142],[77,106],[304,101],[354,130]]) #pixels
pts2 = np.float32([[-14.75,50],[-14.75,71],[14.5,71],[14.5,50]]) #cm

# you can then use this function to find the matrix 
matrix = cv2.getPerspectiveTransform(pts1, pts2)

print(matrix)