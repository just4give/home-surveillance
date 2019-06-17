import cv2
from imutils.video.pivideostream import PiVideoStream
import imutils
import time
import numpy as np
import datetime
from tempimage import TempImage
import boto3
import json


class VideoCamera(object):
    def __init__(self, flip = False):
        self.vs = PiVideoStream().start()
        self.vs.camera.rotation=270
        self.flip = flip
        self.conf = json.load(open("conf.json"))
        self.vs.framerate=self.conf["fps"]
        self.vs.resolution=self.conf["resolution"]
        self.client = boto3.resource('s3')
        time.sleep(2.0)

    def __del__(self):
        self.vs.stop()

    def flip_if_needed(self, frame):
        if self.flip:
            return np.flip(frame, 0)
        return frame

    def get_frame(self):
        frame = self.flip_if_needed(self.vs.read())
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def get_object(self, classifier):
        timestamp = datetime.datetime.now()
        ts = timestamp.strftime("%A %d %B %Y %I:%M:%S.%f%p")
        found_objects = False
        frame = self.flip_if_needed(self.vs.read()).copy() 
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        objects = classifier.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=5,
            minSize=(60, 60),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        if len(objects) > 0:
            found_objects = True
            

        # Draw a rectangle around the objects
        for (x, y, w, h) in objects:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            #t = TempImage()
            #cv2.imwrite(t.path, frame[y:y+h,x:x+w])
            #self.client.meta.client.upload_file(t.path, self.conf["s3bucket_faces"], t.key )
            #t.cleanup()

        cv2.putText(frame,ts,(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,0.35, (0, 255, 0), 1)
        #cv2.imshow("feed",frame)
        #cv2.waitKey(1000)
        ret, jpeg = cv2.imencode('.jpg', frame)
        return (jpeg.tobytes(), found_objects, frame)

