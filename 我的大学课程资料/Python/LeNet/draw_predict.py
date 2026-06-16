import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(
            in_channels=1, out_channels=6, kernel_size=5, stride=1, padding=0
        )
        self.pooling = nn.MaxPool2d(kernel_size=2, stride=2, padding=0)
        self.conv2 = nn.Conv2d(
            in_channels=6, out_channels=16, kernel_size=5, stride=1, padding=0
        )
        self.conv3 = nn.Conv2d(
            in_channels=16, out_channels=120, kernel_size=5, stride=1, padding=0
        )
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

drawing = False
last_x, last_y = None, None
canvas = np.zeros((280, 280), dtype=np.uint8)

def draw(event, x, y, flags, param):
    global drawing, last_x, last_y, canvas
    
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        last_x, last_y = x, y
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            cv2.line(canvas, (last_x, last_y), (x, y), 255, 15)
            last_x, last_y = x, y
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False

cv2.namedWindow('Draw Digit')
cv2.setMouseCallback('Draw Digit', draw)

model = CNN()
checkpoint = torch.load('my_model/mnist_model.pth', map_location=torch.device('cpu'))
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

print("操作说明：")
print("- 用鼠标在画板上绘制数字")
print("- 按'p'键进行预测")
print("- 按'c'键清除画板")
print("- 按'q'键退出程序")

while True:
    cv2.imshow('Draw Digit', canvas)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('c'):
        canvas = np.zeros((280, 280), dtype=np.uint8)
    
    elif key == ord('p'):
        resized = cv2.resize(canvas, (28, 28))
        tensor_img = torch.FloatTensor(resized).unsqueeze(0).unsqueeze(0) / 255.0
        
        with torch.no_grad():
            output = model(tensor_img)
            prediction = torch.argmax(output).item()
            print(f"预测结果: {prediction}")
    
    elif key == ord('q'):
        break

cv2.destroyAllWindows() 