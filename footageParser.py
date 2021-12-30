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

def isWhite(pixel):
    for i in pixel:
        if i != 255:
            return False
    return True

#Main program start

#Handle arguments
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

#Check video resolution and adjust values
supportedResolutions = '1920x1080, 1680x1050, 1600x1024, 1600x900, 1440x900, 1366x768, 1360x768, 1280x800, 1280x768, 1280x800, 1280x768, 1280x720'
video = cv2.VideoCapture(args['videoPath'])
res = str(int(video.get(cv2.CAP_PROP_FRAME_WIDTH))) + 'x' + str(int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)))
print('Video resolution is ' + res)
if not (res in supportedResolutions):
    print('Video is not a supported resolution. Currently supported resolutions: ' + supportedResolutions)
    sys.exit(0)

if res == '1920x1080':
    mX = 621 #X pos of M from mission complete screen
    mY = 86 #Y pos of M from mission complete screen
    cP1 = 811 #Crop starting pos
    cP2 = 869 #crop ending pos
elif res == '1680x1050':
    mY = 83
    mX = 510
    cP1 = 788
    cP2 = 845
elif res == '1600x1024':
    mY = 80
    mX = 477
    cP1 = 769
    cP2 = 824
elif res == '1600x900':
    mY = 70
    mX =474
    cP1 = 676
    cP2 = 723
elif res == '1440x900':
    mY = 70
    mX = 435
    cP1 = 676
    cP2 = 723
elif res == '1366x768':
    mY = 61
    mX = 440
    cP1 = 577
    cP2 = 617
elif res == '1360x768':
    mY = 61
    mX = 437
    cP1 = 577
    cP2 = 617
elif res == '1280x800':
    mY = 6
    mX = 389
    cP1 = 601
    cP2 = 643
elif res == '1280x768':
    mY = 62
    mX =396
    cP1 = 577
    cP2 = 617
elif res == '1280x720':
    mY = 57
    mX = 413
    cP1 = 541
    cP2 = 579

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
        #Check for M on mission complete screen. 
        if isWhite(frame[mY,mX]):
            print('Found Mission complete screen at frame ' + str(video.get(cv2.CAP_PROP_POS_FRAMES)))
            crop = frame[cP1:cP2]
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