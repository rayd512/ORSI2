
import cv2
import numpy as np

button = [20, 60, 50, 250]


def process_click(event, x, y, flags, params):
    # check if the click is within the dimensions of the button
    if event == cv2.EVENT_LBUTTONDOWN:
        if y > button[0] and y < button[1] and x > button[2] and x < button[3]:
            print('Clicked on Button!')


def draw_text(img, text,
              font=cv2.FONT_HERSHEY_PLAIN,
              pos=(0, 0),
              font_scale=3,
              font_thickness=2,
              text_color=(0, 255, 0),
              text_color_bg=(0, 0, 0)
              ):

    x, y = pos
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_w, text_h = text_size
    cv2.rectangle(img, pos, (x + text_w, y + text_h), text_color_bg, -1)
    cv2.putText(img, text, (x, y + text_h + font_scale - 1),
                font, font_scale, text_color, font_thickness)

    return text_size


def main():
    # Stolen from https://www.geeksforgeeks.org/python-opencv-capture-video-from-camera/
    # define a video capture object
    vid = cv2.VideoCapture(0)

    while(True):

        # Capture the video frame
        # by frame
        ret, frame = vid.read()

        # create button image
        # control_image = np.zeros((40, 200, 3), np.uint8)

        # control_image[button[0]:button[1], button[2]:button[3]] = 255
        draw_text(frame, "Start", font_scale=4, pos=(
            10, 20))

        # frame[button[0]:button[1], button[2]:button[3]] = control_image

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
