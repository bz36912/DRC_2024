import cv2
import numpy as np


# You then want to relate the pixel locations (where you clicked) to the real locations (how deep and how left or right in whatever units the point is in reality) in this form:
pts1 = np.float32([[180,132],[433,114],[587,156],[221,202]]) #pixels
pts2 = np.float32([[0,30],[0,51],[29.5,51],[29.5,30]]) #cm

# you can then use this function to find the matrix 
matrix = cv2.getPerspectiveTransform(pts1, pts2)

print(matrix)