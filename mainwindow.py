import sys
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QProgressBar, QLabel, QWidget, QComboBox, QLineEdit, QPushButton
from PyQt5.QtCore import pyqtSlot, QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
import resource1
import face_recognition
import pickle
import os
import cv2
from out_window import Ui_OutputDialog
from other_window import MyApp

class Ui_Dialog(QDialog):
    def __init__(self):
        super(Ui_Dialog, self).__init__()
        loadUi("user_interface/mainwindow.ui", self)
        self.CapturePhoto_Data.clicked.connect(self.CaptureFace)
        self.runButton.clicked.connect(self.runSlot)
        self.SearchButton.clicked.connect(self.SearchWindow)
        self.TrainButton.clicked.connect(self.TrainFaces)
        self._new_window = None
        self.Videocapture_ = None
    
    def check_and_create_folder(self):
        folders = ['Attendance', 'ImagesAttendance', 'Unknown']
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)
                QMessageBox.information(self, "Folders", "Missing Folders Successful")

    def refreshAll(self):
        """
        Set the text of lineEdit once it's valid
        """
        values = self.comboBox.currentText()
        values = str(values)
        if values == 'Select Camera Mode':
            values = '0'
        self.Videocapture_ = values


    @pyqtSlot()
    def runSlot(self):
        """
        Called when the user presses the Run button
        """
        print("Clicked Run")
        self.refreshAll()
        print(self.Videocapture_)
        ui.hide()  # hide the main window
        self.outputWindow_()  # Create and open new output window

    def outputWindow_(self):
        """
        Created new window for vidual output of the video in GUI
        """
        self._new_window = Ui_OutputDialog()
        self._new_window.show()
        self._new_window.startVideo(self.Videocapture_)
        print("Video Played")


    def SearchWindow(self):
        # ui.hide()
        self._new_window = MyApp()
        self._new_window.show()

    def TrainFaces(self):
        print('training')
        path = 'ImagesAttendance'
        if not os.path.exists(path):
            os.mkdir(path)
        # known face encoding and known face name list
        images = []
        self.class_names = []
        self.encode_list = []
        attendance_list = os.listdir(path)

        for name in attendance_list:
            if os.path.isdir(path+ '/' + name):
                for filename in os.listdir(path+ '/' + name):
                    try:
                        image = face_recognition.load_image_file(path+ '/' + name + '/' + filename)
                        encoding = face_recognition.face_encodings(image)[0]
                        self.encode_list.append(encoding)
                        self.class_names.append(os.path.basename(name))
                    except IndexError:
                        print('No Face Found in the image', filename)
        data = {'encodings': self.encode_list, "names": self.class_names}
        print('Uploading Datasets')
        f = open('face_enc', 'wb')
        f.write(pickle.dumps(data))
        f.close()
        # print('done encoding')
        QMessageBox.information(self, "Training", "Training Successful")
    
    def CaptureFace(self):
        self._new_window = FaceCaptureWindow()
        self._new_window.show()


class FaceCaptureWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.capture_count = 0
        self.capture_folder = None
        self.capture_timer = None

        self.initUI()
        self.initCamera()

    def initUI(self):
        self.setWindowTitle("Face Capture")
        screen = app.primaryScreen()
        screen_size = screen.size()
        window_width = screen_size.width() * 0.25
        window_height = screen_size.height() * 0.25
        self.setGeometry(0, 0, int(window_width), int(window_height))

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(10, 10, int(
            window_width - 20), int(window_height - 80))

        self.camera_combo = QComboBox(self)
        self.camera_combo.setGeometry(10, 10, 100, 30)
        self.camera_combo.addItem("Choose Camera")
        self.camera_combo.addItem("0")
        self.camera_combo.addItem("1")
        self.camera_combo.currentIndexChanged.connect(self.changeCamera)

        self.name_input = QLineEdit(self)
        self.name_input.setGeometry(
            10, int(window_height - 60), int(window_width - 20), 30)

        self.capture_button = QPushButton("Capture", self)
        self.capture_button.setGeometry(
            10, int(window_height - 30), int(window_width - 20), 30)
        self.capture_button.clicked.connect(self.captureImage)

    def initCamera(self):
        selected_camera = self.camera_combo.currentIndex() - 1
        self.camera = cv2.VideoCapture(selected_camera)

    def changeCamera(self, index):
        selected_camera = index - 1
        self.camera.release()
        self.camera = cv2.VideoCapture(selected_camera)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(30)

    def updateFrame(self):
        ret, frame = self.camera.read()

        if ret:
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channels = image.shape
            bytesPerLine = channels * width
            q_image = QImage(image.data, width, height,
                             bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.label.setPixmap(pixmap.scaled(
                self.label.width(), self.label.height(), Qt.KeepAspectRatio))

    def captureImage(self):
        if self.capture_count == 0:
            self.name = self.name_input.text()
            if not self.name:
                print("Please enter a name.")
                return

            self.capture_folder = os.path.join(
                os.getcwd() + '\ImagesAttendance', self.name)
            # self.capture_folder = os.path.join(r"C:\Users\nihar\Documents\Face Recognition 4.2.1 - Marking Update\ImagesAttendance", self.name)
            os.makedirs(self.capture_folder, exist_ok=True)

            self.capture_timer = QTimer(self)
            self.capture_timer.timeout.connect(self.captureNextImage)
            # 2 second interval between captures
            self.capture_timer.start(1000)

            # Disable capture button during capturing
            self.capture_button.setEnabled(False)

    def captureNextImage(self):
        ret, frame = self.camera.read()

        if ret:
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) > 0:
                (x, y, w, h) = faces[0]
                cropped_frame = frame[y:y+h, x:x+w]

                image_path = os.path.join(
                    self.capture_folder, f"{self.name}_{self.capture_count}.jpg")
                cv2.imwrite(image_path, cropped_frame)
                self.capture_count += 1
                print(self.capture_count)

            if self.capture_count >= 10:
                self.camera.release()
                self.timer.stop()
                self.capture_timer.stop()
                # Enable capture button after capturing
                self.capture_button.setEnabled(True)
                self.close()

    def closeEvent(self, event):
        self.camera.release()
        self.timer.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Ui_Dialog()
    ui.show()
    sys.exit(app.exec_())
