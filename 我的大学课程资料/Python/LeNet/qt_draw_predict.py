import sys
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import cv2
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                           QVBoxLayout, QHBoxLayout, QLabel)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap

class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=6, kernel_size=5, stride=1, padding=0)
        self.pooling = nn.MaxPool2d(kernel_size=2, stride=2, padding=0)
        self.conv2 = nn.Conv2d(in_channels=6, out_channels=16, kernel_size=5, stride=1, padding=0)
        self.conv3 = nn.Conv2d(in_channels=16, out_channels=120, kernel_size=5, stride=1, padding=0)
        self.fc1 = nn.Linear(120, 84)
        self.fc2 = nn.Linear(84, 10)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = F.interpolate(x, size=(32, 32), mode="bilinear", align_corners=True)
        x = self.conv1(x)
        x = self.relu(x)
        x = self.pooling(x)
        x = self.conv2(x)
        x = self.relu(x)
        x = self.pooling(x)
        x = self.conv3(x)
        x = self.relu(x)
        x = x.squeeze()
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

class DrawingArea(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(500, 500)
        self.pixmap = QPixmap(500, 500)
        self.pixmap.fill(Qt.black)
        self.last_point = None
        self.drawing = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos()

    def mouseMoveEvent(self, event):
        if self.drawing:
            painter = QPainter(self.pixmap)
            painter.setPen(QPen(Qt.white, 25, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(self.last_point, event.pos())
            self.last_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def clear(self):
        self.pixmap.fill(Qt.black)
        self.update()

    def get_image(self):
        image = self.pixmap.toImage()
        width = image.width()
        height = image.height()
        ptr = image.bits()
        ptr.setsize(height * width * 4)
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
        gray = arr[:, :, 0]
        return gray

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("手写数字识别系统")
        self.setup_ui()
        self.load_model()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建绘图区域
        self.drawing_area = DrawingArea()
        layout.addWidget(self.drawing_area)

        # 创建按钮区域
        button_layout = QHBoxLayout()
        
        self.predict_button = QPushButton("预测", self)
        self.predict_button.setFixedSize(120, 40)
        self.predict_button.clicked.connect(self.predict)
        button_layout.addWidget(self.predict_button)

        self.clear_button = QPushButton("清除", self)
        self.clear_button.setFixedSize(120, 40)
        self.clear_button.clicked.connect(self.drawing_area.clear)
        button_layout.addWidget(self.clear_button)

        layout.addLayout(button_layout)

        # 创建结果显示标签
        self.result_label = QLabel("预测结果：", self)
        self.result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_label)

        self.setFixedSize(600, 700)

    def load_model(self):
        self.model = CNN()
        checkpoint = torch.load('my_model/mnist_model.pth', map_location=torch.device('cpu'))
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()

    def predict(self):
        # 获取绘图区域的图像并进行预处理
        image = self.drawing_area.get_image()
        resized = cv2.resize(image, (28, 28))
        tensor_img = torch.FloatTensor(resized).unsqueeze(0).unsqueeze(0) / 255.0

        with torch.no_grad():
            output = self.model(tensor_img)
            prediction = torch.argmax(output).item()
            self.result_label.setText(f"预测结果：{prediction}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 