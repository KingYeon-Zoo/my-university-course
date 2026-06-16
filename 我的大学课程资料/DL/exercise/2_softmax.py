import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
import matplotlib.pyplot as plt

class SoftmaxRegression(nn.Module):
    def __init__(self, input_dim, num_classes):
        super(SoftmaxRegression, self).__init__()
        self.linear = nn.Linear(input_dim, num_classes)
    
    def forward(self, x):
        x = x.view(-1, 784)  # 将28x28的图像展平为784维向量（线性层的输入是一维的）
        return self.linear(x)

def load_mnist_data():
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    train_dataset = datasets.MNIST(root='./data', train=True, transform=transform, download=True)
    test_dataset = datasets.MNIST(root='./data', train=False, transform=transform)
    
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=100, shuffle=True)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=100, shuffle=False)
    
    return train_loader, test_loader

def train_model(model, train_loader, test_loader, num_epochs=10, learning_rate=0.01):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=learning_rate)
    
    train_losses = []
    test_accuracies = []
    
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        for i, (images, labels) in enumerate(train_loader):
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            
        # 计算平均损失
        epoch_loss = running_loss / len(train_loader)
        train_losses.append(epoch_loss)
        
        # 在测试集上评估
        accuracy = evaluate(model, test_loader)
        test_accuracies.append(accuracy)
        
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {epoch_loss:.4f}, Test Accuracy: {accuracy:.2f}%')
    
    # 绘制训练过程图表
    plt.figure(figsize=(10, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(train_losses)
    plt.title('Training Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    
    plt.subplot(1, 2, 2)
    plt.plot(test_accuracies)
    plt.title('Test Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy (%)')
    
    plt.tight_layout() # 调整子图之间的间距
    plt.show()

def evaluate(model, test_loader):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in test_loader:
            outputs = model(images)
            _, predicted = torch.max(outputs, 1) 
            #用_忽略第一个返回值（最大值），只保留最大值的索引，用于和labels比较。
            total += labels.size(0)
            #labels.size(0)返回的是labels的行数，即batch_size
            correct += (predicted == labels).sum().item()
    return 100 * correct / total

if __name__ == "__main__":
    # 加载MNIST数据集
    train_dataset, test_dataset = load_mnist_data()

    # 初始化模型
    model = SoftmaxRegression(784, 10)  # MNIST有784个输入特征(28x28)和10个类别
    
    # 训练模型
    train_model(model, train_dataset, test_dataset)
    
    # 最终测试集评估
    final_accuracy = evaluate(model, test_dataset)
    print(f"\n最终测试集准确率: {final_accuracy:.4f}%")
