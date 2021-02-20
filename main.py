from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput

from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
import imutils
import playsound
import time
from threading import Thread
import dlib
import cv2

class MainApp(App):
    def build(self):
        layout = GridLayout(cols=2)
        inlayout = GridLayout(rows=2)
        self.thresh_label = Label(text='Threshold: ')
        inlayout.add_widget(self.thresh_label)
        self.thresh = TextInput(text='0.25')
        inlayout.add_widget(self.thresh)

        self.frame_label = Label(text='Frames: ')
        inlayout.add_widget(self.frame_label)
        self.frames = TextInput(text='40')
        inlayout.add_widget(self.frames)

        self.buttonCamera = Button(text='Open camera', on_press=self.onStream)
        layout.add_widget(inlayout)
        layout.add_widget(self.buttonCamera)
        return layout

    def onStream(self, obj):

        # Cau hinh duong dan
        wav_path = "./alarm.wav"

        # Ham phat ra am thanh
        def play_sound(wav_path):
            playsound.playsound(wav_path)

        # ham tinh toan ty le co cua mat
        def eye_aspect_ratio(eye):
            # tinh toan khoang cach euclid giua 2 tap hop
            # diem moc mat thang dung toa do (x,y)
            A = dist.euclidean(eye[1], eye[5])
            B = dist.euclidean(eye[2], eye[4])

            # tinh toan khoang cach euclid giua phuong ngang
            # moc mat toa do (x,y)
            C = dist.euclidean(eye[0], eye[3])

            # tien hanh tinh toan
            ear = (A + B) / (2.0 * C)

            return ear

        COUNTER = 0  # bien dem khi do gian no doi mat nho hon EYE_AR_THRESH
        ALARM_ON = False  # mac dinh alarm khong duoc kich hoat

        # khoi tao facial landmark detector
        print("[INFO] loading facial landmark predictor...")
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

        # lay chi so tren khuon mat cua mat trai va mat phai
        (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

        EYE_AR_THRESH = float(self.thresh.text)

        EYE_AR_CONSEC_FRAMES = int(self.frames.text)

        # Doc tu camera
        print("[INFO] starting video stream thread...")
        try:
            vs = VideoStream(src=0).start()
        except:
            vs = VideoStream(src=1).start()

        time.sleep(1.0)

        # cho vong lap de lay hinh anh
        while True:
            # lay khung hinh tu luong video truc tiep, thay doi kich thuoc va chuyen doi thanh mau xam
            frame = vs.read()
            frame = imutils.resize(frame, width=480)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # phat hien guong mat tren khung xam
            rects = detector(gray, 0)

            maxBoundingBox = -1
            maxId = -1
            for (i, rect) in enumerate(rects):
                shape = predictor(gray, rect)
                shape = face_utils.shape_to_np(shape)
                # convert dlib's rectangle to a OpenCV-style bounding box
                # [i.e., (x, y, w, h)], then draw the face bounding box
                (x, y, w, h) = face_utils.rect_to_bb(rect)
                total = (w + h) / 2
                if total > maxBoundingBox:
                    maxBoundingBox = total
                    maxId = i

            for (i, rect) in enumerate(rects):
                if i == maxId:
                    shape = predictor(gray, rect)
                    shape = face_utils.shape_to_np(shape)
                    # convert dlib's rectangle to a OpenCV-style bounding box
                    # [i.e., (x, y, w, h)], then draw the face bounding box
                    (x, y, w, h) = face_utils.rect_to_bb(rect)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    # trich xuat toa do cua mat trai va mat phai, tu do su dung cac toa do nay de tinh toan do gian no cua mat
                    leftEye = shape[lStart:lEnd]
                    rightEye = shape[rStart:rEnd]
                    leftEAR = eye_aspect_ratio(leftEye)
                    rightEAR = eye_aspect_ratio(rightEye)

                    # tinh trung binh do gian no cua doi mat
                    ear = (leftEAR + rightEAR) / 2.0

                    # tinh do loi lom cua mat trai va mat phai, sau do truc quan hoa tung mat
                    leftEyeHull = cv2.convexHull(leftEye)
                    rightEyeHull = cv2.convexHull(rightEye)
                    cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
                    cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

                    # neu do gian no mat duoi vung xac dinh  thi bien dem bat dau tang
                    if ear < EYE_AR_THRESH:
                        COUNTER += 1

                        # neu mat nham den so luong frame nhat dinh thi alarm duoc kich hoat
                        if COUNTER >= EYE_AR_CONSEC_FRAMES:
                            if not ALARM_ON:
                                ALARM_ON = True

                                if wav_path != "":
                                    t = Thread(target=play_sound,
                                               args=(wav_path,))
                                    t.daemon = True
                                    t.start()

                            # hien thi noi dung canh bao
                            cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                        if COUNTER % 90 == 0:
                            ALARM_ON = False

                    else:
                        COUNTER = 0
                        ALARM_ON = False

                    # hien thi do gian no cua mat theo tg thuc
                    cv2.putText(frame, "EAR: {:.2f}".format(
                        ear), (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # hien thi hinh anh
            cv2.imshow("Driver Drowsiness Detection Video Stream", frame)
            key = cv2.waitKey(1) & 0xFF

            # quit with q key
            if key == ord("q"):
                break

        # clean up after quit
        cv2.destroyAllWindows()
        vs.stop()


if __name__ == "__main__":
    MainApp().run()