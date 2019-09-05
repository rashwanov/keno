import re
import os
import sys
import json
import requests
from PIL import Image
from termcolor import colored
from pytesseract import image_to_string


def crop(image_path, coords, saved_location):
    """
    @param image_path: The path to the image to edit
    @param coords: A tuple of x/y coordinates (x1, y1, x2, y2)
    @param saved_location: Path to save the cropped image
    """
    print ("%s was not scanned trying to crop....") %image_path
    image_obj = Image.open("images/"+image_path)
    cropped_image = image_obj.crop(coords)
    cropped_image.save("images/"+saved_location)
    # cropped_image.show()
    repeat = False
    imgtotext(saved_location, repeat)


def imgtotext(cImage, repeat):
    img = Image.open("images/"+cImage)
    text = image_to_string(img, lang="eng")
    extract(text, cImage, repeat)


def extract(text, cImage, repeat):
    try:

        tNumbers = re.findall(r"\s\d{2}\s\d{2}\s\d{2}\s\d{2}\s", text)
        tNumbers = map(int, (str(tNumbers[0])).split())
        did = map(int, re.findall(r"Draw ID:(\s\d+)", text))
        did = did[0] + 1
    except IndexError:
        if repeat:
            crop(cImage, (536, 2040, 1752, 2720), cImage.replace(".jpg", "-cropped.jpg"))
            return
        else:
            tNumbers = 0
            did = 0
    checkumbers(tNumbers, did, cImage)


def checkumbers(tNumbers, did, cImage):

    if len(str(tNumbers)) <= 0 or len(str(did)) < 5:
        print colored("%s: Was not successfully scanned try different scan!", "red") % cImage

    else:
        response = requests.get("https://www.palottery.state.pa.us/Keno/Keno.ashx?DrawID=%s&Draws=1" % did)
        data = response.json()
        winningNumbers = data["Draws"][0]["Numbers"]
        winningNumbers = list(map(int, winningNumbers.split(',')))
        matchNumbers = list((set(winningNumbers) & set(tNumbers)))


        if len(matchNumbers) == 2:
            print ("%s: Matched numbers are %s , Winner Prize: $1") % (cImage, matchNumbers)
        elif len(matchNumbers) == 3:
            print ("%s: Matched numbers are %s , Winner Prize: $3") % (cImage, matchNumbers)
        elif len(matchNumbers) == 4:
            print ("%s: Matched numbers are %s , Winner Prize: $100") % (cImage, matchNumbers)
        elif len(matchNumbers) == 0:
            print ("%s: Not a winner, your numbers: %s") % (cImage, tNumbers)

if __name__ == '__main__':
    # image = 'images/image.jpg'
    # crop(image, (536, 2040, 1752, 2720), 'cropped.jpg')
    allFiles = os.listdir(r"images")
    for imgName in allFiles:
        if "cropped.jpg" in allFiles:
            allFiles.remove("cropped.jpg")
        imgtotext(imgName, repeat=True)
        # print (imgName)
