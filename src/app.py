
import cv2 as cv
import numpy as np
from components import *
from models import *


def on_click(event, x, y, flags, param):
    """
    Process clicks on start and end buttons
    """
    global hasSession, db
    bounding_box = Button.end_text if hasSession else Button.start_text
    (text_w, text_h), _ = cv.getTextSize(bounding_box,
                                         Button.font, Button.font_size, Button.font_thickness)
    # check if the click is within the dimensions of the button
    if event == cv.EVENT_LBUTTONDOWN:
        if x > Button.pos[0] and x < Button.pos[0] + text_w + 10 and y > Button.pos[1] and y < Button.pos[1] + text_h + 10:
            if not hasSession:
                db.new_session()
            hasSession = not hasSession


# Keep state of buttons
hasSession = False

# Global access to db
db = Database()


def main():
    # Stolen from https://www.geeksforgeeks.org/python-opencv-capture-video-from-camera/
    # define a video capture object
    # Initialize the camera and grab a reference to the raw camera capture
    cap = cv.VideoCapture(0)

    # Change to fullscreen
    cv.namedWindow("scanner", cv.WND_PROP_FULLSCREEN)
    cv.setWindowProperty(
        "scanner", cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
    detect = Detect()
    counter = 0
    while True:
        ret, frame = cap.read()

        # Draw start / end button
        if not hasSession:
            Button.start(frame)
        else:
            Button.end(frame)
            Button.scan(frame)

        if counter % 100 == 0:
            detect.detect(frame)
            frame = detect.draw_ROI(frame)
            counter = 0
        else:
            counter += 1
            # Display the resulting frame
        cv.imshow("scanner", frame)

        cv.setMouseCallback("scanner", on_click)

        # the 'q' button is set as the
        # quitting button you may use any
        # desired button of your choice
        if cv.waitKey(10) & 0xFF == ord('q') or cv.waitKey(10) & 0xFF == 27:
            break

    # Destroy all the windows
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
