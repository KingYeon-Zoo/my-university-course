import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
import torch.nn.functional as F
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

transform = transforms.Compose([transforms.ToTensor()])

train_dataset = torchvision.datasets.MNIST(
    root="./data", train=True, download=True, transform=transform
)
test_dataset = torchvision.datasets.MNIST(
    root="./data", train=False, download=True, transform=transform
)

trainloader = DataLoader(train_dataset, batch_size=5, shuffle=True)
testloader = DataLoader(test_dataset, batch_size=1, shuffle=True)

Loss = nn.CrossEntropyLoss()

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


net = CNN()
optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

train_losses = []
train_accuracies = []

for epoch in range(10):
    net.train() 
    total_loss = 0.0
    correct = 0
    total = 0
    for i, data in enumerate(trainloader):
        inputs, label = data
        pre = net(inputs)
        loss = Loss(pre, label)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

        _, predicted = torch.max(pre, 1)
        correct += (predicted == label).sum().item()
        total += label.size(0)

        if (i + 1) % 2000 == 0:
            avg_loss = total_loss / 2000
            train_losses.append(avg_loss)
            accuracy = 100 * correct / total
            train_accuracies.append(accuracy)
            print(f"[{epoch + 1}, {i + 1}] loss: {avg_loss:.3f} accuracy: {accuracy:.3f}%")
            total_loss = 0.0

plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.plot(train_losses, label='Loss')
plt.xlabel('Iterations')
plt.ylabel('Loss')
plt.title('Training Loss Curve')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(train_accuracies, label='Accuracy', color='g')
plt.xlabel('Iterations')
plt.ylabel('Accuracy (%)')
plt.title('Training Accuracy Curve')
plt.legend()

plt.show()

def save_model_cpu(model, folder='my_model', filename='mnist_model.pth'):
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    save_path = os.path.join(folder, filename)
    
    model = model.cpu()
    
    torch.save({
        'model_state_dict': model.state_dict(),
        'model_structure': str(model.__class__.__name__) 
    }, save_path)
    
    print(f"模型已保存到: {save_path}")

def load_model_cpu(model, folder='my_model', filename='mnist_model.pth'):
    load_path = os.path.join(folder, filename)
    
    if not os.path.exists(load_path):
        print(f"未找到模型文件: {load_path}")
        return False
    
    try:
        checkpoint = torch.load(load_path, map_location=torch.device('cpu'))
        
        if str(model.__class__.__name__) != checkpoint['model_structure']:
            print(f"警告：当前模型结构 ({model.__class__.__name__}) 与保存的模型结构 ({checkpoint['model_structure']}) 不匹配")
        
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()  
        
        print(f"模型已从 {load_path} 加载完成")
        return True
        
    except Exception as e:
        print(f"加载模型时出错: {str(e)}")
        return False

net.eval()
cnt = 0
for i, data in enumerate(testloader):
    inputs, label = data

    with torch.no_grad():  
        out = net(inputs)

    out = torch.argmax(out)
    if out == label:
        cnt += 1

    cv2.imwrite(f"out/%d_%d.jpg" % (i, out), np.array(inputs.cpu().squeeze()) * 255.)

print(f"模型准确度: {cnt / len(testloader) * 100:.3f}%")

save_model_cpu(net, folder='my_model', filename='mnist_model.pth')