
import cv2
import numpy as np
from components import *

button = [20, 60, 50, 250]


def process_click(event, x, y, flags, params):
    # check if the click is within the dimensions of the button
    if event == cv2.EVENT_LBUTTONDOWN:
        if y > button[0] and y < button[1] and x > button[2] and x < button[3]:
            print('Clicked on Button!')


def main():
    # Stolen from https://www.geeksforgeeks.org/python-opencv-capture-video-from-camera/
    # define a video capture object
    vid = cv2.VideoCapture(0)

    while(True):

        # Capture the video frame
        # by frame
        ret, frame = vid.read()

        # Draw start button
        Button.end(frame)

        # Change to fullscreen
        cv2.namedWindow("scanner", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(
            "scanner", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        # Display the resulting frame
        cv2.imshow("scanner", frame)

        # cv2.setMouseCallback("scanner", process_click)

        # the 'q' button is set as the
        # quitting button you may use any
        # desired button of your choice
        if cv2.waitKey(1) & 0xFF == ord('q') or cv2.waitKey(20) & 0xFF == 27:
            break

    # After the loop release the cap object
    vid.release()
    # Destroy all the windows
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
