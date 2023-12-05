from car import *
import numpy as np


class LinearNode:
    def __init__(self, x: int, y: int):
        self.l_x = x
        self.l_y = y
        self.weights = np.random.randn(y, x) * np.sqrt(2 / x)
        self.bias = np.random.randn(y, 1)


node_list = [7, 15, 2]
fully_connect_list = []
for i in range(len(node_list) - 1):
    fully_connect_list.append(LinearNode(node_list[i], node_list[i + 1]))
    print('added (%d, %d)' % (node_list[i], node_list[i + 1]))
for i in range(len(fully_connect_list)):
    n = fully_connect_list[i]
    print(n.weights)
