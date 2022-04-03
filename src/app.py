import time
import cv2 as cv
import numpy as np
from components import *
from models import *


def on_click(event, x, y, flags, param):
    """
    Process clicks on start and end buttons
    """
    global has_session, db, detect
    bounding_box = Button.end_text if has_session else Button.start_text
    (text_w, text_h), _ = cv.getTextSize(bounding_box,
                                         Button.font, Button.font_size, Button.font_thickness)
    (scan_w, scan_h), _ = cv.getTextSize(Button.scan_text,
                                         Button.font, Button.font_size, Button.font_thickness)
    # Check if the click is within the dimensions of the button
    if event == cv.EVENT_LBUTTONDOWN:
        if x > Button.pos[0] and x < Button.pos[0] + text_w + \
                10 and y > Button.pos[1] and y < Button.pos[1] + text_h + 10:
            if not has_session:
                db.new_session()
            has_session = not has_session
        elif x > Button.pos_scan[0] and x < Button.pos_scan[0] + scan_w + \
                10 and y > Button.pos_scan[1] and y < Button.pos_scan[1] + scan_h + 10:
            for resistor in detect.resistors:
                if "value" in resistor:
                    db.add_resistor(resistor["value"], resistor["wattage"])


# Keep state of buttons
has_session = False

# Global access to db
db = Database()
detect = Detect()


def main():
    global detect
    # Initialize the camera and grab a reference to the raw camera capture
    cap = cv.VideoCapture(0)

    # Change to fullscreen
    cv.namedWindow("scanner", cv.WND_PROP_FULLSCREEN)
    cv.setWindowProperty(
        "scanner", cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
    start = time.time()

    while True:
        ret, frame = cap.read()

        if time.time() - start > 1:
            detect.detect(frame)
            start = time.time()

        detect.show_values(frame)

        # Draw start / end button
        if not has_session:
            Button.start(frame)
        else:
            Button.end(frame)
            Button.scan(frame)

        cv.imshow("scanner", frame)

        cv.setMouseCallback("scanner", on_click)

        # Set q and ESC to quit program
        if cv.waitKey(10) & 0xFF == ord('q') or cv.waitKey(10) & 0xFF == 27:
            break

    # Destroy all the windows
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
