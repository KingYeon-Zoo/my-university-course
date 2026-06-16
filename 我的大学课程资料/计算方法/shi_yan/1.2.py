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
    
    # 计算h = x[i+1] - x[i]
    h = np.diff(x)
    
    # 构造三对角矩阵系数
    a = np.zeros(n+1) 
    b = np.zeros(n+1)
    c = np.zeros(n+1) 
    d = np.zeros(n+1) 
    
    # 填充三对角矩阵
    for i in range(1, n):
        a[i] = h[i-1]/(h[i-1] + h[i])
        b[i] = 2
        c[i] = 1 - a[i]
        d[i] = 6 * ((y[i+1] - y[i])/h[i] - (y[i] - y[i-1])/h[i-1]) / (h[i-1] + h[i])
    
    m = np.zeros(n+1)
    if n > 1:
        m[1:-1] = zhui_gan_fa(a[1:-1], b[1:-1], c[1:-1], d[1:-1])
    
    y_new = np.zeros_like(x_new)
    
    for i, xi in enumerate(x_new):
        # 找到xi所在的区间
        for j in range(n):
            if x[j] <= xi <= x[j+1]:
                # 计算插值
                hj = h[j]
                t = (xi - x[j]) / hj
                aj = y[j]
                bj = (y[j+1] - y[j])/hj - hj*(2*m[j] + m[j+1])/6
                cj = m[j]/2
                dj = (m[j+1] - m[j])/(6*hj)
                
                y_new[i] = aj + bj*(xi - x[j]) + cj*(xi - x[j])**2 + dj*(xi - x[j])**3
                break
    
    return y_new

x = np.array([0.0, 0.6, 1.5, 1.7, 1.9, 2.1, 2.3, 2.6, 2.8, 3.0,
              3.6, 4.7, 5.2, 5.7, 5.8, 6.0, 6.4, 6.9, 7.6, 8.0])
y = np.array([-0.8, -0.34, 0.59, 0.59, 0.23, 0.1, 0.28, 1.03, 1.5, 1.44,
              0.74, -0.82, -1.27, -0.92, -0.92, -1.04, -0.79, -0.06, 1.0, 0.0])

x_plot = np.linspace(min(x), max(x), 500)
y_plot = cha_zhi(x, y, x_plot)

plt.figure(figsize=(12, 6))
plt.plot(x, y, 'ro', label='数据点')
plt.plot(x_plot, y_plot, 'b-', label='三次样条插值')

plt.xlabel('x')
plt.ylabel('y')
plt.title('自由边界三次样条插值')
plt.grid(True)
plt.legend()
plt.show() 