import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']  
plt.rcParams['axes.unicode_minus'] = False 

def zhui_gan_fa(a, b, c, d):
    n = len(d) 
    x = np.zeros(n) 
    
    #LU分解
    for i in range(1, n):
        m = a[i] / b[i-1]
        b[i] = b[i] - m * c[i-1]
        d[i] = d[i] - m * d[i-1]
    
    # 回代求解x
    x[n-1] = d[n-1] / b[n-1]
    for i in range(n-2, -1, -1):
        x[i] = (d[i] - c[i] * x[i+1]) / b[i]
    
    return x

def cha_zhi(x, y, x_new):
    n = len(x) - 1
    
    #计算h =  x[i+1] - x[i]
    h = np.diff(x)
    #
    
    #三弯矩方程组来求三次样条插值
    # 构造三对角矩阵系数
    a = np.zeros(n-1) 
    b = np.zeros(n-1) 
    c = np.zeros(n-1)  
    d = np.zeros(n-1)  
    # 填充三对角矩阵
    for i in range(n-1):
        if i > 0: # a[0]没有用到，从1开始
            a[i] = h[i]
        b[i] = 2 * (h[i] + h[i+1])
        if i < n-2:# c[n-2]没有用到，到n-3结束
            c[i] = h[i+1]
        d[i] = 6 * ((y[i+2] - y[i+1]) / h[i+1] - (y[i+1] - y[i]) / h[i])
    
    # 使用自然边界条件（二阶导数在端点为0）
    m = np.zeros(n+1)
    if n > 1:
        m[1:-1] = zhui_gan_fa(a, b, c, d)
    
    # 计算插值结果
    y_new = np.zeros_like(x_new)
    
    for i, xi in enumerate(x_new):
        # 找到xi所在的区间
        for j in range(n):
            if x[j] <= xi <= x[j+1]:
                # 计算插值
                t = (xi - x[j]) / h[j]
                a_j = y[j]
                b_j = (y[j+1] - y[j]) / h[j] - h[j] * (2 * m[j] + m[j+1]) / 6
                c_j = m[j] / 2
                d_j = (m[j+1] - m[j]) / (6 * h[j])
                
                y_new[i] = a_j + b_j * (xi - x[j]) + c_j * (xi - x[j])**2 + d_j * (xi - x[j])**3
                break
    
    return y_new


t = np.array([0, 0.2, 0.6, 1, 2, 5, 10])
C = np.array([5.19, 3.77, 2.3, 1.57, 0.8, 0.25, 0.094])

t_interpolate = np.array([0.1, 0.4, 1.2, 5.8])

t_plot = np.linspace(0, 10, 200) #绘图 不然就会是折线

C_interpolate = cha_zhi(t, C, t_interpolate)
C_plot = cha_zhi(t, C, t_plot)

print("t=0.1,0.4,1.2,5.8min时的C值分别为：")
for i, value in enumerate(C_interpolate):
    print(f"{value:.8f}", end=", ")

plt.figure(figsize=(10, 6))
plt.plot(t, C, 'ro', label='实验数据点')
plt.plot(t_plot, C_plot, 'b-', label='三次样条插值')
plt.plot(t_interpolate, C_interpolate, 'g*', label='插值计算点')

plt.xlabel('时间 t/min')
plt.ylabel('浓度 C/(g/L)')
plt.title('反应物浓度随时间变化的三次样条插值')
plt.grid(True)
plt.legend()
plt.show()
