import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from typing import Tuple, Optional

class MLP(nn.Module):
    """多层感知机模型"""
    
    def __init__(self, input_size=784, hidden_size=128, 
                 num_classes=10):
        """
        初始化MLP模型
        
        参数:
            input_size: 输入特征大小 (默认: 784)
            hidden_size: 隐藏层大小 (默认: 128)
            num_classes: 输出类别数 (默认: 10)
        """
        super(MLP, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, num_classes)
        
    def forward(self, x):
        """前向传播"""
        x = x.view(-1, 28*28)  # 展平输入
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

def load_data(batch_size=64):
    """
    加载MNIST数据集
    
    参数:
        batch_size: 批量大小 (默认: 64)
        
    返回:
        train_loader: 训练数据加载器
        test_loader: 测试数据加载器
    """
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    train_dataset = datasets.MNIST(
        root='./data', 
        train=True,
        download=False,
        transform=transform
    )
    
    test_dataset = datasets.MNIST(
        root='./data',
        train=False,
        download=False,
        transform=transform
    )
    
    train_loader = DataLoader(
        dataset=train_dataset,
        batch_size=batch_size,
        shuffle=True
    )
    
    test_loader = DataLoader(
        dataset=test_dataset,
        batch_size=batch_size,
        shuffle=False
    )
    
    return train_loader, test_loader

def train(model, train_loader, optimizer, epoch):
    """训练模型"""
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        optimizer.zero_grad()
        output = model(data)
        loss = F.cross_entropy(output, target)
        loss.backward()
        optimizer.step()
        
        if batch_idx % 100 == 0:
            print(f'Train Epoch: {epoch} [{batch_idx * len(data)}/{len(train_loader.dataset)}'
                  f' ({100. * batch_idx / len(train_loader):.0f}%)]\tLoss: {loss.item():.6f}')

def test(model, test_loader):
    """测试模型"""
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            output = model(data)
            test_loss += F.cross_entropy(output, target, reduction='sum').item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)
    print(f'\nTest set: Average loss: {test_loss:.4f}, '
          f'Accuracy: {correct}/{len(test_loader.dataset)} '
          f'({100. * correct / len(test_loader.dataset):.0f}%)\n')

def main():
    """主函数"""
    # 超参数
    batch_size = 64
    learning_rate = 0.001
    epochs = 10
    
    # 加载数据
    train_loader, test_loader = load_data(batch_size)
    
    # 初始化模型
    model = MLP()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    # 训练和测试
    for epoch in range(1, epochs + 1):
        train(model, train_loader, optimizer, epoch)
        test(model, test_loader)

if __name__ == '__main__':
    main()
