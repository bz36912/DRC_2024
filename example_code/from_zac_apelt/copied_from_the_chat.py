posList = []
def onMouse(event, x, y, flags, param):
   global posList
   if event == cv2.EVENT_LBUTTONDOWN:
        posList.append((x, y))
cv2.setMouseCallback('[window name]', onMouse)
posNp = np.array(posList)

You then want to relate the pixel locations (where you clicked) to the real locations (how deep and how left or right in whatever units the point is in reality) in this form:
pts1 = np.float32([[464, 404], [522, 321], [776, 322], [830, 405]]) #pixels
pts2 = np.float32([[-0.65, 2.5], [-0.65, 3.7], [0.65, 3.7], [.65, 2.5]]) #meters

you can then use this function to find the matrix 
matrix = cv2.getPerspectiveTransform(pts1, pts2)