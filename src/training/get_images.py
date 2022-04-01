import os
import cv2
import requests
import urllib.request
from random import randint
from time import sleep


def main():
    BASE_URL = "https://api.unsplash.com/search/photos?client_id=Du74MRfhhAdBXK0iNWkljwqdcmT41wd4YU-TIUyT8B8&per_page=30&query="
    term = "sky"
    request_url = BASE_URL + term
    response = requests.get(request_url)
    response_json = response.json()
    urls = [res["urls"]["small"] for res in response_json["results"]]

    path = 'src/training/neg/'
    if not os.path.exists(path):
        os.makedirs(path)

    pic_count = len([f for f in os.listdir(
        path)if os.path.isfile(os.path.join(path, f))]) + 1

    for i in range(1, int(response_json["total_pages"]) + 1):
        sleep(randint(5, 60))
        if i != 1:
            request_url = BASE_URL + term + "&page=" + str(i)
            response = requests.get(request_url)
            response_json = response.json()
            urls = [res["urls"]["small"] for res in response_json["results"]]
        for url in urls:
            if randint(1, 3) == 1:
                sleep(randint(1, 3))
            try:
                urllib.request.urlretrieve(url, path + str(pic_count) + ".png")
                img = cv2.imread(path+str(pic_count)+".png",
                                 cv2.IMREAD_GRAYSCALE)
                resized_image = cv2.resize(img, (640, 480))
                cv2.imwrite(path+str(pic_count)+".png", resized_image)
                print("Image Added " + str(pic_count))
                pic_count += 1
            except Exception as e:
                print(str(e))


if __name__ == "__main__":
    main()
