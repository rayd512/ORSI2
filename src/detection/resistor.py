from __future__ import print_function
import cv2 as cv
import numpy as np
import argparse

detected = False
resistors = []

def detectAndDisplay(frame):
    global resistors
    frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # frame_gray = cv.equalizeHist(frame_gray)
    #-- Detect resistors
    resistors = resistor_cascade.detectMultiScale(frame_gray, 1.1, 25)
    for (x,y,w,h) in resistors:
        frame = cv.rectangle(frame, (x,y), (x+w, y+h), (255, 0, 0), 2)
        #frame = cv.line(frame, (x, int(y+(h/2))), (x+w, int(y+(h/2))), (0, 0, 255), 1)
        print(frame[x:x+w, int(y+(h/2))])
        # ROI = frame_gray[y:y+h, x:x+w]
        # secondPass = resistor_cascade.detectMultiScale(ROI, 1.01, 25)
        # for (x1,y1,w1,h1) in secondPass:
        #     frame = cv.rectangle(frame, (x+x1,y+y1), (x+x1+w1, y+y1+h1), (0, 255, 0), 2)
    cv.imshow('Capture - Resistor detection', frame)

def display(frame):

    for(x,y,w,h) in resistors:
        frame = cv.rectangle(frame, (x,y), (x+w, y+h), (255, 0, 0), 2)
        #frame = cv.line(frame, (x, int(y+(h/2))), (x+w, int(y+(h/2))), (0, 0, 255), 1)
    cv.imshow('Capture - Resistor detection', frame)


parser = argparse.ArgumentParser(description='Code for Resistor Detector.')
parser.add_argument('--resistor_cascade', help='Path to resistor cascade.', default='haarcascade_resistors_0.xml')
parser.add_argument('--camera', help='Camera divide number.', type=int, default=0)

args = parser.parse_args()
resistor_cascade_name = args.resistor_cascade
resistor_cascade = cv.CascadeClassifier()

#-- 1. Load the cascade
if not resistor_cascade.load(cv.samples.findFile(resistor_cascade_name)):
    print('--(!)Error loading face cascade')
    exit(0)


camera_device = args.camera

#-- 2. Read the video stream
cap = cv.VideoCapture(camera_device)
counter = 100

if not cap.isOpened:
    print('--(!)Error opening video capture')
    exit(0)
while True:
    ret, frame = cap.read()
    if frame is None:
        print('--(!) No captured frame -- Break!')
        break
    if counter % 100 != 0:
        display(frame)
        counter = counter + 1
    elif counter % 100 == 0:
        detectAndDisplay(frame)
        counter = 0
        if len(resistors) == 1:
            exit(0)
    if cv.waitKey(100) == 27: # ESC key
        break
