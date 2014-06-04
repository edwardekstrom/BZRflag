import numpy
from numpy import *
from numpy import zeros
from numpy.linalg import *

class Kalman:

    def __init__(self):
        self.resetArrays()

    def resetArrays(self):
    # mean of the other tanks initial start position
        self.mu = array([[0],
                         [0],
                         [0],
                         [200],
                         [0],
                         [0]])

        self.sigmaT = array([[90,0,0  ,0 ,0,0  ],
                             [0 ,1,0  ,0 ,0,0  ],
                             [0 ,0,0.1,0 ,0,0  ],
                             [0 ,0,0  ,90,0,0  ],
                             [0 ,0,0  ,0 ,1,0  ],
                             [0 ,0,0  ,0 ,0,0.1]])

        self.H = array([[1,0,0,0,0,0],
                        [0,0,0,1,0,0]])

        self.sigmaZ = array([[25,0],
                             [0,25]])

        dt = .25
        c = .01
        self.F = array([[1,dt,dt**2/2,0,0 ,0      ],
                        [0,1 ,dt     ,0,0 ,0      ],
                        [0,-c,1      ,0,0 ,0      ],
                        [0,0 ,0      ,1,dt,dt**2/2],
                        [0,0 ,0      ,0,1 ,dt     ],
                        [0,0 ,0      ,0,-c,1      ]])

        self.sigmaX = array([[0.1,0  ,0  ,0  ,0  ,0  ],
                             [0  ,0.1,0  ,0  ,0  ,0  ],
                             [0  ,0  ,100,0  ,0  ,0  ],
                             [0  ,0  ,0  ,0.1,0  ,0  ],
                             [0  ,0  ,0  ,0  ,0.1,0  ],
                             [0  ,0  ,0  ,0  ,0  ,100]])

    def resetSigmaT(self):
        self.sigmaT = array([[90,0,0  ,0 ,0,0  ],
                             [0 ,1,0  ,0 ,0,0  ],
                             [0 ,0,0.1,0 ,0,0  ],
                             [0 ,0,0  ,90,0,0  ],
                             [0 ,0,0  ,0 ,1,0  ],
                             [0 ,0,0  ,0 ,0,0.1]])

    def updateKalmanFilter(self, Z_tPlus1):
        fTranspose = self.F.transpose()
        hTranspose = self.H.transpose()

        F_SigmaT_FTrans_plus_SigmaX = self.F.dot(self.sigmaT).dot(fTranspose)+self.sigmaX
        H_first_HTrans_plus_SigmaZ = self.H.dot(F_SigmaT_FTrans_plus_SigmaX).dot(hTranspose)+self.sigmaZ
        secondTrans = inv(H_first_HTrans_plus_SigmaZ)
        k_tPlus1 = F_SigmaT_FTrans_plus_SigmaX.dot(hTranspose).dot(secondTrans)

        Z_tPlus1_minus_H_F_Mu = Z_tPlus1-self.H.dot(self.F).dot(self.mu)
        mu_tPlus1 = self.F.dot(self.mu) + k_tPlus1.dot(Z_tPlus1_minus_H_F_Mu)

        sigmaT_tPlus1 = (identity(6)-k_tPlus1.dot(self.H)).dot(F_SigmaT_FTrans_plus_SigmaX)

        self.sigmaT = sigmaT_tPlus1
        self.mu = mu_tPlus1

    def setDT(self, time_diff):
        self.F[0][1] = time_diff
        self.F[0][2] = time_diff**2/2
        self.F[1][2] = time_diff
        self.F[3][4] = time_diff
        self.F[3][5] = time_diff**2/2
        self.F[4][5] = time_diff

    def projectPosition(self):
        return self.F.dot(self.mu)