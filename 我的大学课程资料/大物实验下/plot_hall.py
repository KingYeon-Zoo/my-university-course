import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline, make_interp_spline

# --- Matplotlib 中文显示设置 ---
plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体为 SimHei
plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
# --- ------------------------ ---

f_tong_xuangua = [710.622,702.390,698.133,697.560,699.274]
f_tong_zhicheng = [714.227,704.082,698.527,698.328,701.385]
f_gang_zhicheng = [1041.094,1038.198,1036.735,1036.246,1036.987]

# 注意：假设使用 L 的前 5 个值与频率数据对应
L = np.array([5.84, 15.84, 25.84, 45.84, 55.84]) # 修正 L 长度并转为 numpy 数组

# 处理和绘制数据
datasets = {
    "铜悬挂法": np.array(f_tong_xuangua),
    "铜支撑法": np.array(f_tong_zhicheng),
    "钢悬挂法": np.array(f_gang_zhicheng)
}

# 使用四次多项式拟合（效果最好）
min_points = {}

plt.figure(figsize=(15, 10)) # 创建一个更大的图形窗口

plot_index = 1
for name, f_data in datasets.items():
    plt.subplot(2, 2, plot_index) # 创建子图
    
    # 绘制原始数据点
    plt.scatter(L, f_data, label='原始数据', color='blue', s=80)
    
    # 创建更密集的点用于绘制平滑曲线
    L_fit = np.linspace(L.min(), L.max(), 1000)
    
    # --- 四次多项式拟合 ---
    coeffs_4 = np.polyfit(L, f_data, 4)
    poly_func_4 = np.poly1d(coeffs_4)
    f_fit_4 = poly_func_4(L_fit)
    
    # 找出四次多项式在区间内的最小值点
    min_idx_4 = np.argmin(f_fit_4)
    L_min = L_fit[min_idx_4]
    f_min = f_fit_4[min_idx_4]
    
    # 显示多项式表达式
    poly_expr = f"y = {coeffs_4[0]:.2e}x⁴"
    for i, coef in enumerate(coeffs_4[1:], 1):
        power = 4 - i
        if power > 0:
            poly_expr += f" {'+' if coef >= 0 else '-'} {abs(coef):.2e}x{'^'+str(power) if power > 1 else ''}"
        else:
            poly_expr += f" {'+' if coef >= 0 else '-'} {abs(coef):.2e}"
    
    plt.plot(L_fit, f_fit_4, '-', label=f'四次多项式拟合', color='red', linewidth=2)
    
    # 记录和标记最低点
    min_points[name] = (L_min, f_min)
    plt.scatter(L_min, f_min, color='orange', s=150, zorder=5, 
                label=f'最低点 ({L_min:.2f}, {f_min:.2f})', edgecolor='black')
    
    plt.xlabel("L (mm)", fontsize=12)
    plt.ylabel("f (Hz)", fontsize=12)
    plt.title(f"{name} ", fontsize=14)
    plt.text(0.05, 0.05, poly_expr, transform=plt.gca().transAxes, fontsize=9,
             bbox=dict(facecolor='white', alpha=0.7))
    plt.legend(fontsize=10)
    plt.grid(True)
    plot_index += 1

# 添加一个总结图表，显示所有数据集的最低点
plt.subplot(2, 2, 4)
colors = ['blue', 'red', 'green']
for i, (name, point) in enumerate(min_points.items()):
    plt.bar(i, point[1], color=colors[i], alpha=0.6, label=f"{name}\nL={point[0]:.2f}, f={point[1]:.2f}")

plt.xticks([])
plt.ylabel("最低频率 (Hz)", fontsize=12)
plt.title("各组数据最低点比较", fontsize=14)
plt.legend(fontsize=9)
plt.grid(True, axis='y')

plt.tight_layout() # 调整子图布局
plt.savefig('hall_effect_fitting.png', dpi=300)  # 保存高质量图像
plt.show() # 显示所有图像

print("\n使用四次多项式拟合得到的最低点总结:")
for name, point in min_points.items():
    print(f"- {name}: L={point[0]:.4f}, f={point[1]:.4f}")
