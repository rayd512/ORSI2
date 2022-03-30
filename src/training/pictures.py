import cv2
import os


def main():
    # Stolen from https://www.geeksforgeeks.org/python-opencv-capture-video-from-camera/
    # define a video capture object
    # Initialize the camera and grab a reference to the raw camera capture
    path = "src/training/images"
    num_files = len([f for f in os.listdir(
        path)if os.path.isfile(os.path.join(path, f))]) + 1
    cap = cv2.VideoCapture(0)

    # Change to fullscreen
    cv2.namedWindow("scanner", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(
        "scanner", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:
        ret, frame = cap.read()

        cv2.imshow("scanner", frame)

        # the 'q' button is set as the
        # quitting button you may use any
        # desired button of your choice
        key = cv2.waitKey(10) & 0xFF
        if key == ord('q') or key == 27:
            break
        elif key == ord('c'):
            print("Picture Taken")
            cv2.imwrite(f'{path}/{num_files}.png', frame)
            num_files += 1

    # Destroy all the windows
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
