def solve_dishes():
    """
    厨师制作菜品问题
    改进策略：优先配对，避免产生难以使用的余数
    """
    T = int(input())
    
    for _ in range(T):
        n, m, k = map(int, input().split())
        materials = list(map(int, input().split()))
        
        # 基本检查
        if sum(materials) != m * k:
            print(-1)
            continue
        
        # 存储答案和剩余材料
        result = []
        remaining = materials[:]
        
        # 贪心策略：每次尝试做一道菜
        success = True
        for dish_num in range(m):
            dish_made = False
            
            # 策略1：优先寻找和为k的完美配对
            for i in range(n):
                if dish_made:
                    break
                if remaining[i] == 0:
                    continue
                    
                for j in range(i + 1, n):
                    if remaining[j] == 0:
                        continue
                    
                    if remaining[i] + remaining[j] == k:
                        # 完美配对
                        result.append([i + 1, remaining[i], j + 1, remaining[j]])
                        remaining[i] = 0
                        remaining[j] = 0
                        dish_made = True
                        break
            
            if dish_made:
                continue
            
            # 策略2：使用单一材料（但只在合适时使用）
            # 只使用恰好是k的倍数的材料
            for i in range(n):
                if remaining[i] % k == 0 and remaining[i] >= k:
                    result.append([i + 1, k])
                    remaining[i] -= k
                    dish_made = True
                    break
            
            if dish_made:
                continue
            
            # 策略3：使用一种材料的全部+另一种的部分（优先用完小的）
            # 按剩余量排序，优先用完小的
            indices_sorted = sorted(range(n), key=lambda i: remaining[i] if remaining[i] > 0 else float('inf'))
            
            for i in indices_sorted:
                if dish_made:
                    break
                if remaining[i] == 0 or remaining[i] >= k:
                    continue
                
                for j in range(n):
                    if i == j or remaining[j] == 0:
                        continue
                    
                    if remaining[i] + remaining[j] >= k:
                        need = k - remaining[i]
                        result.append([i + 1, remaining[i], j + 1, need])
                        remaining[i] = 0
                        remaining[j] -= need
                        dish_made = True
                        break
            
            if dish_made:
                continue
            
            # 策略4：两种材料都使用部分
            for i in range(n):
                if dish_made:
                    break
                if remaining[i] == 0:
                    continue
                
                for j in range(i + 1, n):
                    if remaining[j] == 0:
                        continue
                    
                    if remaining[i] + remaining[j] > k:
                        # 可以凑出一道菜
                        # 尽量让分配更平均
                        use_i = min(remaining[i], k // 2 + 1)
                        use_j = k - use_i
                        if use_j > 0 and use_j <= remaining[j]:
                            result.append([i + 1, use_i, j + 1, use_j])
                            remaining[i] -= use_i
                            remaining[j] -= use_j
                            dish_made = True
                            break
            
            if not dish_made:
                success = False
                break
        
        # 输出结果
        if success and len(result) == m:
            for dish in result:
                print(' '.join(map(str, dish)))
        else:
            print(-1)

solve_dishes()
