import cv2
import numpy as np


# # You then want to relate the pixel locations (where you clicked) to the real locations (how deep and how left or right in whatever units the point is in reality) in this form:
# pts1 = np.float32([[395,191],[128,163],[255,115],[438,124]]) #pixels
# pts2 = np.float32([[0,30],[20,30],[20,50],[0,50]]) #cm
# matrix = cv2.getPerspectiveTransform(pts1, pts2)
# print(repr(matrix))
# # you can then use this function to find the matrix 
# pts1 = np.float32([[270,118],[337,94],[476,100],[450,129]]) #pixels
# pts2 = np.float32([[20,50],[20,70],[0,70],[0,50]]) #cm
# matrix = cv2.getPerspectiveTransform(pts1, pts2)
# print(repr(matrix))

pts1 = np.float32([[131,212],[86,136],[363,115],[504,155]]) #pixels
pts2 = np.float32([[0,30],[0,50],[30,50],[30,30]]) #cm
matrix = cv2.getPerspectiveTransform(pts1, pts2)
print(repr(matrix))