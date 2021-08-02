from django.core.management.base import BaseCommand, CommandError
from automation.models import Action, Switch, Clock, Relay, LightSensor, PIRSensor, Media
from automation import gpio, logger
from raspberry.settings import AUTOMATION

import signal
import sys
import time
from threading import Thread
import redis
from picamera import PiCamera, PiCameraMMALError
import uuid
import cv2
from datetime import datetime
import subprocess
from os import listdir, remove
from os.path import isfile, join
import random

r = redis.Redis(host='127.0.0.1', port=6379, db=0)

class ActionsTimer(Thread):
    
    def __getAction(self, actionId):
        try:
            return Action.objects.get(id=actionId)
        except Action.DoesNotExist:
            return  None

    def run(self):
        keysList = "timed.actions"
        while True:
            logger.debug("Let's check what to turn off")
            
            timedActionsKeys = r.smembers(keysList)
            if len(timedActionsKeys) > 0:
                for ta in timedActionsKeys:
                    timedActionKey = str(ta, "UTF-8")
                    actionId = r.get(timedActionKey)
                    if actionId is None:
                        actionId = timedActionKey.split(".")[-1]
                        action = self.__getAction(actionId)
                        if action:
                            try:
                                action.execute(status=False)
                                
                                logger.debug("action {} expired".format(action))
                            except ValueError as e:
                                r.srem(keysList, timedActionKey)
                                logger.warning(e)
                        else:
                            r.delete(timedActionKey)
                            r.srem(keysList, timedActionKey)
                            logger.error("action {} doesn't exist".format(actionId))
                    else:
                        action = self.__getAction(str(actionId, "UTF-8"))
                        if action:
                            secondsRemaining = r.ttl(timedActionKey)
                            logger.debug("{} seconds left to turn off {}".format(secondsRemaining, action))
            else:
                logger.debug("No valid timed actions")
            time.sleep(2)

class ClockTimer(Thread):
    
    def __init__(self, clock):
        super(ClockTimer, self).__init__()
        self.clock = clock
        
    def run(self):
        while True:
            logger.debug("Clock {} tick".format(self.clock))
            
            self.clock.actuate()
            time.sleep(2)

class LightSensorMonitor(Thread):

    def __init__(self, sensor):
        super(LightSensorMonitor, self).__init__()
        self.sensor = sensor

    def run(self):
        while True:
            darkness = gpio.timeToHigh(self.sensor)
            self.sensor.setDarkness(darkness)
            time.sleep(1)

class PIRSensorMonitor(Thread):

    def __init__(self, sensor):
        super(PIRSensorMonitor, self).__init__()
        self.sensor = sensor

    def run(self):
        gpio.initSensor(self.sensor)
        previousState = False
        while True:
            movement = gpio.readSensorValue(self.sensor)
            if movement:
                if movement != previousState:  # avoid repeating the same signal
                    self.sensor.actuate()
                else:
                    logger.debug("Movement ignored")
            else:
                logger.debug("No movement")
            previousState = movement
            time.sleep(1)

def initRelays():
    for r in Relay.objects.filter(isNormallyClosed=True):
        gpio.toggle(True, r.pin)
    logger.info("Relays initiated")

def buttonPressed(button):
    button.actuate()

def initButtons():
    for button in Switch.objects.all():
        gpio.initButton(button, buttonPressed)
    logger.info("Buttons initiated")
        
def initClocks():
    for clock in Clock.objects.all():
        clockTimer = ClockTimer(clock)
        clockTimer.setDaemon(True)
        clockTimer.start()
    logger.info("Clocks initiated")

def initLightSensors():
    for lightSensor in LightSensor.objects.all():
        lightSensorMonitor = LightSensorMonitor(lightSensor)
        lightSensorMonitor.setDaemon(True)
        lightSensorMonitor.start()
    logger.info("Light sensors initiated")

def initPIRSensors():
    for pirSensor in PIRSensor.objects.all():
        pirSensorMonitor = PIRSensorMonitor(pirSensor)
        pirSensorMonitor.setDaemon(True)
        pirSensorMonitor.start()
    logger.info("PIR sensors initiated")

def startActionsTimer():
    actionsTimer = ActionsTimer()
    actionsTimer.setDaemon(True)
    actionsTimer.start()
    logger.info("Actions timer initiated")

