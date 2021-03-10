import numpy as np
from froll import froll2d2
import matplotlib.pyplot as plt


def distances(arr):
    temp = np.zeros(arr.shape)
    for i in range(1, arr.shape[1], 1):
        temp = temp + (arr - froll2d2(arr, [0, i]))
    return temp


# projeziert die Koordinaten auf den 1x1x1 Würfel um den Ursprung
def project(arr):
    temp = np.copy(arr)
    max = np.amax(temp, axis=0)
    min = np.amin(temp, axis=0)
    for i in range(len(min)):
        if min[i] < 0:
            temp[:, i] = temp[:, i] + min[i]
    for i in range(len(max)):
        temp[:, i] = 1 / max[i] * temp[:, i]
    return temp


n = 12
coordinates = np.random.rand(n, 2)
for i in range(1000):
    dis = distances(coordinates)
    print((dis ** 2).sum())
    coordinates = project(coordinates + dis)
    x = coordinates[:, 0]
    y = coordinates[:, 1]

for i in range(len(x)):
    for j in range(len(x)):
        plt.plot([x[i], x[j]], [y[i], y[j]], "ro-")
plt.show()
