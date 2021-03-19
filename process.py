import playsound
import cv2
import time
import imutils
from threading import Thread

# Initializing the face and eye cascade classifiers from xml files
face_cascade = cv2.CascadeClassifier('./haar_cascade/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('./haar_cascade/haarcascade_eye_tree_eyeglasses.xml')

wav_path = "./alarm.wav"

def sound_alarm(wav_path):
    playsound.playsound(wav_path)

# Variable store execution state
ALARM_ON = False
COUNTER = 0
NUM_FRAMES = 0

EYE_AR_CONSEC_FRAMES = 5

# Starting the video capture
cap = cv2.VideoCapture(0)
ret, img = cap.read()
time.sleep(0.1)

while (ret):
    NUM_FRAMES += 1
    ret, img = cap.read()
    img = imutils.resize(img, width=600)
    # Coverting the recorded image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Applying filter to remove impurities
    gray = cv2.bilateralFilter(gray, 5, 1, 1)

    # Detecting the face for region of image to be fed to eye classifier
    faces = face_cascade.detectMultiScale(gray, 1.3, 5, minSize=(150, 150))
    # print(len(faces))
    maxBoundingBox = -1
    maxId = -1
    
    t = Thread(target=sound_alarm, args=(wav_path,), daemon = True)
    
    if (len(faces) > 0):
        for (i, rect) in enumerate(faces):
            (x, y, w, h) = rect
            region = (w + h)/2
            if region > maxBoundingBox:
                maxBoundingBox = region
                maxId = i

        for (i, rect) in enumerate(faces):
            if i == maxId:
                (x, y, w, h) = rect
                img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # roi_face is face which is input to eye classifier
                roi_face = gray[y:y + h, x:x + w]
                roi_face_clr = img[y:y + h, x:x + w]
                eyes = eye_cascade.detectMultiScale(roi_face, 1.3, 5, minSize=(20, 20))
                if NUM_FRAMES % 2 == 0:
                    if (len(eyes) != None):
                        if(len(eyes) < 1):
                            COUNTER += 1
                            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                                if not ALARM_ON:
                                    ALARM_ON = True

                                    if wav_path != "":
                                        t.start()

                                cv2.putText(img, "DROWSINESS ALERT!", (10, 30),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            else:
                                cv2.putText(img,"Count: %d" %COUNTER, (10, 30),
                                            cv2.FONT_HERSHEY_PLAIN, 2,(0, 0, 255), 2)
                        else:
                            COUNTER = 0
                            ALARM_ON = False
                           
    else:
        cv2.putText(img,
                    "No face detected", (100, 100),
                    cv2.FONT_HERSHEY_PLAIN, 3,
                    (0, 255, 0), 2)

    cv2.imshow('Screen', img)
    a = cv2.waitKey(1)
    if (a == ord('q')):
        break

cap.release()
cv2.destroyAllWindows() 