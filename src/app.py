
import cv2
import numpy as np
from components import *
from models import *


def on_click(event, x, y, flags, param):
    """
    Process clicks on start and end buttons
    """
    global hasSession, db
    bounding_box = Button.end_text if hasSession else Button.start_text
    (text_w, text_h), _ = cv2.getTextSize(bounding_box,
                                          Button.font, Button.font_size, Button.font_thickness)
    # check if the click is within the dimensions of the button
    if event == cv2.EVENT_LBUTTONDOWN:
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
    vid = cv2.VideoCapture(0)
    while(True):

        # Capture the video frame
        # by frame
        ret, frame = vid.read()

        # Draw start / end button
        if not hasSession:
            Button.start(frame)
        else:
            Button.end(frame)

        # Change to fullscreen
        cv2.namedWindow("scanner", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(
            "scanner", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        # Display the resulting frame
        cv2.imshow("scanner", frame)

        cv2.setMouseCallback("scanner", on_click)

        # the 'q' button is set as the
        # quitting button you may use any
        # desired button of your choice
        if cv2.waitKey(1) & 0xFF == ord('q') or cv2.waitKey(1) & 0xFF == 27:
            break

    # After the loop release the cap object
    vid.release()
    # Destroy all the windows
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
