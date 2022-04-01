import time
import cv2 as cv
from components import *
from models import *
from picamera.array import PiRGBArray
from picamera import PiCamera


def on_click(event, x, y, flags, param):
    """
    Process clicks on start and end buttons
    """
    global has_session, db, detect, frame
    bounding_box = Button.end_text if has_session else Button.start_text
    (text_w, text_h), _ = cv.getTextSize(bounding_box,
                                         Button.font, Button.font_size, Button.font_thickness)
    (scan_w, scan_h), _ = cv.getTextSize(Button.scan_text,
                                         Button.font, Button.font_size, Button.font_thickness)
    # check if the click is within the dimensions of the button
    if event == cv.EVENT_LBUTTONDOWN:
        if x > Button.pos[0] and x < Button.pos[0] + text_w + \
                10 and y > Button.pos[1] and y < Button.pos[1] + text_h + 10:
            if not has_session:
                db.new_session()
            has_session = not has_session
        elif x > Button.pos_scan[0] and x < Button.pos_scan[0] + scan_w + \
                10 and y > Button.pos_scan[1] and y < Button.pos_scan[1] + scan_h + 10:
            pass


# Keep state of buttons
has_session = False

# Global access to db
db = Database()


def main():
    # Stolen from https://www.geeksforgeeks.org/python-opencv-capture-video-from-camera/
    # define a video capture object
    # Initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera(resolution=(640, 480), framerate=32)
    cap = PiRGBArray(camera, size=(640, 480))
    time.sleep(2)
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode = 'off'
    camera.awb_gains = (0.0, 0.0)
    # Change to fullscreen
    cv.namedWindow("scanner", cv.WND_PROP_FULLSCREEN)
    cv.setWindowProperty(
        "scanner", cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
    detect = Detect()
    start = time.time()
    for image in camera.capture_continuous(cap, format="bgr", use_video_port=True):
        frame = image.array

        # Draw start / end button
        if not has_session:
            Button.start(frame)
        else:
            Button.end(frame)
            Button.scan(frame)

        if time.time() - start > 1:
            detect.detect(frame)
            start = time.time()
        detect.show_values(frame)

        # frame = detect.draw_ROI(frame)
        # Display the resulting frame
        cv.imshow("scanner", frame)

        cv.setMouseCallback("scanner", on_click)

        cap.truncate(0)

        # the 'q' button is set as the
        # quitting button you may use any
        # desired button of your choice
        if cv.waitKey(10) & 0xFF == ord('q') or cv.waitKey(10) & 0xFF == 27:
            break

    # Destroy all the windows
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
