import numpy as np
import pandas as pd

def f(x):
    return np.sin(x) / x

def trapezoid(f, a, b, n):
    h = (b - a) / n
    x = np.linspace(a, b, n+1)
    y = f(x)
    return h * (0.5 * y[0] + np.sum(y[1:-1]) + 0.5 * y[-1])

def simpson(f, a, b, n):
    h = (b - a) / n
    x = np.linspace(a, b, n+1)
    y = f(x)
    return h/3 * (y[0] + 4*np.sum(y[1:-1:2]) + 2*np.sum(y[2:-1:2]) + y[-1])

def romberg(f, a, b, eps=1e-6):
    max_steps = 5  
    T = np.zeros(max_steps)
    S = np.zeros(max_steps)
    C = np.zeros(max_steps)
    R = np.zeros(max_steps)

    for i in range(max_steps):
        n = 2**i
        T[i] = trapezoid(f, a, b, n)

    for i in range(1, max_steps):
        S[i] = (4*T[i] - T[i-1])/3
    
    for i in range(2, max_steps):
        C[i] = (16*S[i] - S[i-1])/15
    
    for i in range(3, max_steps):
        R[i] = (64*C[i] - C[i-1])/63
    
    return T, S, C, R, R[-1]

a, b = 0.1, 1  
eps = 1e-6   

print("复化梯形公式结果:")
for n in [2, 4, 8, 16]:
    result = trapezoid(f, a, b, n)
    print(f"n={n}: {result:.7f}")

print("\n复化辛普森公式结果:")
for n in [2, 4, 8, 16]:
    result = simpson(f, a, b, n)
    print(f"n={n}: {result:.7f}")

print("\n龙贝格算法结果:")

T, S, C, R, result = romberg(f, a, b, eps)

data = {
    'k': list(range(5)),
    'T': T,
    'S': ['-', *S[1:]],
    'C': ['-', '-', *C[2:]],
    'R': ['-', '-', '-', *R[3:]]
}

df = pd.DataFrame(data)
pd.set_option('display.float_format', lambda x: '{:.7f}'.format(x) if isinstance(x, (float, int)) else str(x))

print(df.to_string(index=False))
print(f"\nresult is: {result:.7f}")
