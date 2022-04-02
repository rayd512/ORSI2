from typing import List
import cv2


class Detect:
    def __init__(self):
        self.cascade = cv2.CascadeClassifier()
        self.resistors = []
        self.MIN_AREA = 700
        self.COLOR_BOUNDS = [
            [(0, 0, 0), (179, 255, 10), "BLACK", 0, (0, 0, 0)],
            [(0, 104, 0), (11, 255, 46), "BROWN", 1, (0, 51, 102)],
            [(0, 30, 50), (6, 255, 200), "RED", 2, (0, 0, 255)],
            [(2, 235, 68), (121, 255, 225), "ORANGE", 3, (0, 128, 255)],
            [(30, 170, 100), (40, 250, 255), "YELLOW", 4, (0, 255, 255)],
            [(35, 20, 110), (60, 45, 120), "GREEN", 5, (0, 255, 0)],
            [(65, 0, 85), (115, 30, 147), "BLUE", 6, (255, 0, 0)],
            [(120, 40, 100), (140, 250, 220), "PURPLE", 7, (255, 0, 127)],
            [(0, 0, 50), (179, 50, 80), "GRAY", 8, (128, 128, 128)],
            [(0, 0, 90), (179, 15, 250), "WHITE", 9, (255, 255, 255)],
        ]
        self.RED_TOP_LOWER = (160, 30, 80)
        self.RED_TOP_UPPER = (179, 255, 200)
        self._load_cascade()

    def _load_cascade(self) -> None:
        if not self.cascade.load(cv2.samples.findFile(
                "src/models/haarcascade_resistors_0.xml")):
            raise Exception("Could not load face cascade!")

    def detect(self, frame: List[int]) -> None:
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        self.resistors = []
        resistors = self.cascade.detectMultiScale(frame_gray, 1.1, 25)
        for i, (x, y, w, h) in enumerate(resistors):
            self.resistors.append(
                {"resistor": resistors[i], "ROI": frame[y:y + h, x:x + w]})

    def draw_ROI(self, frame: List[int]) -> List[int]:
        for (x, y, w, h) in self.resistors:
            frame = cv2.rectangle(
                frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        return frame

    def _find_bands(self, resistor_img) -> None:
        resistor_img = cv2.resize(resistor_img, (400, 200))
        bilateral_filt = cv2.bilateralFilter(resistor_img, 5, 80, 80)
        hsv = cv2.cvtColor(bilateral_filt, cv2.COLOR_BGR2HSV)
        # edge threshold filters out background and resistor body
        thresh = cv2.adaptiveThreshold(
            cv2.cvtColor(
                bilateral_filt,
                cv2.COLOR_BGR2GRAY),
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            59,
            5)
        thresh = cv2.bitwise_not(thresh)

        resistor_pos = []
        for color in self.COLOR_BOUNDS:
            mask = cv2.inRange(hsv, color[0], color[1])
            if (color[2] == "RED"):  # combining the 2 RED ranges in hsv
                redMask2 = cv2.inRange(
                    hsv, self.RED_TOP_LOWER, self.RED_TOP_UPPER)
                mask = cv2.bitwise_or(redMask2, mask, mask)

            mask = cv2.bitwise_and(mask, thresh, mask=mask)

            if (cv2.__version__ == "3.4.16"):
                _, contours, hierarchy = cv2.findContours(
                    mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                contours = list(contours)
            else:
                contours, hierarchy = cv2.findContours(
                    mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # filter invalid contours, store valid ones
            for k in range(len(contours) - 1, -1, -1):
                if (self._valid_contour(contours[k])):
                    left = tuple(
                        contours[k][contours[k][:, :, 0].argmin()][0])
                    resistor_pos += [left + tuple(color[2:])]
                    cv2.circle(bilateral_filt, left,
                               5, (255, 0, 255), -1)
                else:
                    contours.pop(k)

            cv2.drawContours(bilateral_filt, contours, -1, color[-1], 3)
        return sorted(resistor_pos, key=lambda contour: contour[0])

    def _valid_contour(self, contour):
        # looking for a large enough area and correct aspect ratio
        if(cv2.contourArea(contour) < self.MIN_AREA):
            return False
        else:
            x, y, w, h = cv2.boundingRect(contour)
            aspectRatio = float(w) / h
            if (aspectRatio > 0.4):
                return False
        return True

    def show_values(self, frame):
        for i in range(len(self.resistors)):
            bands = self._find_bands(self.resistors[i]["ROI"])
            x, y, w, h = self.resistors[i]["resistor"]
            strVal = ""
            if (len(bands) in [3, 4, 5]):
                for band in bands[:-1]:
                    strVal += str(band[3])
                intVal = int(strVal)
                intVal *= 10**bands[-1][3]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, str(intVal) + " OHMS", (x + w + 10, y),
                            cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 2, cv2.LINE_AA)
                continue
            # draw a red rectangle indicating an error reading the bands
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.imshow("scanner", frame)
