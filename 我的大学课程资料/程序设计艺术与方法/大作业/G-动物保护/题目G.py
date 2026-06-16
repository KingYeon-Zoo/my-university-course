"""
题目G: 动物保护
问题描述：
    无人机从A点飞到B点，需要避开保护装置（球心C，半径R的球）
    A、B不在球内
    求最短飞行距离
    
解题思路：
    三维空间中的最短路径问题
    
情况分析：
    1. 如果AB线段不与球相交 -> 最短距离 = |AB|
    2. 如果AB线段与球相交 -> 需要绕过球面
    
相交判断：
    AB线段与球相交 <=> AB到C的最短距离 < R
    
绕过球面的最短路径：
    如果需要绕过球面，最短路径由三部分组成：
    - A到球面的切线段
    - 球面上的劣弧
    - 球面到B的切线段
    
计算方法：
    1. 计算A到C的距离 d1，B到C的距离 d2
    2. 计算A到球面切点的距离：sqrt(d1^2 - R^2)
    3. 计算B到球面切点的距离：sqrt(d2^2 - R^2)
    4. 计算球面上的圆心角θ，然后计算弧长 R*θ
    
    更简单的方法：
    - 从A到球面的切线长度：L1 = sqrt(|AC|^2 - R^2)
    - 从B到球面的切线长度：L2 = sqrt(|BC|^2 - R^2)
    - 球面弧长通过向量夹角计算
"""

import math

def distance(p1, p2):
    """计算两点间的欧几里得距离"""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))

def point_to_line_distance(A, B, C):
    """
    计算点C到线段AB的最短距离
    """
    # 向量AB和AC
    AB = [B[i] - A[i] for i in range(3)]
    AC = [C[i] - A[i] for i in range(3)]
    
    # AB的长度平方
    AB_len_sq = sum(x ** 2 for x in AB)
    
    if AB_len_sq == 0:  # A和B是同一点
        return distance(A, C)
    
    # 投影参数t
    t = sum(AB[i] * AC[i] for i in range(3)) / AB_len_sq
    
    # 限制t在[0, 1]之间，确保最近点在线段上
    t = max(0, min(1, t))
    
    # 最近点
    closest = [A[i] + t * AB[i] for i in range(3)]
    
    # 返回C到最近点的距离
    return distance(C, closest)

def solve():
    """
    主求解函数
    """
    # 读取A、B、C三个点的坐标
    A = list(map(int, input().split()))
    B = list(map(int, input().split()))
    C = list(map(int, input().split()))
    R = int(input())
    
    # 计算AB的直线距离
    dist_AB = distance(A, B)
    
    # 计算AB线段到C的最短距离
    dist_to_C = point_to_line_distance(A, B, C)
    
    # 如果AB线段不与球相交，直接返回AB距离
    if dist_to_C >= R:
        print(f"{dist_AB:.2f}")
        return
    
    # 需要绕过球面
    # 计算AC和BC的距离
    dist_AC = distance(A, C)
    dist_BC = distance(B, C)
    
    # 从A到球面的切线长度
    if dist_AC <= R:  # A在球内或球面上（题目保证不会发生）
        print(f"{dist_AB:.2f}")
        return
    tangent_A = math.sqrt(dist_AC ** 2 - R ** 2)
    
    # 从B到球面的切线长度
    if dist_BC <= R:  # B在球内或球面上（题目保证不会发生）
        print(f"{dist_AB:.2f}")
        return
    tangent_B = math.sqrt(dist_BC ** 2 - R ** 2)
    
    # 计算切点到C的向量
    # 切点在AC和BC与球面的交点
    # 使用余弦定理计算圆心角
    
    # A、B在球面的投影方向
    # 切点A': A + t * (C - A)，其中 |A' - C| = R
    # 切点B': B + s * (C - B)，其中 |B' - C| = R
    
    # 计算A的切点方向向量
    AC_vec = [C[i] - A[i] for i in range(3)]
    AC_len = dist_AC
    
    # 切点A'的位置：C + R * (A - C) / |A - C| 方向的某个点
    # 实际上有两个切点，选择靠近B的那个
    
    # 使用另一种方法：计算包含A、B、C三点的球面弧长
    # cos(angle_ACB)
    CA = [A[i] - C[i] for i in range(3)]
    CB = [B[i] - C[i] for i in range(3)]
    dot_product = sum(CA[i] * CB[i] for i in range(3))
    cos_angle_ACB = dot_product / (dist_AC * dist_BC)
    cos_angle_ACB = max(-1, min(1, cos_angle_ACB))  # 防止浮点误差
    angle_ACB = math.acos(cos_angle_ACB)
    
    # A和B的切点与C的夹角
    # 从A的切点：角度 = arccos(R / dist_AC)
    # 从B的切点：角度 = arccos(R / dist_BC)
    cos_angle_A = R / dist_AC
    cos_angle_B = R / dist_BC
    angle_A = math.acos(cos_angle_A)
    angle_B = math.acos(cos_angle_B)
    
    # 球面上的圆心角
    arc_angle = angle_ACB - angle_A - angle_B
    
    # 如果角度为负，说明不需要弧，直接切线
    if arc_angle < 0:
        arc_angle = 0
    
    # 球面弧长
    arc_length = R * arc_angle
    
    # 总距离
    total_distance = tangent_A + arc_length + tangent_B
    
    print(f"{total_distance:.2f}")

if __name__ == "__main__":
    solve()

