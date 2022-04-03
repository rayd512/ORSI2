from typing import List, Union
import cv2


# Used to detect resistors and determine it's wattage and values
# Detection was created and based off of https://github.com/dishonesthips/OhmVision
class Detect:
    # Inner class used to store data on bands that could exist on resistor
    class Band:
        # Default values for resistor band color ranges, multipliers and draw
        # color
        BAND_DEFAULTS = [
            [(0, 0, 0), (179, 255, 2), "BLACK", 0, (0, 0, 0)],
            [(0, 104, 0), (5, 255, 46), "BROWN", 1, (0, 51, 102)],
            [(0, 220, 30), (2, 255, 100), "RED", 2, (0, 0, 255)],
            [(5, 165, 75), (15, 255, 180), "ORANGE", 3, (0, 128, 255)],
            [(22, 200, 15), (30, 255, 185), "YELLOW", 4, (0, 255, 255)],
            [(35, 130, 0), (70, 255, 255), "GREEN", 5, (0, 255, 0)],
            [(100, 150, 0), (120, 255, 35), "BLUE", 6, (255, 0, 0)],
            [(122, 100, 20), (179, 255, 255), "PURPLE", 7, (255, 0, 127)],
            [(0, 20, 0), (179, 180, 60), "GRAY", 8, (128, 128, 128)],
            [(0, 0, 90), (179, 15, 250), "WHITE", 9, (255, 255, 255)],
        ]

        def __init__(
                self,
                lower_hsv,
                upper_hsv,
                color,
                multiplier,
                draw_color) -> None:
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
        """
        Loads the machine learning model
        """
        if not self.cascade.load(cv2.samples.findFile(
                "src/models/haarcascade_resistors_0.xml")):
            raise Exception("Could not load face cascade!")

    def detect(self, frame: List[int]) -> None:
        """
        Detects resistors in the current frame
        :param List[int] frame the current frame from opencv video capture
        """
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        self.resistors = []
        resistors = self.cascade.detectMultiScale(frame_gray, 1.1, 25)
        for i, (x, y, w, h) in enumerate(resistors):
            self.resistors.append(
                {"resistor": resistors[i], "ROI": frame[y:y + h, x:x + w].copy()})

    def draw_ROI(self, frame: List[int]) -> List[int]:
        """
        Draws a bounding box on a detected resistor
        :param List[int] frame the current frame from opencv video capture
        """
        for (x, y, w, h) in self.resistors:
            frame = cv2.rectangle(
                frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        return frame

    def _find_bands(self, resistor_img: List[int]) -> None:
        """
        Finds bands on an ROI of a resistor
        :param List[int] resistor_img cropped version of
        current frame containing only the current resistor
        """

        resistor_img = cv2.resize(resistor_img, (400, 200))
        bilateral_filt = cv2.bilateralFilter(resistor_img, 5, 80, 80)
        hsv = cv2.cvtColor(bilateral_filt, cv2.COLOR_BGR2HSV)

        band_pos = []

        # Mask out for each color and check for contours
        for band in self.BANDS:
            mask = cv2.inRange(hsv, band.lower_hsv, band.upper_hsv)

            contours, hierarchy = cv2.findContours(
                mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours = list(contours)

            # Discard or store contours
            for i in range(len(contours) - 1, -1, -1):
                if (self._valid_contour(contours[i])):
                    # Find the left most portion of the contour
                    band_left = tuple(
                        contours[i][contours[i][:, :, 0].argmin()][0])

                    # Check if we have a contour that is in the same vertical
                    # plane
                    found_close_band = False
                    for position in band_pos:
                        if abs(position[0] - band_left[0]) < self.HORIZ_MARG:
                            contours.pop(i)
                            found_close_band = True
                            break
                    if found_close_band:
                        continue

                    # Store the position of the band and it's information
                    band_pos.append((*band_left, band))

                    # Draw a circle for debugging
                    cv2.circle(bilateral_filt, band_left,
                               5, (255, 0, 255), -1)
                else:
                    contours.pop(i)

        return sorted(band_pos, key=lambda contour: contour[0])

    def _valid_contour(self, contour):
        """
        Filter out any false positive contours by checkings its area and aspect ratio
        :param contour the contour to check validity on
        """
        area = cv2.contourArea(contour)
        if(area < self.MIN_AREA):
            return False
        x, y, w, h = cv2.boundingRect(contour)
        aspectRatio = float(w) / h
        if (aspectRatio > 1.5):
            return False
        return True

    def _get_wattage(self, frame: List[int]) -> Union[int, None]:
        """
        Determines the wattage of the current resistor
        :param List[int] resistor_img cropped version of
        current frame containing only the current resistor
        """

        # Default detection values
        WATTAGES = {45: "1/8", 75: "1/4", 100: "1/2"}
        lower_hsv = (0, 100, 0)
        upper_hsv = (179, 255, 255)

        # Mask off to isolate the resistor body
        frame = cv2.resize(frame, (400, 200))
        bilateral_filt = cv2.bilateralFilter(frame, 5, 80, 80)
        hsv = cv2.cvtColor(bilateral_filt, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
        if (cv2.__version__ == "3.4.16"):
            _, contours, hierarchy = cv2.findContours(
                mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        else:
            contours, hierarchy = cv2.findContours(
                mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Used for debugging, show the contours found
        for i in range(len(contours)):
            cv2.drawContours(bilateral_filt, contours, i, (0, 255, 0),
                             2, cv2.LINE_8, hierarchy, 0)

        # Determine the leftmost and rightmost points
        left_most = None
        right_most = None
        for i in range(len(contours)):
            # Filter out small contours
            if cv2.contourArea(contours[i]) < 100:
                continue
            left = tuple(contours[i][contours[i][:, :, 0].argmin()][0])
            right = tuple(contours[i][contours[i][:, :, 0].argmax()][0])
            if not left_most:
                left_most = left
            if not right_most:
                right_most = right
            if left[0] < left_most[0]:
                left_most = left
            if right[0] > right_most[0]:
                right_most = right
        if not (right_most or left_most):
            return 0

        # Determine resistor wattage by pixel length
        resistor_length = right_most[0] - left_most[0]
        for length, wattage in WATTAGES.items():
            if resistor_length < length + 15 and resistor_length > length - 15:
                return wattage
        return 0

    def show_values(self, frame: List[int]) -> None:
        """
        Determines the wattage and value of detected resistors and displays them on screen
        :param List[int] frame the current frame from opencv video capture
        """

        # Assuming all resistors on screen are same value, use value of other
        # detected resistors if not able to calculate
        fallback_value = None

        # Find wattage of one resistor and assign it to all detected resistors
        wattage = self._get_wattage(frame)

        # Loop through detected resistors
        for i in range(len(self.resistors)):
            bands = self._find_bands(self.resistors[i]["ROI"])
            self.resistors[i]["wattage"] = wattage
            x, y, w, h = self.resistors[i]["resistor"]
            resistor_val = ""

            if (len(bands) in [3, 4, 5]):
                for band in bands[:-1]:
                    resistor_val += str(band[-1].multiplier)
                resistor_val = int(resistor_val)
                resistor_val *= 10**bands[-1][-1].multiplier
                self.resistors[i]["value"] = resistor_val
                fallback_value = resistor_val

                # Display resistor value
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    f'{resistor_val} OHMS, {wattage} W',
                    (x +
                     w +
                     10,
                     y),
                    cv2.FONT_HERSHEY_PLAIN,
                    1,
                    (0,
                     0,
                     0),
                    2,
                    cv2.LINE_AA)
                continue

            if len(bands) == 0:
                continue

            # Display value of other resistors if not able to calculate self
            if fallback_value:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    f'{resistor_val} OHMS, {wattage} W',
                    (x +
                     w +
                     10,
                     y),
                    cv2.FONT_HERSHEY_PLAIN,
                    1,
                    (0,
                     0,
                     0),
                    2,
                    cv2.LINE_AA)
            else:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # Show frame with detected calculations
        cv2.imshow("scanner", frame)
