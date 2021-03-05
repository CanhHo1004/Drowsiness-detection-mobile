from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput

import playsound
from threading import Thread
import cv2

class MainApp(App):
    def build(self):
        layout = GridLayout(cols=2)
        inlayout = GridLayout(rows=2)

        self.frame_label = Label(text='Frames: ')
        inlayout.add_widget(self.frame_label)
        self.frames = TextInput(text='40')
        inlayout.add_widget(self.frames)

        self.buttonCamera = Button(text='Open camera', on_press=self.onStream)
        layout.add_widget(inlayout)
        layout.add_widget(self.buttonCamera)
        return layout

    def onStream(self, obj):

        face_cascade = cv2.CascadeClassifier('./haar_cascade/haarcascade_frontalface_default.xml')
        eye_cascade = cv2.CascadeClassifier('./haar_cascade/haarcascade_eye_tree_eyeglasses.xml')

        wav_path = "./alarm.wav"

        def sound_alarm(wav_path):
            playsound.playsound(wav_path)

        # Variable store execution state
        ALARM_ON = False
        COUNTER = 0

        EYE_AR_CONSEC_FRAMES = int(self.frames.text)

        # Starting the video capture
        cap = cv2.VideoCapture(0)
        ret, img = cap.read()

        while (ret):
            ret, img = cap.read()
            # Coverting the recorded image to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Applying filter to remove impurities
            gray = cv2.bilateralFilter(gray, 5, 1, 1)

            # Detecting the face for region of image to be fed to eye classifier
            faces = face_cascade.detectMultiScale(gray, 1.3, 5, minSize=(150, 150))
            if (len(faces) > 0):
                for (x, y, w, h) in faces:
                    img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    # roi_face is face which is input to eye classifier
                    roi_face = gray[y:y + h, x:x + w]
                    roi_face_clr = img[y:y + h, x:x + w]
                    eyes = eye_cascade.detectMultiScale(roi_face, 1.3, 5, minSize=(40, 40))
                    # Examining the length of eyes object for eyes
                    if (len(eyes) != None):
                        cv2.putText(img, "Eyes detected", (50, 70), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
                        if (len(eyes) < 1):
                            COUNTER += 1
                            cv2.putText(img, "Count: " + str(COUNTER), (450, 70), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
                            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                                if not ALARM_ON:
                                    ALARM_ON = True

                                    if wav_path != "":
                                        t = Thread(target=sound_alarm,
                                                   args=(wav_path,))
                                        t.daemon = True
                                        t.start()

                                cv2.putText(img, "DROWSINESS ALERT!", (10, 30),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        else:
                            COUNTER = 0
                            ALARM_ON = False
            else:
                cv2.putText(img,
                            "No face detected", (100, 100),
                            cv2.FONT_HERSHEY_PLAIN, 3,
                            (0, 255, 0), 2)

                # Controlling the algorithm with keys
            cv2.imshow('img', img)
            a = cv2.waitKey(1)
            if (a == ord('q')):
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    MainApp().run()