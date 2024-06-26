import cv2
import numpy as np


# You then want to relate the pixel locations (where you clicked) to the real locations (how deep and how left or right in whatever units the point is in reality) in this form:
pts1 = np.float32([[60,156],[202,115],[461,134],[420,203]]) #pixels
pts2 = np.float32([[29.5,30],[29.5,51],[0,51],[0,30]]) #cm

# you can then use this function to find the matrix 
matrix = cv2.getPerspectiveTransform(pts1, pts2)

print(repr(matrix))