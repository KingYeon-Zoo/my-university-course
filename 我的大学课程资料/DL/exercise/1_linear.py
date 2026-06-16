import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt

# 定义训练相关的超参数（全局常量）
NUM_EPOCHS = 200  # 训练轮数
LEARNING_RATE = 0.01  # 学习率
NUM_SAMPLES = 100  # 样本数量
TRUE_WEIGHT = 2.5  # 真实权重
TRUE_BIAS = 1.5  # 真实偏置


def set_seed(seed=42):
    """设置随机种子以确保实验可重现

    参数:
        seed: 随机种子值，默认为42
    """
    torch.manual_seed(seed)
    np.random.seed(seed)


def generate_data():
    """生成线性回归训练数据

    返回:
        X: 输入特征张量
        Y: 目标值张量
        true_w: 真实权重
        true_b: 真实偏置
    """
    try:
        x = torch.linspace(-10, 10, NUM_SAMPLES)
        y = TRUE_WEIGHT * x + TRUE_BIAS + torch.randn(NUM_SAMPLES)

        X = x.reshape(-1, 1)
        Y = y.reshape(-1, 1)
        return X, Y, TRUE_WEIGHT, TRUE_BIAS
    except Exception as e:
        print(f"生成数据时发生错误: {str(e)}")
        raise


class LinearRegression(nn.Module):
    """线性回归模型类"""

    def __init__(self):
        """初始化模型参数"""
        super(LinearRegression, self).__init__()
        self.linear = nn.Linear(1, 1)  # 输入维度=1，输出维度=1

    def forward(self, x):
        """前向传播函数"""
        return self.linear(x)

    def get_weight(self):
        """获取模型权重"""
        return self.linear.weight.item()

    def get_bias(self):
        """获取模型偏置"""
        return self.linear.bias.item()


def train_model(model, X, Y):
    """训练线性回归模型

    参数:
        model: 线性回归模型实例
        X: 输入特征
        Y: 目标值

    返回:
        losses: 训练损失历史
        weights: 权重历史
        biases: 偏置历史
    """
    criterion = nn.MSELoss()  # 使用均方误差损失
    optimizer = torch.optim.SGD(model.parameters(), lr=LEARNING_RATE)

    losses = []  # 记录损失
    weights = []  # 记录权重
    biases = []  # 记录偏置

    try:
        for epoch in range(NUM_EPOCHS):
            # 前向传播
            outputs = model(X)
            loss = criterion(outputs, Y)

            # 反向传播和优化
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            # 记录训练过程
            losses.append(loss.item())
            weights.append(model.get_weight())
            biases.append(model.get_bias())

            # 打印训练进度
            if (epoch + 1) % 20 == 0:
                print(f"训练轮次 [{epoch+1}/{NUM_EPOCHS}], 损失: {loss.item():.4f}")
                print(
                    f"当前权重 = {model.get_weight():.4f}, 偏置 = {model.get_bias():.4f}"
                )

        return losses, weights, biases
    except Exception as e:
        print(f"训练过程中发生错误: {str(e)}")
        raise


def plot_training_progress(losses, weights, biases, true_w, true_b):
    """可视化训练进度

    参数:
        losses: 训练损失历史
        weights: 权重历史
        biases: 偏置历史
        true_w: 真实权重
        true_b: 真实偏置
    """
    plt.figure(figsize=(15, 5))

    # 绘制损失曲线
    plt.subplot(131)
    plt.plot(losses)
    plt.title("损失曲线")
    plt.xlabel("训练轮次")
    plt.ylabel("损失值")

    # 绘制权重变化曲线
    plt.subplot(132)
    plt.plot(weights)
    plt.axhline(y=true_w, color="r", linestyle="--", label=f"真实权重={true_w}")
    plt.title("权重变化曲线")
    plt.xlabel("训练轮次")
    plt.ylabel("权重值")
    plt.legend()

    # 绘制偏置变化曲线
    plt.subplot(133)
    plt.plot(biases)
    plt.axhline(y=true_b, color="r", linestyle="--", label=f"真实偏置={true_b}")
    plt.title("偏置变化曲线")
    plt.xlabel("训练轮次")
    plt.ylabel("偏置值")
    plt.legend()

    plt.tight_layout()
    plt.show()


def plot_regression_result(X, Y, model):
    """可视化回归结果

    参数:
        X: 输入特征
        Y: 目标值
        model: 训练好的模型
    """
    plt.figure(figsize=(10, 6))
    plt.scatter(X.numpy(), Y.numpy(), label="原始数据")
    plt.plot(X.numpy(), model(X).detach().numpy(), "r-", label="拟合直线")
    plt.title("线性回归结果")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend()
    plt.show()


def main():
    """主函数：执行完整的线性回归训练流程"""
    try:
        # 设置随机种子
        set_seed()

        # 生成数据
        X, Y, true_w, true_b = generate_data()

        # 创建和训练模型
        model = LinearRegression()
        losses, weights, biases = train_model(model, X, Y)

        # 可视化训练过程
        plot_training_progress(losses, weights, biases, true_w, true_b)

        # 可视化回归结果
        plot_regression_result(X, Y, model)

        # 打印最终结果
        print("\n最终模型参数:")
        print(f"权重 w = {model.get_weight():.4f} (真实值: {true_w})")
        print(f"偏置 b = {model.get_bias():.4f} (真实值: {true_b})")

    except Exception as e:
        print(f"程序执行出错: {str(e)}")


if __name__ == "__main__":
    main()
