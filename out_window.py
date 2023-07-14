import pickle
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, QTimer, QDate, Qt
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtTextToSpeech import QTextToSpeech, QVoice
import cv2
import face_recognition
import numpy as np
import datetime
import os
import csv
import pandas as pd
import time
import pyttsx3
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

class Ui_OutputDialog(QDialog):
    def __init__(self):
        super(Ui_OutputDialog, self).__init__()
        loadUi("user_interface/outputwindow.ui", self)

        #Initialize Firebase
        self.initialize_firebase()

        # Update time
        now = QDate.currentDate()
        current_date = now.toString('ddd dd MMMM yyyy')
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        self.Date_Label.setText(current_date)
        self.Time_Label.setText(current_time)
        self.image = None
        self.encode_list = []
        self.class_names = []
        self.attendance_records = {}
        self.engine = pyttsx3.init()

    def initialize_firebase(self):
        # Initialize Firebase
        cred = credentials.Certificate('ventura-5d1fe-firebase-adminsdk-q6x4i-2a488de72f.json')
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://ventura-5d1fe-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })

    @pyqtSlot()
    def startVideo(self, camera_name):
        print('Video Started')
        """
        :param camera_name: link of camera or usb camera
        :return:
        """
        if len(camera_name) == 1:
            self.capture = cv2.VideoCapture(int(camera_name), cv2.CAP_DSHOW)
        else:
            self.capture = cv2.VideoCapture(camera_name, cv2.CAP_DSHOW)
        self.timer = QTimer(self)  # Create Timer
        path = 'ImagesAttendance'
        if not os.path.exists(path):
            os.mkdir(path)
        # known face encoding and known face name list
        self.load_known_faces()
        self.timer.timeout.connect(self.update_frame)  # Connect timeout to the output function
        self.timer.start(10)  # emit the timeout() signal every 10ms

    def load_known_faces(self):
        print('Reading face encodings')
        f = open('face_enc', 'rb').read()
        data = pickle.loads(f)
        self.encode_list = data['encodings']
        self.class_names = data['names']

    def mark_attendance(self, name):
        print('Marking attendance:', name)
        Attendance_Folder = 'Attendance'
        current_date = datetime.datetime.now().strftime("%y_%m_%d")
        current_month = datetime.datetime.now().strftime("%Y_%m")
        attendance_path = os.path.join(Attendance_Folder, current_month)
        if not os.path.exists(attendance_path):
            os.makedirs(attendance_path)

        attendance_file_path = os.path.join(attendance_path, current_date + '.csv')
        fields = ['name', 'Date', 'Status']

        if os.path.exists(attendance_file_path):
            with open(attendance_file_path, 'r') as f:
                reader = csv.DictReader(f)
                previous_records = list(reader)
        else:
            previous_records = []

        with open(attendance_file_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()

            new_records = []
            for record in previous_records:
                if record['name'] == name:
                    if record['Status'] == 'Clock In':
                        # Skip marking "Clock Out" if same person seen again within a minute
                        last_clock_in_time = datetime.datetime.strptime(record['Date'], "%y/%m/%d %H:%M:%S")
                        current_time = datetime.datetime.now()
                        time_difference = current_time - last_clock_in_time
                        if time_difference.total_seconds() < 60:
                            new_records.append(record)
                        else:
                            # Mark as "Clock Out" if more than a minute has passed since last "Clock In"
                            record['Status'] = 'Clock Out'
                            status = 'Clock Out'
                            new_records.append(record)
                else:
                    new_records.append(record)

            # Add new record if it's a different person or no previous records exist
            if len(previous_records) == 0 or previous_records[-1]['name'] != name:
                status = 'Clock In'
                date_time_string = datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
                new_record = {'name': name, 'Date': date_time_string, 'Status': 'Clock In'}
                new_records.append(new_record)

            writer.writerows(new_records)

        self.update_attendance_records(current_date, name)

        ## Store in Firebase
        now = datetime.datetime.now()
        year = now.strftime('%Y')
        month = now.strftime('%B')
        day = now.strftime('%d')

        # Store in Firebase
        ref = db.reference(f'/attendance/{year}/{month}/{day}')
        attendance_data = {
        'name': name,
        'date': now.strftime("%y/%m/%d %H:%M:%S"),
        'status': status
        }
        ref.push(attendance_data)

        # Voice announcement
        if status == "Clock In":
            announcement = f"Welcome, {name}!"
        elif status == "Clock Out":
            announcement = f"Goodbye, {name}!"
        self.announce(announcement)

        # QMessageBox.information(self, "Confirmation", f"{name} {status}")


    def update_attendance_records(self, current_date, name):
        if name not in self.attendance_records:
            self.attendance_records[name] = [current_date]
        else:
            dates = self.attendance_records[name]
            if current_date not in dates:
                dates.append(current_date)

    def generate_monthly_report(self, month):
        attendance_path = os.path.join('Attendance', month)
        if not os.path.exists(attendance_path):
            return

        attendance_files = os.listdir(attendance_path)
        attendance_data = {}

        for file_name in attendance_files:
            file_path = os.path.join(attendance_path, file_name)
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row['name']
                    date = row['Date'].split()[0]
                    status = row['Status']

                    if name not in attendance_data:
                        attendance_data[name] = {}

                    if date not in attendance_data[name]:
                        attendance_data[name][date] = []

                    attendance_data[name][date].append(status)

        report_folder = os.path.join(attendance_path, 'Reports')
        if not os.path.exists(report_folder):
            os.makedirs(report_folder)

        for name, dates in attendance_data.items():
            report_file = os.path.join(report_folder, f'{name}_report.xlsx')
            df = pd.DataFrame(dates).T.fillna('Absent')
            df.columns = ['Status'] * len(df.columns)
            df.index.name = 'Date'

            with pd.ExcelWriter(report_file) as writer:
                df.to_excel(writer)

    def update_frame(self):
        ret, self.image = self.capture.read()
        self.displayImage(self.image, self.encode_list, self.class_names, 1)

    def face_rec_(self, frame, encode_list_known, class_names):
        print('Recognition Started')
        """
        :param frame: frame from camera
        :param encode_list_known: known face encoding
        :param class_names: known face names
        :return:
        """
        def draw_text(frame, text, x, y):
            cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

        # face recognition
        faces_cur_frame = face_recognition.face_locations(frame)
        encodes_cur_frame = face_recognition.face_encodings(frame, faces_cur_frame)

        for encodeFace, faceLoc in zip(encodes_cur_frame, faces_cur_frame):
            match = face_recognition.compare_faces(encode_list_known, encodeFace, tolerance=0.50)
            face_dis = face_recognition.face_distance(encode_list_known, encodeFace)
            name = "unknown"
            best_match_index = np.argmin(face_dis)

            if match[best_match_index]:
                name = class_names[best_match_index].upper()
                y1, x2, y2, x1 = faceLoc
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cropped_face = frame[y1:y2, x1:x2]
                cropped_face = cv2.resize(cropped_face, (96, 96), interpolation=cv2.INTER_AREA)

                if name != "Unknown":
                    img_path = os.path.join("ImagesAttendance", name)
                    if not os.path.exists(img_path):
                        os.makedirs(img_path)

                    cv2.imwrite(
                        os.path.join(img_path, f"{name}_{len(os.listdir(img_path))}.jpg"),
                        cropped_face,
                        [cv2.IMWRITE_JPEG_QUALITY, 95]
                    )

                cv2.rectangle(frame, (x1, y2 - 20), (x2, y2), (0, 255, 0), cv2.FILLED)
                draw_text(frame, name, x1 + 6, y2 - 6)
                time.sleep(2)
                self.mark_attendance(name)
            else:
                name = 'UNKNOWN'
                y1, x2, y2, x1 = faceLoc
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.rectangle(frame, (x1, y2 - 20), (x2, y2), (0, 0, 255), cv2.FILLED)
                draw_text(frame, name, x1 + 6, y2 - 6)
                if name == 'UNKNOWN':
                    print('CAPTURING PICTURE')
                    crop = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    unknown_person_time = datetime.datetime.now().strftime("%y_%m_%d %H_%M_%S")
                    cv2.imwrite(os.path.join('Unknown', f'Unknown_Person_{unknown_person_time}.jpg'), crop)

        return frame

    def showdialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText("This is a message box")
        msg.setInformativeText("This is additional information")
        msg.setWindowTitle("MessageBox demo")
        msg.setDetailedText("The details are as follows:")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    def update_frame(self):
        ret, self.image = self.capture.read()
        self.displayImage(self.image, self.encode_list, self.class_names, 1)

    def displayImage(self, image, encode_list, class_names, window=1):
        """
        :param image: frame from camera
        :param encode_list: known face encoding list
        :param class_names: known face names
        :param window: number of window
        :return:
        """
        image = cv2.resize(image, (640, 480))
        try:
            image = self.face_rec_(image, encode_list, class_names)
        except Exception as e:
            print(e)
        qformat = QImage.Format_Indexed8
        if len(image.shape) == 3:
            if image.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        outImage = QImage(image, image.shape[1], image.shape[0], image.strides[0], qformat)
        outImage = outImage.rgbSwapped()

        if window == 1:
            self.imgLabel.setPixmap(QPixmap.fromImage(outImage))
            self.imgLabel.setScaledContents(True)

    def announce(self, message):
        self.engine.say(message)
        self.engine.runAndWait()