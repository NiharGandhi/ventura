import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QComboBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, QTimer, Qt
from Table import Viewer
import cv2


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        loadUi('user_interface/Searchui.ui', self)
        self.UnknownFaces.clicked.connect(self.OpenUnkownFolder)
        self.Today_Attendance.clicked.connect(self.Today_Attendance_Open)
        self.View_Attendance_Folder.clicked.connect(self.Attendance_Folder)
        self.DatabaseButton.clicked.connect(self.DatabaseFolder)
        # self.CapturePhoto_Data.clicked.connect(self.CaptureFace)

    @pyqtSlot()
    def OpenUnkownFolder(self):
        os.startfile('Unknown')

    def Today_Attendance_Open(self):
        # Attendace_File_Date = datetime.datetime.now().strftime("%y_%m_%d")
        # Todays_path = './Attendance/' + Attendace_File_Date + '.csv'
        # print(Todays_path)
        # os.startfile(Todays_path)
        self._new_window = Viewer()
        self._new_window.show()

    def Attendance_Folder(self):
        os.startfile('Attendance')

    def DatabaseFolder(self):
        os.startfile('ImagesAttendance')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myApp = MyApp()
    myApp.show()
    sys.exit(app.exec_())
