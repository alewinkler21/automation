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

def classify(fileName, identifier, sleep=False):
    global thr, net, classNames, videoPath
    cap = cv2.VideoCapture("{}{}".format(videoPath, fileName))
    classification = None
    framesCounter = 0
    framesAnalyzed = 0
    if cap.isOpened():
        # Read until video is completed or people is detected
        while classification is None or True:
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
                net.setInput(blob)
                # Prediction of network
                detections = net.forward()
                # Size of frame resize (300x300)
                cols = cvImage.shape[1]
                rows = cvImage.shape[0]
                # For get the class and location of object detected,
                # There is a fix index for class, location and confidence
                # value in @detections array .
                #temp = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True)
                #print("[{}]{} frames{}".format(datetime.now(), str(temp.stdout, "UTF-8"), framesAnalyzed))
                for i in range(detections.shape[2]):
                    confidence = detections[0, 0, i, 2]  # Confidence of prediction
                    if confidence > thr:  # Filter prediction
                        classId = int(detections[0, 0, i, 1])  # Class label
                        if (classNames[classId] == "person"
                            or classNames[classId] == "dog" 
                            or classNames[classId] == "horse"
                            or classNames[classId] == "sheep"):

                            print("Confidence passed detected: {}:{} in {}".format(classNames[classId], confidence, fileName))

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
                            cv2.rectangle(frame, (xLeftBottom, yLeftBottom), (xRightTop, yRightTop),
                                  (0, 255, 0))

                            img_name = "{}frame{}.jpg".format(videoPath, identifier)
                            cv2.imwrite(img_name, frame)

                            fileNameH264 = fileName
                            fileNameMP4 = "{}.mp4".format(identifier)
                            # convert to mp4 and delete h264 file
                            subprocess.run(["MP4Box", "-add", "{}{}".format(videoPath, fileNameH264), 
                                            "{}{}".format(videoPath, fileNameMP4)], stdout=subprocess.DEVNULL)
                            #os.remove("{}{}".format(AUTOMATION["mediaPath"], fileNameH264))
                            # update media
                            classification = classNames[classId]
                            
                            break
                    if sleep:
                        time.sleep(0.1)
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

def detectMovement(fileName):
    global videoPath
    cap = cv2.VideoCapture("{}{}".format(videoPath, fileName))
    framesCounter = 0
    framesAnalyzed = 0
    baseline_image = None
    status_list=[None,None]
    if cap.isOpened():
        # Read until video is completed or movement is detected
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            status=0
            if ret == True:
                framesCounter += 1
                if framesCounter % 24 != 0:
                    continue
                framesAnalyzed += 1
                
                temp = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True)
                print("[{}]{} frames{}".format(datetime.now(), str(temp.stdout, "UTF-8"), framesAnalyzed))
                
                #Gray conversion and noise reduction (smoothening)
                gray_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                gray_frame=cv2.GaussianBlur(gray_frame,(25,25),0)

                if baseline_image is None:
                    baseline_image = gray_frame
                    continue
                #Calculating the difference and image thresholding
                delta=cv2.absdiff(baseline_image,gray_frame)
                threshold=cv2.threshold(delta,35,255, cv2.THRESH_BINARY)[1]
                # Finding all the contours
                (contours,_)=cv2.findContours(threshold,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for contour in contours:
                    if cv2.contourArea(contour) < 10000:
                        continue
                    status=1
                status_list.append(status)
                
                if status_list[-1] == 1 and status_list[-2] == 0:
                    print("Movement detected")
                    break
            else:
                break
    # When everything done, release the video capture object
    cap.release()
    # Closes all the frames
    cv2.destroyAllWindows()
    
    print("Frames analyzed:{}".format(framesAnalyzed))

def test(sleep=True):
    for i in range(10):
        print("Vuelta {}".format(i))
        start = datetime.now()
        #classify(file1, i, sleep)
        detectMovement(file1)
        end = datetime.now()
        print("Duration:{}s".format((end - start).total_seconds()))

if __name__ == '__main__':
    try:
        test()
    except KeyboardInterrupt:
        sys.exit()

