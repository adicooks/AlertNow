from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel
from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import cv2
import numpy as np
import requests

class Annotate(QThread):
    changePixmap = pyqtSignal(QImage)

    def __init__(self, image_url):
        super(Annotate, self).__init__()
        self.image_url = image_url
        self.frame = None
        self.original_frame = None  # Store original frame for redrawing
        self.scaled_frame = None

    def run(self):
        response = requests.get(self.image_url, stream=True)
        if response.status_code == 200:
            image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
            self.original_frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            self.frame = self.original_frame.copy()
        else:
            print("Failed to fetch image")
            return

        self.show_image()

    def show_image(self):
        if self.frame is not None:
            rgbImage = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgbImage.shape
            bytesPerLine = ch * w
            convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
            self.scaled_frame = convertToQtFormat.scaled(800, 500, Qt.KeepAspectRatio)  # Scale for display
            self.changePixmap.emit(self.scaled_frame)

    def draw_box(self, start, end, scale_x, scale_y):
        if self.frame is not None:
            # Scale back to original image size
            start = (int(start[0] * scale_x), int(start[1] * scale_y))
            end = (int(end[0] * scale_x), int(end[1] * scale_y))

            self.frame = self.original_frame.copy()  # Reset frame to avoid artifacts
            cv2.rectangle(self.frame, start, end, (255, 255, 255), thickness=3)  # White Box
            cv2.putText(self.frame, "Weapon 87.6%", (start[0], start[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)  # White Text
            self.show_image()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Manual Annotation")
        self.setGeometry(100, 100, 900, 600)

        self.label = QLabel(self)
        self.label.setGeometry(50, 50, 800, 500)
        self.label.setAlignment(Qt.AlignCenter)

        self.annotate = Annotate("https://fox17.com/resources/media/13f51f85-2b71-4d52-a659-067dd430472d-jumbo16x9_gun1111.png?1679972234732")
        self.annotate.changePixmap.connect(self.update_image)
        self.annotate.start()

        self.start_point = None
        self.end_point = None
        self.drawing = False

    def update_image(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.label.geometry().contains(event.pos()):
            self.start_point = event.pos() - self.label.pos()
            self.drawing = True

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.end_point = event.pos() - self.label.pos()
            self.drawing = False

            # Get original and displayed image sizes
            orig_h, orig_w, _ = self.annotate.original_frame.shape
            disp_w, disp_h = self.label.width(), self.label.height()

            # Calculate scaling factors
            scale_x = orig_w / disp_w
            scale_y = orig_h / disp_h

            self.annotate.draw_box((self.start_point.x(), self.start_point.y()),
                                   (self.end_point.x(), self.end_point.y()), scale_x, scale_y)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
