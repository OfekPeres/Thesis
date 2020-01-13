import numpy as np
import cv2

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

def find_side_height_difference(coords):
    # print("Coordinates are: {}".format(coords))
    # sort the inputted coordinates
    coords_sorted = sorted(coords, key = lambda k: [k[0], k[1]])
    # print("Coordinates sorted are: {}".format(coords_sorted))
    y1 = coords_sorted[0][1]
    y2 = coords_sorted[1][1]
    y3 = coords_sorted[2][1]
    y4 = coords_sorted[3][1]
    height_diff = abs(y1 - y2) - abs(y3 - y4)
    # print("Height difference is: {}".format(height_diff))
    return height_diff



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

def draw_april_tag_bounding_box(frame, aprilTag, centered, close_enough):
    (x,y,w,h) = aprilTag.rect
    circle_radius = np.min([w,h])//8
    qrCX = x+w//2
    qrCY = y+h//2
    frameHeight,frameWidth = frame.shape[:2]
    frame_area = frameHeight * frameWidth
    # print(frameHeight)
    # print(frameWidth)
    # Define colors for bounding box on april tags
    colorFound = (0,255,0) # Green
    colorCircleNotFound = (255,50,100)
    yellow = (0,255,255)
    colorPolyNotFound   = yellow

    currentCircleColor = colorCircleNotFound
    currentPolyColor   = colorPolyNotFound
    poly_area = polygon_area(np.array(aprilTag.polygon))
    find_side_height_difference(np.array(aprilTag.polygon))
    percent_screen = poly_area/frame_area

    # Get side length of QR Code based on the data inside of it
    QR_Code_Map = {1:2.1256, 2:4.325, 18:7.03125, 19:5.0625}
    aprilTagData = int(aprilTag.data.decode("utf-8"))
    side_length = QR_Code_Map[aprilTagData]

    # Get Distances
    y_dist = get_y(side_length, percent_screen)
    # print("Current y distance: {}".format(y_dist))

    x_dist = get_x(qrCX, frameWidth//2, side_length, percent_screen)
    z_dist = get_z(qrCY, frameHeight//2, side_length, percent_screen)
    print("Current x distance: {:.2f}, Current y distance: {:.2f}, Current z distance {:.2f}".format(x_dist, y_dist, z_dist))


    if centered and close_enough:
        currentCircleColor = colorFound
        currentPolyColor   = colorFound    

    cv2.circle(frame,(qrCX,qrCY), circle_radius//2, currentCircleColor, -1)
    polygon   = np.array(aprilTag.polygon)
    polygon = polygon.reshape((-1,1,2))
    cv2.polylines(frame,[polygon],True,currentPolyColor,5)
    aprilTagData = aprilTag.data.decode("utf-8")
    text = "Data:{}".format(aprilTagData)
    cv2.putText(frame,text,(x,y-10),cv2.FONT_HERSHEY_TRIPLEX,0.5,(0,0,255),2)

# Define Criteria for how to interact with april tag
def get_control_inputs(frame, aprilTag):
    frameHeight,frameWidth = frame.shape[:2]
    frame_area = frameHeight * frameWidth
    (x,y,w,h) = aprilTag.rect
    qrCX = x+w//2
    qrCZ = y+h//2
    frameCX = frameWidth//2
    frameCZ = frameHeight//2
    # Get Percent of Screen QR Code Covers
    poly_area = polygon_area(np.array(aprilTag.polygon))
    percent_screen = poly_area/frame_area

    # Get side length of QR Code based on the data inside of it
    QR_Code_Map = {1:2.1256, 2:4.325, 18:7.03125, 19:5.0625}
    aprilTagData = int(aprilTag.data.decode("utf-8"))
    side_length = QR_Code_Map[aprilTagData]

    # Get Distances and figure out control inputs
    y_dist = get_y(side_length, percent_screen)
    print("Current y distance: {}".format(y_dist))
    y_tracking = 12 #inches
    accuracy_error = 75 #Pixels

    y_input = y_dist - y_tracking
    x_input = -frameCX + qrCX
    z_input = -qrCZ + frameCZ
    # print("x input: {}".format(x_input))
    # print("y input: {}".format(y_input))
    # print("z input: {}".format(z_input))

    centered = False
    closeEnough = False
    if z_input < accuracy_error and x_input < accuracy_error:
        centered = True
    if abs(y_input) <= 1: #inch
        closeEnough = True

    if centered and closeEnough:
        x_vel = 0
        y_vel = 0
        z_vel = 0
        return x_vel, y_vel,z_vel, 0, centered, closeEnough

    speed = 10
    if y_dist > 30:
        speed = 10
    x_vel = speed
    y_vel = speed
    z_vel = speed
    if abs(y_input) < 1:
        y_vel = 0
    elif y_input < 0:
        y_vel = -speed

    if abs(x_input) < accuracy_error:
        x_vel = 0
    elif x_input < 0:    
        x_vel = -speed
    if abs(z_input) < accuracy_error:
        z_vel = 0
    elif z_input < 0:
        z_vel = -speed

    if y_vel > 0:
        z_vel+= 5

    return x_vel,y_vel,z_vel,0, centered, closeEnough
    

def get_pid_control_inputs(frame, aprilTag):
    frameHeight,frameWidth = frame.shape[:2]
    frame_area = frameHeight * frameWidth
    (x,y,w,h) = aprilTag.rect
    qrCX = x+w//2
    qrCZ = y+h//2
    frameCX = frameWidth//2
    frameCZ = frameHeight//2
    # Get Percent of Screen QR Code Covers
    poly_area = polygon_area(np.array(aprilTag.polygon))
    percent_screen = poly_area/frame_area
    # Get side length of QR Code based on the data inside of it
    QR_Code_Map = {1:2.1256, 2:4.325, 18:7.03125, 19:5.0625}
    aprilTagData = int(aprilTag.data.decode("utf-8"))
    side_length = QR_Code_Map[aprilTagData]

    # Get Distances and figure out control inputs
    y_dist = get_y(side_length, percent_screen)
    # print("Current y distance: {}".format(y_dist))
    y_des = 5 #inches
    x_des_pxl = frameCX #pixels
    z_des_pxl = frameCZ #pixels
    yaw_des_dh = 0 #deltaH pixels

    height_diff = find_side_height_difference(np.array(aprilTag.polygon))
    kp_yaw = 2
    # yaw_dot = -1*kp_yaw * height_diff

    # x_dot = int(-1*R * k_yaw * yaw_dot*deg2rad)
    # print("X-dot is: {}".format(x_dot))
    



    r = np.array([x_des_pxl, y_des, z_des_pxl, yaw_des_dh])
    state = np.array([qrCX, y_dist, qrCZ, height_diff])
    e = r - state

    kp_x_pxl = -0.06
    kp_y     = -0.4
    kp_z_pxl = 0.17
    Kp = np.diag([kp_x_pxl, kp_y, kp_z_pxl, kp_yaw])

    k_yaw = 0.6
    in2cm = 2.54
    deg2rad = np.pi/180
    R = y_dist * in2cm
    Kp[0][3] = -R*k_yaw*deg2rad

    kd_x_pxl = 0
    kd_y = 0
    kd_z_pxl = 0
    Kd = np.diag([kd_x_pxl, kd_y, kd_z_pxl])

    u = Kp@e
    print(u)
    return int(u[0]), int(u[1]), int(u[2]), int(u[3])







# p1 = np.array([4, 10])
# p2 = np.array([9, 7])
# p3 = np.array([11, 2])
# p4 = np.array([2, 2])

# polygon = np.array([p1,p2,p3,p4])
# print(polygon_area(polygon))