import numpy as np

def polygon_area(coords):
    num_vertices = coords.shape[0]

    area = 0
    for i in range(num_vertices):
        j = i + 1
        if j == num_vertices: j = 0

        x_a,y_a = coords[i]
        x_b,y_b = coords[j]
        area = area + (x_a*y_b - y_a*x_b)/2

    return abs(area)

# p1 = np.array([4, 10])
# p2 = np.array([9, 7])
# p3 = np.array([11, 2])
# p4 = np.array([2, 2])

# polygon = np.array([p1,p2,p3,p4])
# print(polygon_area(polygon))