import numpy as np
import cv2
pts1 = np.float32([[226,688],[919,691],[802,601],[347,600]]) #pixels
pts2 = np.float32([[-0.123,0.300],[0.123,0.300],[0.123,0.461],[-0.123,0.461]]) #meters

matrix = cv2.getPerspectiveTransform(pts1, pts2)

image = cv2.imread("./example_code/from_zac_apelt/IMG_20240616_144315.jpg")
image = cv2.resize(image,(0,0),fx=0.35,fy=0.35)

# image shape: 857, 1142
image = cv2.warpPerspective(image,matrix,(600,800))
print(matrix)

cv2.namedWindow('Image')
cv2.imshow('Image', image)

cv2.waitKey(0)