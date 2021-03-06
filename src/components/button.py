import cv2

# https://stackoverflow.com/questions/60674501/how-to-make-black-background-in-cv2-puttext-with-python-opencv
# https://stackoverflow.com/questions/55919337/creating-capture-button-on-window


class Button:

    pos = (0, 0)
    pos_scan = (320, 0)
    font_thickness = 2
    text_color = (0, 255, 0)
    text_color_bg = (0, 0, 0)
    start_text = "Start"
    end_text = "End"
    scan_text = "Scan"
    font_size = 2
    background_size = max(start_text, end_text, key=len)
    font = cv2.FONT_HERSHEY_PLAIN

    @staticmethod
    def start(img, font=cv2.FONT_HERSHEY_PLAIN):

        x, y = Button.pos
        (text_w, text_h), _ = cv2.getTextSize(
            Button.start_text, font, Button.font_size, Button.font_thickness)
        cv2.rectangle(img, Button.pos, (x + text_w + 10, y +
                                        text_h + 10), Button.text_color_bg, -1)
        cv2.putText(
            img,
            Button.start_text,
            (x +
             5,
             y +
             text_h +
             Button.font_size -
             1 +
             5),
            font,
            Button.font_size,
            Button.text_color,
            Button.font_thickness)

    @staticmethod
    def end(img, font=cv2.FONT_HERSHEY_PLAIN):

        x, y = Button.pos
        (text_w, text_h), _ = cv2.getTextSize(
            Button.end_text, font, Button.font_size, Button.font_thickness)
        cv2.rectangle(img, Button.pos, (x + text_w + 10, y +
                                        text_h + 10), Button.text_color_bg, -1)

        cv2.putText(
            img,
            Button.end_text,
            (x +
             5,
             y +
             text_h +
             Button.font_size -
             1 +
             5),
            font,
            Button.font_size,
            Button.text_color,
            Button.font_thickness)

    @staticmethod
    def scan(img, font=cv2.FONT_HERSHEY_PLAIN):

        x, y = Button.pos_scan
        (text_w, text_h), _ = cv2.getTextSize(
            Button.scan_text, font, Button.font_size, Button.font_thickness)
        cv2.rectangle(img, Button.pos_scan, (x + text_w + 10,
                                             y + text_h + 10), Button.text_color_bg, -1)
        cv2.putText(
            img,
            Button.scan_text,
            (x +
             5,
             y +
             text_h +
             Button.font_size -
             1 +
             5),
            font,
            Button.font_size,
            Button.text_color,
            Button.font_thickness)
