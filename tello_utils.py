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

def get_y(s, alpha):
    b = -.5135
    k_y = 1.0721
    a = s*k_y
    dist = a*alpha**b
    return dist

def get_x(qrCX, frameCenter, s, alpha):
    f = 591.01
    k_x = 1/f
    y = get_y(s, alpha)
    x_prime = frameCenter - qrCX
    x = k_x*x_prime*y
    return x

def get_z(qrCY, frameCenter, s, alpha):
    f = 551.54
    k_z = 1 / f
    y = get_y(s, alpha)
    z_prime = frameCenter - qrCY
    z = k_z * z_prime * y
    return z


def get_x_measurement(qrCX, frameCenter, s, alpha):
    '''

    :param qrCX: Center X position of the QR Code
    :param frameCenter: The center of the frame (Frame Width / 2)
    :param s:
    :param alpha:
    :return:
    '''
    y = get_y(s,alpha)
    x_prime = frameCenter - qrCX
    return x_prime, y

def get_z_measurement(qrCY, frameCenter, s, alpha):
    y = get_y(s, alpha)
    z_prime =  qrCY - frameCenter
    return z_prime, y




# p1 = np.array([4, 10])
# p2 = np.array([9, 7])
# p3 = np.array([11, 2])
# p4 = np.array([2, 2])

# polygon = np.array([p1,p2,p3,p4])
# print(polygon_area(polygon))