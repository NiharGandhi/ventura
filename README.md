# Face Recognition Attendance System

## Description

The Face Recognition Attendance System is a software application that utilizes face recognition technology to automate the process of marking attendance. It captures images of individuals, recognizes their faces, and records their attendance in a database. The software provides a user-friendly interface for managing various functions such as capturing photos, training the face recognition model, and viewing attendance records.

## Features

- Face detection and recognition using OpenCV and face_recognition library.
- User interface built with PyQt5 for easy interaction.
- Capture photos for dataset generation.
- Train the face recognition model using captured photos.
- Real-time video processing for face recognition.
- Mark attendance and store records in a local database.
- View attendance records by date, month, or person.
- Integration with Firebase for cloud-based storage and synchronization (optional).

## Requirements

- Python 3.6 or higher
- PyQt5
- OpenCV
- face_recognition
- Firebase Admin SDK (optional)

## Installation

1. Clone the repository:

git clone https://github.com/your-username/face-recognition-attendance-system.git


2. Install the required Python dependencies:

pip install -r requirements.txt


3. Set up Firebase (if using):

- Create a Firebase project and enable the Realtime Database.
- Download the service account key file (JSON) and place it in the project directory.

4. Run the application:

python mainwindow.py

## Usage

1. Launch the application by running `mainwindow.py`.
2. Use the buttons and dropdown menus in the user interface to perform various actions:
- Capture photos for dataset generation.
- Train the face recognition model.
- View the live video feed for face recognition.
- Mark attendance.
- View attendance records.
3. Customize the application as per your requirements by modifying the code.

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug fixes, please open an issue or submit a pull request.

## License

This software is licensed under the [MIT License](https://opensource.org/licenses/MIT).

