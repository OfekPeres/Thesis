'''
This class will represent a drone object, which will be able to tell the Tello what to do
at a higher level (i.e. hover) and will also keep track of keyboard inputs.

Keyboard events are tracked using the python modeul pynput, which on MacOSX needs access to
the accessibility features found in system preferences (need to grant access to python, pycharm, and terminal)
'''
import time
import pygame
from djitellopy import Tello
import cv2
import numpy as np
import imutils
import matplotlib.pyplot as plt
from pyzbar import pyzbar
from tello_utils import get_y, polygon_area, get_x, get_z_measurement, get_z, draw_april_tag_bounding_box, get_control_inputs, get_pid_control_inputs
# Some keyboard keys print the wrong thing, so here is a dictionary to fix some of them
key_dict = {"Key.media_volume_up":"a", "Key.media_volume_down":'s','Key.media_next':'t'}

SPEED = 50
FPS = 15
HAS_NOT_SEEN_QR_CODE = 0
TRACKING_QR_CODE = 1
LOST_QR_CODE = 2
Found_and_Centered_on_QR_Code = 3
landed = 4
class Drone:

    def __init__(self):  
        self.forward_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.speed = 10
        self.rc_mode = True
        self.drone_state = 'landed'
        self.stage = HAS_NOT_SEEN_QR_CODE
        self.program_active = True
        self.tello = Tello()
        self.centered = False
        self.closeEnough = False
        self.land = False
        self.e_integral = np.array([0,0,0,0])
        self.e_prev = np.array([0,0,0,0])

        # Setup pygame window
        pygame.init()
        # self.screen = pygame.display.set_mode([960,720])
        self.screen = pygame.display.set_mode([600,450])
        pygame.display.set_caption("Tello Video Stream")
        # create update timer
        pygame.time.set_timer(pygame.USEREVENT + 1, 50)



    # Code very similar to example.py from DJItello. Adapted to use
    # opencv instead of pygame
    def activate(self):
        
        self.tello.connect()
        self.tello.streamon()

        print(self.tello.get_battery())

        vs = self.tello.get_frame_read()
        time.sleep(2)
        # prepare time loop to run for 1 minute

        while self.program_active:

            for event in pygame.event.get():

                if event.type == pygame.USEREVENT + 1:
                    self.update()
                elif event.type == pygame.QUIT:
                    self.program_active = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.program_active = False
                    else:
                        self.keydown(event.key)
                elif event.type == pygame.KEYUP:
                    self.keyup(event.key)
            if vs.stopped:
                vs.stop()
                break


            frame = vs.frame
            frame = imutils.resize(frame, width=600)
            

            # Find QR Codes in Image
            aprilTags = pyzbar.decode(frame)
            # print("AprilTags is: {}".format(aprilTags))
            # print("Length of AprilTags is: {}".format(len(aprilTags)))
            
            # print("Current stage is: {}".format(self.stage))
            # for aprilTag in aprilTags:
            #     draw_april_tag_bounding_box(frame, aprilTag, self.centered, self.closeEnough)
            #     if not self.rc_mode:
            #         # self.left_right_velocity, self.forward_back_velocity, self.up_down_velocity, self.yaw_velocity, = get_pid_control_inputs(frame,aprilTag)
            #         self.controller(frame, aprilTag)
            #         # self.left_right_velocity, self.forward_back_velocity, self.up_down_velocity, self.yaw_velocity, self.centered, self.closeEnough = get_control_inputs(frame,aprilTag)
            
            if len(aprilTags) >= 1:
                aprilTag = aprilTags[0]
            else:
                aprilTag = None
            if aprilTag is not None:
                draw_april_tag_bounding_box(frame, aprilTag, self.centered, self.closeEnough)
            if not self.rc_mode:
                self.stageUpdate(len(aprilTags))
                self.controller(frame, aprilTag)

            # Prepare image for display in Pygame
            self.screen.fill([0,0,0])
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = np.flipud(frame)
            frame = pygame.surfarray.make_surface(frame)
            self.screen.blit(frame,(0,0))
            pygame.display.update()

            time.sleep(1/FPS)

        print(self.tello.get_battery())
        self.tello.end()
        pygame.quit()

    # Functions to update actions
    def keydown(self, key):
        """ Update velocities based on key pressed
        Arguments:
            key: pygame key
        """
        if key == pygame.K_UP:  # set forward velocity
            self.forward_back_velocity = SPEED
        elif key == pygame.K_DOWN:  # set backward velocity
            self.forward_back_velocity = -SPEED
        elif key == pygame.K_LEFT:  # set left velocity
            self.left_right_velocity = -SPEED
        elif key == pygame.K_RIGHT:  # set right velocity
            self.left_right_velocity = SPEED
        elif key == pygame.K_w:  # set up velocity
            self.up_down_velocity = SPEED
        elif key == pygame.K_s:  # set down velocity
            self.up_down_velocity = -SPEED
        elif key == pygame.K_a:  # set yaw counter clockwise velocity
            self.yaw_velocity = -SPEED
        elif key == pygame.K_d:  # set yaw clockwise velocity
            self.yaw_velocity = SPEED
        elif key == pygame.K_m:
            self.rc_mode = not self.rc_mode
            print(self.rc_mode)
            self.forward_back_velocity = 0
            self.left_right_velocity = 0
            self.up_down_velocity = 0
            self.yaw_velocity = 0
        elif key == pygame.K_h:
            self.rc_mode = True
            self.forward_back_velocity = 0
            self.left_right_velocity = 0
            self.up_down_velocity = 0
            self.yaw_velocity = 0
            print(self.rc_mode)
            print("Hovering")
        elif key == pygame.K_r:
            self.stage = HAS_NOT_SEEN_QR_CODE
            self.rc_mode = True
            self.forward_back_velocity = 0
            self.left_right_velocity = 0
            self.up_down_velocity = 0
            self.yaw_velocity = 0
            self.e_integral = np.array([0,0,0,0])
            self.e_derivative = np.array([0,0,0,0])
            print(self.rc_mode)
            print("Hovering")



    def keyup(self, key):
        """ Update velocities based on key released
        Arguments:
            key: pygame key
        """
        if key == pygame.K_UP or key == pygame.K_DOWN:  # set zero forward/backward velocity
            self.forward_back_velocity = 0
        elif key == pygame.K_LEFT or key == pygame.K_RIGHT:  # set zero left/right velocity
            self.left_right_velocity = 0
        elif key == pygame.K_w or key == pygame.K_s:  # set zero up/down velocity
            self.up_down_velocity = 0
        elif key == pygame.K_a or key == pygame.K_d:  # set zero yaw velocity
            self.yaw_velocity = 0
        elif key == pygame.K_t:  # takeoff
            self.tello.takeoff()
            self.send_rc_control = True
        elif key == pygame.K_l:  # land
            self.tello.land()
            self.send_rc_control = False
        
    def update(self):
        """ Update routine. Send velocities to Tello."""
        # if self.rc_mode:
        command = "rc {} {} {} {}".format(self.left_right_velocity, self.forward_back_velocity, self.up_down_velocity,
                                   self.yaw_velocity)
        printInfo = False
        self.tello.send_command_without_return(command, printInfo)
        # self.tello.send_rc_control(self.left_right_velocity, self.forward_back_velocity, self.up_down_velocity,
        #                            self.yaw_velocity)
        
    def controller(self, frame, aprilTag):
        if self.stage == HAS_NOT_SEEN_QR_CODE:
            self.rotate()
        if self.stage == TRACKING_QR_CODE and aprilTag is not None:
            self.left_right_velocity, self.forward_back_velocity, self.up_down_velocity, self.yaw_velocity, self.e_integral, self.e_prev, self.land = get_pid_control_inputs(frame,aprilTag, self.e_integral, self.e_prev)
        if self.stage == LOST_QR_CODE:
            self.backup()
        if self.stage == Found_and_Centered_on_QR_Code:
            command = "rc {} {} {} {}".format(0, 0, 0, 0)
            printInfo = False
            self.tello.send_command_without_return(command, printInfo)
            self.tello.land()
            self.stage = landed
        if self.stage == landed:
            command = "rc {} {} {} {}".format(0, 0, 0, 0)
            printInfo = False
            self.tello.send_command_without_return(command, printInfo)
            



    def stageUpdate(self, numQRCodes):
        # print("Number of QR Codes is: {}".format(numQRCodes))
        # print("Stage in stageUpdate is: {}".format(self.stage))
        if self.stage == HAS_NOT_SEEN_QR_CODE and numQRCodes >= 1:
            self.stage = TRACKING_QR_CODE

        elif self.stage == TRACKING_QR_CODE and numQRCodes == 0:
            self.stage = LOST_QR_CODE

        elif self.stage == LOST_QR_CODE and numQRCodes >= 1:
            self.stage = TRACKING_QR_CODE
        elif self.stage == TRACKING_QR_CODE and self.land == True:
            self.stage = Found_and_Centered_on_QR_Code
            
            


    def rotate(self):
        print("Rotating")
        self.left_right_velocity = 0
        self.forward_back_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 20


    def backup(self):
        print("Backing up")
        self.left_right_velocity = 0
        self.forward_back_velocity = -15
        self.up_down_velocity = 0
        self.yaw_velocity = 0

        

test_drone = Drone()
test_drone.activate()



