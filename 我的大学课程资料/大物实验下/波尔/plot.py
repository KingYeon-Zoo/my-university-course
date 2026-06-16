xita = [51,73,120,137,139,143,143,146]
xita_T1 = [1.532,1.550,1.568,1.572,1.575,1.579]
xita_T2 = [1.589,1.587,1.582,1.581,1.579,1.579,1.579,1.579]

fai = [-165,-163,-158,-151,-124,-114,-104,-103,-85,-77]
fai_T = [1.495,1.513,1.532,1.550,1.568,1.572,1.575,1.579,1.582,1.586]

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
import matplotlib as mpl
from scipy.interpolate import interp1d

# 设置中文字体显示
try:
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号
except:
    print("无法设置中文字体，使用系统默认字体")

# 计算角频率 ω = 2π/T
xita_omega1 = [2 * np.pi / T for T in xita_T1]
xita_omega2 = [2 * np.pi / T for T in xita_T2]
fai_omega = [2 * np.pi / T for T in fai_T]

# 创建图形，设置大小
plt.figure(figsize=(10, 8))

# 绘制 θ～ω 幅频特性曲线
plt.subplot(2, 1, 1)

# 对数据进行排序和去重
points1 = sorted(zip(xita_omega1, xita[:len(xita_T1)]), key=lambda x: x[0])
points2 = sorted(zip(xita_omega2, xita[:len(xita_T2)]), key=lambda x: x[0])

# 提取排序后的横纵坐标
xita_omega1_sorted, xita1_sorted = zip(*points1)
xita_omega2_sorted, xita2_sorted = zip(*points2)

# 去除重复的x值
def remove_duplicates(x, y):
    seen = {}
    unique_x = []
    unique_y = []
    for i, val in enumerate(x):
        if val not in seen:
            seen[val] = True
            unique_x.append(val)
            unique_y.append(y[i])
    return np.array(unique_x), np.array(unique_y)

xita_omega1_unique, xita1_unique = remove_duplicates(xita_omega1_sorted, xita1_sorted)
xita_omega2_unique, xita2_unique = remove_duplicates(xita_omega2_sorted, xita2_sorted)

# 使用插值生成平滑曲线 - 只使用线性插值
if len(xita_omega1_unique) >= 2:  # 需要至少2个点来创建线性插值
    x_smooth1 = np.linspace(min(xita_omega1_unique), max(xita_omega1_unique), 100)
    interp_func1 = interp1d(xita_omega1_unique, xita1_unique, kind='linear')
    y_smooth1 = interp_func1(x_smooth1)
    plt.plot(x_smooth1, y_smooth1, 'b-', label='θ～ω (数据集1)')
else:
    plt.plot(xita_omega1_unique, xita1_unique, 'b-', label='θ～ω (数据集1)')

if len(xita_omega2_unique) >= 2:
    x_smooth2 = np.linspace(min(xita_omega2_unique), max(xita_omega2_unique), 100)
    interp_func2 = interp1d(xita_omega2_unique, xita2_unique, kind='linear')
    y_smooth2 = interp_func2(x_smooth2)
    plt.plot(x_smooth2, y_smooth2, 'r-', label='θ～ω (数据集2)')
else:
    plt.plot(xita_omega2_unique, xita2_unique, 'r-', label='θ～ω (数据集2)')

plt.scatter(xita_omega1, xita[:len(xita_T1)], marker='o', color='blue')
plt.scatter(xita_omega2, xita[:len(xita_T2)], marker='x', color='red')

plt.xlabel('ω (rad/s)')
plt.ylabel('θ (度)')
plt.title('θ～ω 幅频特性曲线')
plt.grid(True)
plt.legend()

# 绘制 φ～ω 相频特性曲线
plt.subplot(2, 1, 2)

# 确保数据按照预期的顺序排列 - 这里假设应该是递减的
# 我们先按ω排序，但确保相应的φ值是按照预期的下降趋势
points3 = sorted(zip(fai_omega, fai), key=lambda x: x[0])
fai_omega_sorted, fai_sorted = zip(*points3)

# 去除重复的x值
fai_omega_unique, fai_unique = remove_duplicates(fai_omega_sorted, fai_sorted)

# 使用线性插值而不是三次插值，以避免非预期的曲线形状
if len(fai_omega_unique) >= 2:
    x_smooth3 = np.linspace(min(fai_omega_unique), max(fai_omega_unique), 100)
    interp_func3 = interp1d(fai_omega_unique, fai_unique, kind='linear')
    y_smooth3 = interp_func3(x_smooth3)
    plt.plot(x_smooth3, y_smooth3, 'g-', label='φ～ω')
else:
    plt.plot(fai_omega_unique, fai_unique, 'g-', label='φ～ω')

plt.scatter(fai_omega, fai, marker='o', color='green')

plt.xlabel('ω (rad/s)')
plt.ylabel('φ (度)')
plt.title('φ～ω 相频特性曲线')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.savefig('frequency_characteristics.png', dpi=300)
plt.show()
