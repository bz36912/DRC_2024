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
    # M = np.array([[-2.13117761e-04, -8.70680435e-06,  1.27400463e-01], 
    #         [-4.39043323e-06,  1.77834625e-05, -1.89890525e-01], 
    #         [-4.34531921e-06, -2.31760232e-03,  1.00000000e+00]])
    # 30cm right
    # M = np.array([[-1.77968529e-01,-2.50144655e+00,3.62225280e+02],
    #         [-2.35887861e-01,-9.30697817e-01, 5.46427169e+01],
    #         [ 1.36469318e-04, -3.57086222e-02,  1.00000000e+00]])

    # 50cm
    # M = np.array([[-7.58054875e-01, 3.32676396e-01, 1.15693471e+02],
    #         [ 2.19673733e-01,3.14465915e-01,-4.95921012e+02],
    #         [ 1.46091182e-03,-6.97129355e-02,1.00000000e+00]])
    # M = np.array([[ 3.54535414e-01,  2.10665971e-01, -1.91670066e+02],
    #    [-1.63719927e-01,  6.22979284e-02, -1.39760417e+02],
    #    [-4.71241936e-04, -3.61147222e-02,  1.00000000e+00]])
    # M = np.array([[ 2.57209401e-01,  1.65074690e-01, -1.33126979e+02],
    #    [-1.07922755e-01, -4.71710524e-02, -8.84425078e+01],
    #    [-8.29407028e-04, -2.79673986e-02,  1.00000000e+00]])
    #new 30cm 
    # M = np.array([[-5.71185135e-01,  3.38201725e-01,  3.12648705e+00],
    #    [ 3.36647916e-01, -1.06567803e-01, -3.85482094e+02],
    #    [ 2.09993538e-03, -6.32431348e-02,  1.00000000e+00]])
    #1/7 recalcabration
    # M = np.array([[-5.50575612e-01,  2.47197213e-01,  3.29895918e+01],
    #    [ 2.96654063e-01, -1.47976353e-01, -3.66981148e+02],
    #    [ 1.95472858e-03, -6.09277193e-02,  1.00000000e+00]])
    #set turret matrix
    M = np.array([[-1.94654961e-01,  1.28295315e-01,  9.15320712e+00],
       [ 9.96374948e-02, -5.46254529e-02, -1.22633496e+02],
       [-1.33995753e-05, -2.17713448e-02,  1.00000000e+00]])
    
    # multiplier = np.array([[-1., -1., -1.],
    #             [1., 1., 1.],
    #             [1., 1., 1.]])
    # newM = M * multiplier
    # P = np.array([oldX, oldY, np.ones_like(oldX)])
    rowOfOnes = np.ones(shape=(1, oldXY.shape[1]))
    P = np.concatenate((oldXY, rowOfOnes), axis=0)
    X = 0
    Y = 1
    C = 2

    transformed = np.matmul(M, P)
    transformedXY:np.array = transformed[[X, Y]] / transformed[C]

    return transformedXY.transpose()

if __name__ == "__main__":
    oldXY = np.array([[395,191],[128,163],[255,115],[438,124]])
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
    # ax.plot(oldXY[::, 0], oldXY[::, 1], "*b")
    # the * 10 is to adjust the scale, so the two plot can be compared on the same graph. 
    # It is JUST for visualisation. We want oldX and oldY, not the 10X version of them.
    ax.plot(transformedXY[::, 0], transformedXY[::, 1], "*g")
    plt.show()