from djitellopy import Tello
import time
from pyzbar import pyzbar
import argparse
import cv2
import matplotlib.pyplot as plt
import imutils
from imutils.video import VideoStream
import time
import numpy as np
import matplotlib.pyplot as plt


tello = Tello()

tello.connect()
tello.streamon()
time.sleep(3)

print(tello.get_battery())
vs = tello.get_frame_read()
counter = 0
tello.takeoff()
time.sleep(3)
while True:
    counter = counter + 1
    if counter%50 == 0:
        # tello.connect()
        tello.send_command_without_return('rc 0 0 0 30')
    frame = vs.frame
    frame = imutils.resize(frame, width=600)
    
    aprilTags = pyzbar.decode(frame)




    if len(aprilTags) == 0:
        cv2.imshow("Barcode Scanner", frame)
    # Stop the loop by pressing "q"
    key = cv2.waitKey(1) & 0xFF
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
         break

    frameHeight,frameWidth = frame.shape[:2]
    for aprilTag in aprilTags:
        # Find box that surrounds the location of the barcode
        # draw a rectangle around it
        
        (x,y,w,h) = aprilTag.rect
        radius = np.min([w,h])//8
        qrCX = x+w//2
        qrCY = y+h//2
        
        colorFound = (0,255,0)
        colorSquareNotFound = (255,255,120)
        colorCircleNotFound = (255,50,100)
        yellow = (0,255,255)
        colorPolyNotFound   = yellow

        currentSquareColor = colorSquareNotFound
        currentCircleColor = colorCircleNotFound
        currentPolyColor   = colorPolyNotFound

        centeredEpsilon = 50
        centeredEpsilonXRatio = .35
        centeredEpsilonYRatio = .6
        centered = abs(qrCX - frameWidth//2) < 50 and abs(qrCY - frameHeight//2) <= 50
        
        closeEnough = w/frameWidth > centeredEpsilonXRatio and h/frameHeight > centeredEpsilonYRatio
        if centered and closeEnough:
            currentSquareColor = colorFound
            currentCircleColor = colorFound
            currentPolyColor   = colorFound
        cv2.circle(frame,(qrCX,qrCY), radius, currentCircleColor, -1)
        polygon   = np.array(aprilTag.polygon)
        polygon = polygon.reshape((-1,1,2))

        cv2.polylines(frame,[polygon],True,currentPolyColor,5)

        cv2.rectangle(frame, (x, y), (x + w, y + h), currentSquareColor, 3)

        centerQR = (qrCX,qrCY)

        # Add Direction to move in:
        
        if qrCX < frameWidth/2 and abs(qrCX - frameWidth/2) > centeredEpsilon/2:
            scaling = 2* abs(qrCX - frameWidth//2)/frameWidth
            arrowHeadX = int(qrCX + frameWidth//4*scaling)
            arrowHeadY = qrCY
            arrowHead = (arrowHeadX,arrowHeadY)
            cv2.arrowedLine(frame,centerQR,arrowHead,(255,255,255),2)
        elif qrCX > frameWidth/2 and abs(qrCX - frameWidth/2) > centeredEpsilon/2:
            scaling = 2* abs(qrCX - frameWidth//2)/frameWidth
            arrowHeadX = int(qrCX - frameWidth//4*scaling)
            arrowHeadY = qrCY
            arrowHead = (arrowHeadX,arrowHeadY)
            cv2.arrowedLine(frame,centerQR,arrowHead,(255,255,255),2)
        if qrCY < frameHeight/2 and abs(qrCY - frameHeight/2) > centeredEpsilon/2:
            scaling = 2* abs(qrCY - frameHeight//2)/frameHeight
            arrowHeadX = qrCX 
            arrowHeadY = int(qrCY+frameHeight//4*scaling)
            arrowHead = (arrowHeadX,arrowHeadY)
            cv2.arrowedLine(frame,centerQR,arrowHead,(255,255,255),2)
        if qrCY >= frameHeight/2 and abs(qrCY- frameHeight/2) > centeredEpsilon/2:
            scaling = 2* abs(qrCY - frameHeight//2)/frameHeight
            arrowHeadX = qrCX 
            arrowHeadY = int(qrCY-frameHeight//4*scaling)
            arrowHead = (arrowHeadX,arrowHeadY)
            cv2.arrowedLine(frame,centerQR,arrowHead,(255,255,255),2)
        # Currently, data in QR code is a bytes object.
        # Convert it to a string 
        aprilTagData = aprilTag.data.decode("utf-8")
        text = "Data:{}".format(aprilTagData)
        cv2.putText(frame,text,(x,y-10),cv2.FONT_HERSHEY_TRIPLEX,0.5,(0,0,255),2)
        
        # Output the info found to command line
        # print("Found a April Tag with this data: {}".format(aprilTagData))

        # show the output frame
        cv2.imshow("Barcode Scanner", frame)
        key = cv2.waitKey(1) & 0xFF
     
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

# # When everything done, release the capture

cv2.destroyAllWindows()


'''
# while(True):
#     # Capture frame-by-frame

#     ret, frame = cap.read()
    
#     aprilTags = pyzbar.decode(frame)
#     # resize so its not huge!!
    # frame = imutils.resize(frame, width=600)

#     cv2.imshow("Barcode Scanner", frame)
    
#     key = cv2.waitKey(1) & 0xFF
#     # if the `q` key was pressed, break from the loop
#     if key == ord("q"):
#         break
'''

# # When everything done, release the capture
# cap.release()
tello.send_command_without_return('rc 0 0 0 0')
time.sleep(3)
tello.land()
vs.stop()
tello.streamoff()
tello.end()


# key = cv2.waitKey(1) & 0xFF
#     # if the `q` key was pressed, break from the loop
#     if key == ord("q"):
#          break