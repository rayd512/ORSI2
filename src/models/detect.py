from typing import List
import cv2


class Detect:
    class Band:
        BAND_DEFAULTS = [
            [(0, 0, 0), (179, 255, 2), "BLACK", 0, (0, 0, 0)],
            [(0, 104, 0), (11, 255, 46), "BROWN", 1, (0, 51, 102)],
            [(0, 220, 30), (179, 255, 100), "RED", 2, (0, 0, 255)],
            [(4, 230, 75), (18, 255, 180), "ORANGE", 3, (0, 128, 255)],
            [(20, 200, 15), (30, 255, 185), "YELLOW", 4, (0, 255, 255)],
            [(35, 130, 0), (70, 255, 255), "GREEN", 5, (0, 255, 0)],
            [(100, 150, 0), (140, 255, 70), "BLUE", 6, (255, 0, 0)],
            [(100, 80, 40), (130, 255, 255), "PURPLE", 7, (255, 0, 127)],
            [(0, 20, 0), (179, 180, 60), "GRAY", 8, (128, 128, 128)],
            [(0, 0, 90), (179, 15, 250), "WHITE", 9, (255, 255, 255)],
        ]

        def __init__(self, lower_hsv, upper_hsv, color, multiplier, draw_color) -> None:
            self.lower_hsv = lower_hsv
            self.upper_hsv = upper_hsv
            self.color = color
            self.multiplier = multiplier
            self.draw_color = draw_color

    def __init__(self):
        self.cascade = cv2.CascadeClassifier()
        self.resistors = []
        self.MIN_AREA = 400
        self.HORIZ_MARG = 40
        self.BANDS = [self.Band(*band_param)
                      for band_param in self.Band.BAND_DEFAULTS]
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
                {"resistor": resistors[i], "ROI": frame[y:y + h, x:x + w].copy()})

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
        # invalid_contours = []
        for band in self.BANDS:
            mask = cv2.inRange(hsv, band.lower_hsv, band.upper_hsv)

            # mask = cv2.bitwise_and(mask, thresh, mask=mask)
            # cv2.imshow("scanner", mask)
            # print(band.color)

            # while cv2.waitKey(10) & 0xFF != ord('n'):
            #     pass
            if (cv2.__version__ == "3.4.16"):
                _, contours, hierarchy = cv2.findContours(
                    mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                contours = list(contours)
            else:
                contours, hierarchy = cv2.findContours(
                    mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                contours = list(contours)
            # filter invalid contours, store valid ones
            for i in range(len(contours) - 1, -1, -1):
                if (self._valid_contour(contours[i])):
                    band_left = tuple(
                        contours[i][contours[i][:, :, 0].argmin()][0])
                    found_close_band = False
                    for position in resistor_pos:
                        if abs(position[0] - band_left[0]) < self.HORIZ_MARG:
                            contours.pop(i)
                            found_close_band = True
                            break
                    if found_close_band:
                        continue
                    # resistor_pos += [band_left +
                    #                  (band.color, band.multiplier, band.draw_color)]
                    resistor_pos.append((*band_left, band))
                    cv2.circle(bilateral_filt, band_left,
                               5, (255, 0, 255), -1)
                else:
                    contours.pop(i)

            cv2.drawContours(bilateral_filt, contours, -
                             1, (band.draw_color), 3)
        # cv2.imshow("scanner", bilateral_filt)
        # while cv2.waitKey(10) & 0xFF != ord('n'):
        #     pass
        return sorted(resistor_pos, key=lambda contour: contour[0])

    def _valid_contour(self, contour):
        # looking for a large enough area and correct aspect ratio
        if(cv2.contourArea(contour) < self.MIN_AREA):
            return False
        x, y, w, h = cv2.boundingRect(contour)
        aspectRatio = float(w) / h
        if (aspectRatio > 1.5):
            return False
        return True

    def show_values(self, frame):
        fallback_value = None
        for i in range(len(self.resistors)):
            bands = self._find_bands(self.resistors[i]["ROI"])
            x, y, w, h = self.resistors[i]["resistor"]
            resistor_val = ""
            if (len(bands) in [3, 4, 5]):
                for band in bands[:-1]:
                    resistor_val += str(band[-1].multiplier)
                resistor_val = int(resistor_val)
                resistor_val *= 10**bands[-1][-1].multiplier
                fallback_value = resistor_val
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, str(resistor_val) + " OHMS", (x + w + 10, y),
                            cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 2, cv2.LINE_AA)
                continue

            if fallback_value:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, str(fallback_value) + " OHMS", (x + w + 10, y),
                            cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 2, cv2.LINE_AA)
            else:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.imshow("scanner", frame)
