import numpy as np
import cv2


def getContours(img, imgContour):
    """ DRAWS AND FINDS CONTOURS, THEN RETURNS a list of lists incl x0, y0, w, h"""

    contour_list = []
    contours, hierarchy = cv2.findContours(
        img, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    # print('contours:', contours)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        areaMin = 200
        if area > areaMin and area < 5000:
            cv2.drawContours(imgContour, cnt, -1, (255, 0, 0), 7)
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            # print(len(approx))
            x, y, w, h = cv2.boundingRect(approx)
            print('contour bounding:', x, y, w, h)
            center_x = int(x + w/2)
            center_y = int(y + h/2)

            cv2.circle(imgContour, (center_x, center_y), 5, (0, 0, 255), 5)
            cv2.rectangle(imgContour, (x, y), (x + w, y + h), (0, 255, 0), 5)

            cv2.putText(imgContour, "Points: " + str(len(approx)), (x + w + 20, y + 20), cv2.FONT_HERSHEY_COMPLEX, .7,
                        (0, 255, 0), 2)
            cv2.putText(imgContour, "Area: " + str(int(area)), (x + w + 20, y + 45), cv2.FONT_HERSHEY_COMPLEX, 0.7,
                        (0, 255, 0), 2)

            if area < 3500:
                cv2.putText(imgContour, "THIS IS A SMALL PART", (x + w + 20, y + 70), cv2.FONT_HERSHEY_COMPLEX, 0.7,
                            (0, 255, 0), 2)

            contour_list.append([x, y, w, h])

    return contour_list


while True:
    img = cv2.imread('/home/raynard/Projects/ORSI2/src/test.jpg', 1)
    image_original = img.copy()

    lower_blue = np.array([160, 140, 15])  # [R value, G value, B value]
    upper_blue = np.array([255, 235, 60])

    image_copy = np.copy(img)
    image_copy = cv2.cvtColor(image_copy, cv2.COLOR_BGR2RGB)

    mask = cv2.inRange(image_copy, lower_blue, upper_blue)
    mask = cv2.bitwise_not(mask)
    img = cv2.cvtColor(mask, cv2.COLOR_BGR2RGB)

    # img = image
    imgContour = image_original.copy()

    print(getContours(mask, imgContour))
    # imgStack = stackImages(0.6, ([mask], [imgContour]))

    # cv2.imshow("Result", imgStack)
    cv2.imshow('Img_contour', imgContour)
    # cv2.setMouseCallback("Img_contour", mouse_callback)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