class VideoAnalysis(Thread):
    thr = 0.8
    net = cv2.dnn.readNetFromCaffe("{}{}".format(AUTOMATION["modelsPath"], "MobileNetSSD_deploy.prototxt"), 
                                   "{}{}".format(AUTOMATION["modelsPath"], "MobileNetSSD_deploy.caffemodel"))
    classNames = {0: 'background',
                  1: 'aeroplane', 2: 'bicycle', 3: 'bird', 4: 'boat',
                  5: 'bottle', 6: 'bus', 7: 'car', 8: 'cat', 9: 'chair',
                  10: 'cow', 11: 'diningtable', 12: 'dog', 13: 'horse',
                  14: 'motorbike', 15: 'person', 16: 'pottedplant',
                  17: 'sheep', 18: 'sofa', 19: 'train', 20: 'tvmonitor'}

    def run(self):  
        while True:
            logger.info("Videos to analyze: {}".format(r.scard("videos")))
            
            videosToAnalyze = r.smembers("videos")
            for v in videosToAnalyze:
                vid = str(v, "UTF-8")
                media = None
                try:
                    media = Media.objects.get(id=vid)
                except Action.DoesNotExist:
                    logger.error("Video not found in database")
                r.srem("videos", vid)
                if media is not None:
                    logger.info("Analyzing {}".format(media.videoFile))                        
                    start = datetime.now()
                    
                    if self.__detectMovement(media):
                        logger.info("Video - movement detected")
                        #self.__classify(media)
                    else:
                        logger.info("Video - no movement detected")
                    
                    end = datetime.now()
                    logger.info("Video analysis duration {}s".format((end - start).total_seconds()))
            time.sleep(1)

    def __detectMovement(self, media):
        cap = cv2.VideoCapture("{}{}".format(AUTOMATION["mediaPath"], media.videoFile))
        framesCounter = 0
        framesAnalyzed = 0
        baselineImage = None
        statusList = [None,None]
        if cap.isOpened():
            # Read until video is completed or people is detected
            while not media.movementDetected:
                # Capture frame-by-frame
                ret, frame = cap.read()
                if ret == True:
                    status=0
                    framesCounter += 1
                    if framesCounter % 24 != 0:
                        continue
                    #time.sleep(1)
                    framesAnalyzed += 1
                    
                    #temp = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True)
                    #logger.info("[{}]{} frames{}".format(datetime.now(), str(temp.stdout, "UTF-8"), framesAnalyzed))
                    
                    #Gray conversion and noise reduction (smoothening)
                    gray_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                    gray_frame = cv2.GaussianBlur(gray_frame,(25,25),0)
    
                    if baselineImage is None:
                        baselineImage = gray_frame
                        continue
                    #Calculating the difference and image thresholding
                    delta = cv2.absdiff(baselineImage,gray_frame)
                    threshold = cv2.threshold(delta,35,255, cv2.THRESH_BINARY)[1]
                    # Finding all the contours
                    (contours,_) = cv2.findContours(threshold,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
                    for contour in contours:
                        if cv2.contourArea(contour) < 5000:
                            continue
                        status = 1
                    statusList.append(status)
                    
                    if statusList[-1] == 1 and statusList[-2] == 0:
                        media.movementDetected = True
                        media.save()
                        break
                else:
                    break
        # When everything done, release the video capture object
        cap.release()
        # Closes all the frames
        cv2.destroyAllWindows()
        
        return media.movementDetected

    def __classify(self, media):
        cap = cv2.VideoCapture("{}{}".format(AUTOMATION["mediaPath"], media.videoFile))
        framesCounter = 0
        framesAnalyzed = 0
        if cap.isOpened():
            # Read until video is completed or people is detected
            while media.classification is None:
                # Capture frame-by-frame
                ret, frame = cap.read()
                if ret == True:
                    framesCounter += 1
                    if framesCounter % 24 != 0:
                        continue
                    framesAnalyzed += 1
                    # Resizing the Image
                    cvImage = cv2.resize(frame, (360, 240))  # resize frame for prediction
                    # create blob
                    blob = cv2.dnn.blobFromImage(cvImage, 0.007843, (360, 240), (127.5, 127.5, 127.5), False)
                    # Set to network the input blob
                    VideoAnalysis.net.setInput(blob)
                    # Prediction of network
                    detections = VideoAnalysis.net.forward()
                    # Size of frame resize (300x300)
                    cols = cvImage.shape[1]
                    rows = cvImage.shape[0]
                    # For get the class and location of object detected,
                    # There is a fix index for class, location and confidence
                    # value in @detections array .
                    for i in range(detections.shape[2]):
                        confidence = detections[0, 0, i, 2]  # Confidence of prediction
                        if confidence > VideoAnalysis.thr:  # Filter prediction
                            classId = int(detections[0, 0, i, 1])  # Class label
                            if (VideoAnalysis.classNames[classId] == "person"
                                or VideoAnalysis.classNames[classId] == "dog" 
                                or VideoAnalysis.classNames[classId] == "horse"
                                or VideoAnalysis.classNames[classId] == "sheep"):
                                
                                logger.info("Confidence passed detected: {}:{} in {}".format(VideoAnalysis.classNames[classId], confidence, media.videoFile))

                                # Object location
                                xLeftBottom = int(detections[0, 0, i, 3] * cols)
                                yLeftBottom = int(detections[0, 0, i, 4] * rows)
                                xRightTop = int(detections[0, 0, i, 5] * cols)
                                yRightTop = int(detections[0, 0, i, 6] * rows)
    
                                # Factor for scale to original size of frame
                                heightFactor = frame.shape[0] / 240.0
                                widthFactor = frame.shape[1] / 360.0
                                # Scale object detection to frame
                                xLeftBottom = int(widthFactor * xLeftBottom)
                                yLeftBottom = int(heightFactor * yLeftBottom)
                                xRightTop = int(widthFactor * xRightTop)
                                yRightTop = int(heightFactor * yRightTop)
                                # Draw location of object
                                cv2.rectangle(frame, (xLeftBottom, yLeftBottom), (xRightTop, yRightTop), (255, 0, 0))
                                # save thumbnail
                                thumbnail = media.videoFile.replace("mp4", "jpg")
                                cv2.imwrite("{}{}".format(AUTOMATION["mediaPath"], thumbnail), frame)
                                # update media
                                media.thumbnail = thumbnail
                                media.classification = VideoAnalysis.classNames[classId]
                                media.save()
                                
                                break
                        #time.sleep(0.1)
                else:
                    break
        # When everything done, release the video capture object
        cap.release()
        # Closes all the frames
        cv2.destroyAllWindows()
        
        logger.info("Frames analyzed:{}. Classification:{}".format(framesAnalyzed, media.classification))

def startRecordingVideo():
    logger.info("Recording video initiated")
    with PiCamera() as camera:
        while True:
                try:
                    uniqueId = uuid.uuid1().hex
                    videoFile = "{}.h264".format(uniqueId)
                    # record video
                    camera.start_recording("{}{}".format(AUTOMATION["mediaPath"], videoFile))
                    camera.wait_recording(AUTOMATION["videoDuration"])
                    camera.stop_recording()
                    # convert to mp4 and delete h264 file
                    MP4file = videoFile.replace("h264", "mp4")
                    subprocess.run(["MP4Box", "-quiet", "-add", "{}{}".format(AUTOMATION["mediaPath"], videoFile), 
                                    "{}{}".format(AUTOMATION["mediaPath"], MP4file)], stdout=subprocess.DEVNULL)
                    remove("{}{}".format(AUTOMATION["mediaPath"], videoFile))
                    # save metadata
                    media = Media()
                    media.videoFile = MP4file
                    media.save()
                    # put media in analyzer queue
                    r.sadd("videos", media.id)
                except PiCameraMMALError as error:
                    logger.error(error)
                    break
                except:
                    logger.error("startRecordingVideo:Unexpected error:{}".format(sys.exc_info()[0]))
                    break
                time.sleep(1)

def startVideoAnalysis():
    videoAnalysis = VideoAnalysis()
    videoAnalysis.setDaemon(True)
    videoAnalysis.start()
    logger.info("Video analysis initiated")

class ElevatorMusic(Thread):

    def __init__(self):
        super(ElevatorMusic, self).__init__()
        self.musicFiles = [f for f in listdir(AUTOMATION["musicPath"]) if isfile(join(AUTOMATION["musicPath"], f))]

    def __continuePlaying(self):
        playMusic = r.get("play.music")
        if playMusic is None:
            return False
        else:
            return bool(playMusic)
        
    def run(self):        
        while True:
            if self.__continuePlaying():
                song = random.choice(self.musicFiles)
                if song is not None:
                    logger.info("playing{}".format(song))
                    subprocess.run(["omxplayer", "{}{}".format(AUTOMATION["musicPath"], song)], stdout=subprocess.DEVNULL)
            time.sleep(1)

def playElevatorMusic():
    elevatorMusic = ElevatorMusic()
    elevatorMusic.setDaemon(True)
    elevatorMusic.start()
    logger.info("Elevator music initiated")

def terminateProcess(signalNumber, frame):
    logger.info("(SIGTERM) terminating the process")
    gpio.cleanUp()
    sys.exit()

class Command(BaseCommand):
    help = "Start automation daemons"

    def add_arguments(self, parser):
        parser.add_argument(
            '--automation',
            action='store_true',
            help='Start automation services',
        )
        parser.add_argument(
            '--camera',
            action='store_true',
            help='Start recording services'
        )
        parser.add_argument(
            '--music',
            action='store_true',
            help='Start elevator music',
        )
                     
    def handle(self, *args, **options):
        signal.signal(signal.SIGTERM, terminateProcess)
        try:
            if options["music"]:
                playElevatorMusic()
            if options["automation"]:
                initRelays()
                initButtons()
                initClocks()
                initLightSensors()
                initPIRSensors()
                startActionsTimer()
            if options["camera"]:
                startVideoAnalysis()
                startRecordingVideo()  
        except KeyboardInterrupt:
            gpio.cleanUp()
            sys.exit()
