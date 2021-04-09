import playsound
import cv2
import time
import imutils
from threading import Thread


# Initializing the face and eye cascade classifiers from xml files
face_cascade = cv2.CascadeClassifier('./haar_cascade/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('./haar_cascade/haarcascade_eye_tree_eyeglasses.xml')

wav_path = "./audio/alarm.wav"
detect_path = "./audio/detect.mp3"
not_detect_path = "./audio/not_detect.mp3"

def sound_alarm(path):
    playsound.playsound(path)

def playSound(path):
    t = Thread(target=sound_alarm, args=(path,), daemon=True)
    t.start()

# Variable store execution state
ALARM_ON = False
COUNTER = 0
NUM_FRAMES = 0
FRAMES_NOT_DETECT = 0.0
START = 0.0

EYE_AR_CONSEC_FRAMES = 3

# Starting the video capture
cap = cv2.VideoCapture(0)
ret, img = cap.read()
time.sleep(0.5)

while (ret):
    
    ret, img = cap.read()
    img = imutils.resize(img, width=480)
    # Coverting the recorded image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detecting the face for region of image to be fed to eye classifier
    faces = face_cascade.detectMultiScale(gray, 1.3, 5, minSize=(100, 100), flags=cv2.CASCADE_SCALE_IMAGE)
    # print(len(faces))
    maxBoundingBox = -1
    maxId = -1
    
    if (len(faces) > 0):
        if NUM_FRAMES == 2: # Bao hieu he thong da nhan duoc guong mat
            if detect_path != "":
                playSound(detect_path)
        
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
                
                if NUM_FRAMES % 5 == 0:  # He thong xu ly moi 5 frame
                    if (len(eyes) != None):
                        if(len(eyes) < 1):
                            COUNTER += 1
                            print(COUNTER)
                            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                                if not ALARM_ON:
                                    ALARM_ON = True

                                    if wav_path != "":
                                        playSound(wav_path)

                                cv2.putText(img, "Ban dang ngu gat!", (10, 30),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            else:
                                cv2.putText(img,"Count: %d" %COUNTER, (10, 30),
                                            cv2.FONT_HERSHEY_PLAIN, 2,(0, 0, 255), 2)
                            
                            if COUNTER != 0 and COUNTER % 5 == 0:
                                ALARM_ON = False
                        else:
                            COUNTER = 0
                            ALARM_ON = False
                           
        FRAMES_NOT_DETECT = 0
        NUM_FRAMES += 1
    else:
        if FRAMES_NOT_DETECT == 1.0: # Bao hieu he thong chua nhan duoc guong mat
            if not_detect_path != "":
                playSound(not_detect_path)
                
        COUNTER = 0
        NUM_FRAMES = 0
        FRAMES_NOT_DETECT += 0.5 # Cong 0.5 de tranh tinh trang overload khi cong so int
        ALARM_ON = False
        
        cv2.putText(img,
                    "No face detected", (10, 30),
                    cv2.FONT_HERSHEY_PLAIN, 2,
                    (255, 0, 0), 2)

    cv2.imshow('Screen', img)
    key = cv2.waitKey(1) & 0xFF
    if (key == ord('q')):
        break

cap.release()
cv2.destroyAllWindows() 