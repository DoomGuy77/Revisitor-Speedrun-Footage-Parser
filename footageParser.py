import cv2
import argparse
import pytesseract
import numpy
import re
import sys
    
def getBetterTime(time1, time2):
    if time1[0:1] == time2[0:1]:
        if time1[2:4] == time2[2:4]:
            if time1[5:7] < time2[5:7]:
                return 'time1'
        elif time1[2:4] < time2[2:4]:
            return 'time1'
    elif time1[0:1] < time2[0:1]:
        return 'time1'
    return 'time2'

def formatTime(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return '%d:%02d:%02d' % (hour, minutes, seconds)


#Main program start

#Handle arguments / Check if video is valid
ap = argparse.ArgumentParser()
ap.add_argument('-v', '--videoPath', required=True, help='Path to video file')
ap.add_argument('-t', '--tesseractPath', required=True, help='Path to tesseract.exe')
ap.add_argument('-c', '--checksPerSecond', required =False, help='How many times per second of video the program checks for speedrun timer. The higher this number is, the more accurate but slower the program. Default 4')
args = vars(ap.parse_args())
pytesseract.pytesseract.tesseract_cmd = args['tesseractPath']
if args['checksPerSecond'] is not None:
    checksPerSecond = args['checksPerSecond']
else:
    checksPerSecond = 4

video = cv2.VideoCapture(args['videoPath'])
if not (str(int(video.get(cv2.CAP_PROP_FRAME_WIDTH))) + 'x' + str(int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))) in ['1920x1080']):
    print("Video is not a supported resolution. Currently supported resolutions: 1920x1080")
    sys.exit(0)

#Check for speedrun timer x times every second
counter = 0
fps = video.get(cv2.CAP_PROP_FPS)
bestTime = '9:99.99'
while True:
    counter += 1
    grabbed, frame = video.read()
    if counter >= fps/checksPerSecond:
        if not grabbed:
            break
        if numpy.all(frame[86,621] == [255,255,251]):
            print('Found Mission complete screen at frame ' + str(video.get(cv2.CAP_PROP_POS_FRAMES)))
            crop = frame[811:869]
            grey = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(grey)
            #print(text)
            if re.search(r'\d:\d\d\.\d\d', text):
                runTime = re.search(r'\d:\d\d\.\d\d', text).group(0)
                if getBetterTime(runTime, bestTime) == 'time1':
                    bestTime = runTime
                    bestTimeTime = str(formatTime(int(video.get(cv2.CAP_PROP_POS_FRAMES)/fps)))
                    print('found new best time ' + bestTime + ' at ' + bestTimeTime)
                
        counter = 0
if bestTime == '9:99.99':
    print('No Speedrun timers found. Please ensure speedrun tools are enabled while playing')
else:
    print('Video parse complete. Best time found was ' + bestTime + ' at ' + bestTimeTime)