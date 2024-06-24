"""Convert the camera frame/perspective to bird's eye view
using matrix operations
"""

import numpy as np
import matplotlib.pyplot as plt

def perspective_tansform(oldXY):
    # Bryce JUST need to figure out the correct numbers in the M matrix,
    # which depends on the physical camera placement
    # Everything else is already good.
    # M = np.array([[-3.0985, -4.6553, 2776.3],
    #             [2.71022, -4.4267, 1141.],
    #             [0.0001966, 0.022109, 1.]])

    # Bryce's first matrix
    M = np.array([[-2.13117761e-04, -8.70680435e-06,  1.27400463e-01], 
            [-4.39043323e-06,  1.77834625e-05, -1.89890525e-01], 
            [-4.34531921e-06, -2.31760232e-03,  1.00000000e+00]])
    
    multiplier = np.array([[-1., -1., -1.],
                [1., 1., 1.],
                [1., 1., 1.]])
    newM = M * multiplier
    # P = np.array([oldX, oldY, np.ones_like(oldX)])
    rowOfOnes = np.ones(shape=(1, oldXY.shape[1]))
    P = np.concatenate((oldXY, rowOfOnes), axis=0)
    X = 0
    Y = 1
    C = 2
    transformed = np.matmul(newM, P)
    transformedXY:np.array = transformed[[X, Y]] / transformed[C]

    return transformedXY.transpose() * 100 # convert to cm

if __name__ == "__main__":
    oldXY = np.array([[100, 150], [2, 4], [3, 6], [4, 8], [5, 10], [6, 12]])
    oldX = oldXY[::, 0]
    oldY = oldXY[::, 1]
    # in the comp the oldXY will come from Jack Lord's colour mask step
    # He will give you THREE sets of oldXY: yellow for one side of the track, blue the other side
    # and purple for the obstacle
    matrixInput = np.copy(oldXY.transpose())
    transformedXY = perspective_tansform(matrixInput)
    # the path planning will be based on transformedX, transformedY locations of yellow, blue and purple

    # testing the transform
    print("xy: ", transformedXY)
    # graphing the points
    fig, ax = plt.subplots()
    ax.plot(oldXY[::, 0] * 10, oldXY[::, 1] * 10, "*b")
    # the * 10 is to adjust the scale, so the two plot can be compared on the same graph. 
    # It is JUST for visualisation. We want oldX and oldY, not the 10X version of them.
    ax.plot(transformedXY[::, 0], transformedXY[::, 1], "*g")
    plt.show()