from typing import List
import cv2 as cv


class Detect:
    def __init__(self):
        self.cascade = cv.CascadeClassifier()
        self.resistors = []

        if not self.cascade.load(cv.samples.findFile(
                "src/models/haarcascade_resistors_0.xml")):
            raise Exception("Could not load face cascade!")

    def detect(self, frame: List[int]) -> None:
        frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        self.resistors = self.cascade.detectMultiScale(frame_gray, 1.1, 25)
        self.resistor_imgs = []
        for (x, y, w, h), i in enumerate(self.resistors):
            if not self.cascade.detectMultiScale(frame_gray[y:y+h, x:x+w], 1.1, 25):
                self.resistors.pop(i)
            else:
                self.resistor_imgs.append(frame[y:y+h, x:x+w])

    def draw_ROI(self, frame: List[int]) -> List[int]:
        for (x, y, w, h) in self.resistors:
            frame = cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        return frame
