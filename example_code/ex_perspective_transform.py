"""Convert the camera frame/perspective to bird's eye view
using matrix operations
"""

import numpy as np
import matplotlib.pyplot as plt

def perspective_tansform(oldX, oldY):
    # Bryce JUST need to figure out the correct numbers in the M matrix,
    # which depends on the physical camera placement
    # Everything else is already good.
    M = np.array([[-3.0985, -4.6553, 2776.3],
                [2.71022, -4.4267, 1141.],
                [0.0001966, 0.022109, 1.]])
    
    multiplier = np.array([[-1., -1., -1.],
                [1., 1., 1.],
                [1., 1., 1.]])
    newM = M * multiplier
    P = np.array([oldX, oldY, np.ones_like(oldX)])
    X = 0
    Y = 1
    C = 2
    transformed = np.matmul(newM, P)
    transformedX = transformed[X] / transformed[C]
    transformedY = transformed[Y] / transformed[C]

    return transformedX, transformedY

if __name__ == "__main__":
    oldX = np.array([100,2,3,4,5,6])
    oldY = np.array([150,4,6,8,10,12])
    # in the comp the oldX and oldY will come from Jack Lord's colour mask step
    # He will give you THREE sets of oldX and oldY: yellow for one side of the track, blue the other side
    # and purple for the obstacle
    transformedX, transformedY = perspective_tansform(oldX, oldY)
    # the path planning will be based on transformedX, transformedY locations of yellow, blue and purple

    # testing the transform
    print("x: ", transformedX)
    print("y: ", transformedY)
    # graphing the points
    fig, ax = plt.subplots()
    ax.plot(oldX * 10, oldY * 10, "*b") 
    # the * 10 is adjust the scale, so the two plot can be compared on the same graph. 
    # It is JUST for visualisation. We want oldX and oldY, not the 10X version of them.
    ax.plot(transformedX, transformedY, "*g")
    plt.show()