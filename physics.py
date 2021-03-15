import numpy as np
from froll import froll2d2
import matplotlib.pyplot as plt


def distances(arr):
    temp_distances  = np.zeros_like(arr)
    for i in range(arr.shape[0]):
        for j in range(arr.shape[0]-1):
            temp_distances[i] = temp_distances[i] + (arr[i]-arr[i-j])
    return temp_distances
def loss(arr):
    loss = np.copy(arr)
    loss = np.sqrt((loss**2).sum(1))
    return np.max(loss)

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
iterations = 10000
steps = np.arange(iterations)
losses = np.zeros(iterations)
for i in range(iterations):
    dis = distances(coordinates)
    losses[i] = loss(dis)
    coordinates = project(coordinates + 1/100*dis)
    x = coordinates[:, 0]
    y = coordinates[:, 1]
plt.plot(steps,losses)
plt.show()
for i in range(len(x)):
    for j in range(len(x)):
        plt.plot([x[i], x[j]], [y[i], y[j]], "ro-")
plt.show()
