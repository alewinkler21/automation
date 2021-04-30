import signal
import sys
import time
from threading import Thread
import uuid
import cv2
from datetime import datetime
import subprocess
import os

videoPath = "/home/alejandro/Desktop/aaa/"
modelsPath = "/home/alejandro/Downloads/PythonDetector/"
thr = 0.8
net = cv2.dnn.readNetFromCaffe("{}{}".format(modelsPath, "MobileNetSSD_deploy.prototxt"), 
                               "{}{}".format(modelsPath, "MobileNetSSD_deploy.caffemodel"))
classNames = {0: 'background',
              1: 'aeroplane', 2: 'bicycle', 3: 'bird', 4: 'boat',
              5: 'bottle', 6: 'bus', 7: 'car', 8: 'cat', 9: 'chair',
              10: 'cow', 11: 'diningtable', 12: 'dog', 13: 'horse',
              14: 'motorbike', 15: 'person', 16: 'pottedplant',
              17: 'sheep', 18: 'sofa', 19: 'train', 20: 'tvmonitor'}

file1 = "63bf16d4a5c811eb9491b827ebdd52e2.h264"

def classify(fileName):
    global thr, net, classNames, videoPath
    cap = cv2.VideoCapture("{}{}".format(videoPath, fileName))
    if cap.isOpened():
        classification = None
        framesCounter = 0
        framesAnalyzed = 0
        # Read until video is completed or people is detected
        while classification is None:
            # Capture frame-by-frame
            ret, frame = cap.read()
            if ret == True:
                framesCounter += 1
                if framesCounter % 24 != 0:
                    continue
                framesAnalyzed += 1
                # Resizing the Image
                cvImage = cv2.resize(frame, (300, 300))  # resize frame for prediction
                # create blob
                blob = cv2.dnn.blobFromImage(cvImage, 0.007843, (300, 300), (127.5, 127.5, 127.5), False)
                # Set to network the input blob
                net.setInput(blob)
                # Prediction of network
                detections = net.forward()
                # For get the class and location of object detected,
                # There is a fix index for class, location and confidence
                # value in @detections array .
                print("detections range:{}".format(range(detections.shape[2])))
                for i in range(detections.shape[2]):
                    confidence = detections[0, 0, i, 2]  # Confidence of prediction
                    if confidence > thr:  # Filter prediction
                        classId = int(detections[0, 0, i, 1])  # Class label
                        if (classNames[classId] == "person"
                            or classNames[classId] == "dog" 
                            or classNames[classId] == "horse"
                            or classNames[classId] == "sheep"):
                            
                            print("Confidence passed detected: {}:{} in {}".format(classNames[classId], confidence, fileName))

                            fileNameH264 = fileName
                            fileNameMP4 = fileNameH264.replace("h264", "mp4")
                            # convert to mp4 and delete h264 file
                            #subprocess.run(["MP4Box", "-add", fileNameH264, fileNameMP4], stdout=subprocess.DEVNULL)
                            #os.remove("{}{}".format(AUTOMATION["mediaPath"], fileNameH264))
                            # update media
                            classification = classNames[classId]
                            
                            break
                    #time.sleep(0.1)
            else:
                break
    # When everything done, release the video capture object
    cap.release()
    # Closes all the frames
    cv2.destroyAllWindows()
    
    print("Frames analyzed:{}. Classification:{}".format(framesAnalyzed, classification))
    # delete useless file and data
    if classification is None:
        print("Delete {}".format(fileName))

def test():
    start = datetime.now()
    classify(file1)
    end = datetime.now()
    print("Duration:{}s".format((end - start).total_seconds()))
