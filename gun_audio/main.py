import sys
import time
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QHBoxLayout)
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QColor

class DetectionThread(QThread):
    log_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)

    def __init__(self, log_file_path):
        super().__init__()
        self.running = False
        self.log_file_path = log_file_path
        self.process = None
    def run(self):
        self.running = True
        self.status_signal.emit("Running")
        self.log_signal.emit("Starting gunshot detection...")

        try:
            self.process = subprocess.Popen(
                ['python', 'gunshot.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            with open(self.log_file_path, 'r') as log_file:
                log_file.seek(0, os.SEEK_END)
                while self.running:
                    line = log_file.readline()
                    if line:
                        self.log_signal.emit(line.strip())
                    time.sleep(0.1)
        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}")
            self.status_signal.emit("Error")

    def stop(self):
        self.running = False
        if self.process:
            self.process.terminate()
            self.process = None
        self.log_signal.emit("Stopping gunshot detection...")
        self.status_signal.emit("Idle")


class GunshotDetectionUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.log_file_path = 'output.log'
        self.detection_thread = DetectionThread(self.log_file_path)

    def initUI(self):
        self.setWindowTitle("AlertNow - Gunshot Detection System")
        self.setGeometry(300, 200, 600, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                background-image: linear-gradient(145deg, #232526, #414345);
                color: white;
            }
        """)

        title_font = QFont("Arial", 24, QFont.Bold)
        status_font = QFont("Arial", 14, QFont.Bold)
        button_font = QFont("Arial", 12, QFont.Bold)
        log_font = QFont("Courier", 10)

        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        title_label = QLabel("AlertNow Gunshot Detection")
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            QLabel {
                color: #FFD700;
                padding: 10px;
            }
        """)
        layout.addWidget(title_label)

        self.status_label = QLabel("Status: Idle")
        self.status_label.setFont(status_font)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #FFD700;
                padding: 10px;
            }
        """)
        layout.addWidget(self.status_label)

        self.start_button = QPushButton("Start Detection")
        self.start_button.setFont(button_font)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 8px;
                border: 2px solid #ffffff;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.start_button.clicked.connect(self.start_detection)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Detection")
        self.stop_button.setFont(button_font)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px;
                border-radius: 8px;
                border: 2px solid #ffffff;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.stop_button.clicked.connect(self.stop_detection)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        layout.addLayout(button_layout)

        self.log_window = QTextEdit(self)
        self.log_window.setFont(log_font)
        self.log_window.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                color: #00FF00;
                padding: 10px;
                border: 2px solid #00FF00;
                border-radius: 5px;
            }
        """)
        self.log_window.setReadOnly(True)
        layout.addWidget(self.log_window)

        self.setLayout(layout)

    def start_detection(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.detection_thread.start()

        self.detection_thread.log_signal.connect(self.append_log)
        self.detection_thread.status_signal.connect(self.update_status)

    def stop_detection(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.detection_thread.stop()
        self.detection_thread.wait()

    @pyqtSlot(str)
    def append_log(self, message):
        if "gun_shot" in message:
            self.log_window.setTextColor(QColor("#FF0000"))
        else:
            self.log_window.setTextColor(QColor("#00FF00"))
        self.log_window.append(message)
        self.log_window.setTextColor(QColor("#00FF00"))

    @pyqtSlot(str)
    def update_status(self, status):
        if status == "Running":
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #00FF00;
                    padding: 10px;
                }
            """)
        elif status == "Idle":
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #FFD700;
                    padding: 10px;
                }
            """)
        elif status == "Error" or status == "Stopped":
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #FF0000;
                    padding: 10px;
                }
            """)
        self.status_label.setText(f"Status: {status}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = GunshotDetectionUI()
    ui.show()
    sys.exit(app.exec_())
