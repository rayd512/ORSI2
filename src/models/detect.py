from typing import List
import cv2 as cv


class Detect:
    def __init__(self):
        self.cascade = cv.CascadeClassifier()
        self.resistors = []
        self.MIN_AREA = 700
        self.COLOR_BOUNDS = [
            [(0, 0, 0), (179, 255, 93), "BLACK", 0, (0, 0, 0)],
            [(0, 90, 10), (15, 250, 100), "BROWN", 1, (0, 51, 102)],
            [(0, 30, 80), (10, 255, 200), "RED", 2, (0, 0, 255)],
            [(10, 70, 70), (25, 255, 200), "ORANGE", 3, (0, 128, 255)],
            [(30, 170, 100), (40, 250, 255), "YELLOW", 4, (0, 255, 255)],
            [(35, 20, 110), (60, 45, 120), "GREEN", 5, (0, 255, 0)],
            [(65, 0, 85), (115, 30, 147), "BLUE", 6, (255, 0, 0)],
            [(120, 40, 100), (140, 250, 220), "PURPLE", 7, (255, 0, 127)],
            [(0, 0, 50), (179, 50, 80), "GRAY", 8, (128, 128, 128)],
            [(0, 0, 90), (179, 15, 250), "WHITE", 9, (255, 255, 255)],
        ]
        self.RED_TOP_LOWER = (160, 30, 80)
        self.RED_TOP_UPPER = (179, 255, 200)
        if not self.cascade.load(cv.samples.findFile(
                "src/models/haarcascade_resistors_0.xml")):
            raise Exception("Could not load face cascade!")

    def detect(self, frame: List[int]) -> None:
        frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        self.resistors = []
        self.resistor_imgs = []
        resistors = self.cascade.detectMultiScale(frame_gray, 1.1, 25)
        for i, (x, y, w, h) in enumerate(resistors):
            if len(self.cascade.detectMultiScale(
                    frame_gray[y:y + h, x:x + w], 1.1, 25)) > 0 or True:
                self.resistors.append(resistors[i])
                self.resistor_imgs.append(frame[y:y + h, x:x + w])

    def draw_ROI(self, frame: List[int]) -> List[int]:
        for (x, y, w, h) in self.resistors:
            frame = cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        return frame

    def _bands(self, resistor_img) -> None:
        resistor_img = cv.resize(resistor_img, (400, 200))
        bilateral_filt = cv.bilateralFilter(resistor_img, 5, 80, 80)
        hsv = cv.cvtColor(bilateral_filt, cv.COLOR_BGR2HSV)
        # edge threshold filters out background and resistor body
        thresh = cv.adaptiveThreshold(cv.cvtColor(
            bilateral_filt, cv.COLOR_BGR2GRAY), 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 59, 5)
        thresh = cv.bitwise_not(thresh)

        resistor_pos = []
        for color in self.COLOR_BOUNDS:
            mask = cv.inRange(hsv, color[0], color[1])
            if (color[2] == "RED"):  # combining the 2 RED ranges in hsv
                redMask2 = cv.inRange(
                    hsv, self.RED_TOP_LOWER, self.RED_TOP_UPPER)
                mask = cv.bitwise_or(redMask2, mask, mask)

            mask = cv.bitwise_and(mask, thresh, mask=mask)
            contours, hierarchy = cv.findContours(
                mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

            # filter invalid contours, store valid ones
            for k in range(len(contours)-1, -1, -1):
                if (self._valid_contour(contours[k])):
                    left = tuple(
                        contours[k][contours[k][:, :, 0].argmin()][0])
                    resistor_pos += [left + tuple(color[2:])]
                    cv.circle(bilateral_filt, left,
                              5, (255, 0, 255), -1)
                else:
                    contours.pop(k)

            cv.drawContours(bilateral_filt, contours, -1, color[-1], 3)
        return sorted(resistor_pos, key=lambda contour: contour[0])

    def _valid_contour(self, contour):
        # looking for a large enough area and correct aspect ratio
        if(cv.contourArea(contour) < self.MIN_AREA):
            return False
        else:
            x, y, w, h = cv.boundingRect(contour)
            aspectRatio = float(w)/h
            if (aspectRatio > 0.4):
                return False
        return True

    def show_values(self, frame):
        for i in range(len(self.resistors)):
            bands = self._bands(self.resistor_imgs[i])
            print(bands)
            # printResult(bands, cliveimg, resClose[i][1])
            x, y, w, h = self.resistors[i]
            strVal = ""
            if (len(bands) in [3, 4, 5]):
                print("yeah")
                for band in bands[:-1]:
                    strVal += str(band[3])
                intVal = int(strVal)
                intVal *= 10**bands[-1][3]
                cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv.putText(frame, str(intVal) + " OHMS", (x+w+10, y),
                           cv.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 2, cv.LINE_AA)
                continue
            # draw a red rectangle indicating an error reading the bands
            cv.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
        cv.imshow("scanner", frame)
