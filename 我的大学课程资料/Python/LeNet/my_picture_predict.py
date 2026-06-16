import os
import sys
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import shutil
from pathlib import Path

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
        x = x.view(x.size(0), -1)  
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)

        return x

def ensure_dir(dir_path):
    # 确保目录存在
    Path(dir_path).mkdir(parents=True, exist_ok=True)

def load_model(model_path):
    if not os.path.exists(model_path):
        print(f"错误：模型文件 {model_path} 不存在")
        return None
        
    try:
        model = CNN()
        checkpoint = torch.load(model_path, map_location='cpu')
        if 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])
        else:
            model.load_state_dict(checkpoint)
        model.eval()
        print("模型已成功加载")
        return model
    except Exception as e:
        print(f"加载模型时出错: {e}")
        return None

def process_image(image_path):
    if not os.path.exists(image_path):
        print(f"错误：图片文件 {image_path} 不存在")
        return None
        
    try:
        transform = transforms.Compose([
            transforms.Grayscale(num_output_channels=1),
            transforms.Resize((28, 28)),
            transforms.ToTensor(),
        ])
        
        image = Image.open(image_path)
        image_tensor = transform(image)
        if image_tensor.max() > 1:
            image_tensor = image_tensor / 255.0
        if image_tensor.mean() > 0.5:
            image_tensor = 1 - image_tensor
        return image_tensor.unsqueeze(0)
    except Exception as e:
        print(f"处理图像时出错: {e}")
        return None

def extract_true_label(filename):
    try:
        parts = filename.split('_')
        if len(parts) >= 3:
            return int(parts[2].split('.')[0])
    except (IndexError, ValueError):
        pass
    return -1

def main():
    input_dir = "my_picture"
    output_dir = "my_out"
    model_dir = "my_model"

    if not os.path.exists(input_dir):
        print(f"错误：输入目录 {input_dir} 不存在")
        return

    ensure_dir(output_dir)
    print(f"输出目录 {output_dir} 已准备就绪")

    model_path = os.path.join(model_dir, "mnist_model.pth")
    model = load_model(model_path)
    if model is None:
        return

    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not image_files:
        print(f"警告：在 {input_dir} 中没有找到图片文件")
        return

    print(f"找到 {len(image_files)} 个图片文件待处理")
    correct_predictions = 0
    total_predictions = 0

    for idx, image_file in enumerate(image_files, 1):
        input_path = os.path.join(input_dir, image_file)
        print(f"\n正在处理第 {idx}/{len(image_files)} 张图片: {image_file}")

        image_tensor = process_image(input_path)
        if image_tensor is None:
            continue

        with torch.no_grad():
            try:
                outputs = model(image_tensor)
                _, predicted = torch.max(outputs, 1)
                prediction = predicted.item()

                true_label = extract_true_label(image_file)

                if true_label != -1:
                    output_filename = f"result_{idx:02d}_true{true_label}_pred{prediction}.png"
                    total_predictions += 1
                    if true_label == prediction:
                        correct_predictions += 1
                else:
                    output_filename = f"result_{idx:02d}_pred{prediction}.png"
                
                output_path = os.path.join(output_dir, output_filename)
                shutil.copy2(input_path, output_path)
                
                result_str = f"预测结果: {prediction}"
                if true_label != -1:
                    result_str += f", 真实标签: {true_label}"
                    result_str += f" {'[正确]' if true_label == prediction else '[错误]'}"
                print(result_str)
                
            except Exception as e:
                print(f"预测图像 {image_file} 时出错: {e}")

    if total_predictions > 0:
        accuracy = (correct_predictions / total_predictions) * 100
        print(f"\n预测完成！准确率: {accuracy:.2f}% ({correct_predictions}/{total_predictions})")

if __name__ == "__main__":
    main()
