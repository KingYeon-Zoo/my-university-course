#!/bin/bash

# 配置路径
DATA_DIR="/opt/simplescalar_all/simplesim-3.0/exp_results"
OUTPUT_CSV="$DATA_DIR/statistics.csv"

# 写入CSV表头
echo "Benchmark,Predictor,Branches,Mispredictions,MissRate,Accuracy" > "$OUTPUT_CSV"

echo "开始分析实验数据..."
echo "数据目录: $DATA_DIR"
echo "================================"

# 程序列表
benchmarks=("bzip2" "gcc" "mcf")

# 处理每个benchmark的结果
for bench in "${benchmarks[@]}"; do
    echo "分析 $bench 的结果..."
    
    for data_file in "$DATA_DIR"/${bench}.*.txt; do
        if [[ -f "$data_file" ]]; then
            # 提取预测器名称
            base_name=$(basename "$data_file" .txt)
            pred_name=$(echo "$base_name" | sed "s/${bench}\.//")
            
            echo "  处理: $base_name"
            
            # 提取分支总数
            branch_count=$(grep -E "sim_num_branches[[:space:]]+[0-9]+" "$data_file" | awk '{print $2}' | tr -d '[:space:]')
            
            # 根据预测器类型提取错误预测数
            mispred_count=""
            
            if [[ "$pred_name" == "taken_always" ]]; then
                pattern="bpred_taken\.misses"
            elif [[ "$pred_name" == "nottaken_always" ]]; then
                pattern="bpred_nottaken\.misses"
            elif [[ "$pred_name" == bimod_* ]]; then
                pattern="bpred_bimod\.misses"
            elif [[ "$pred_name" == 2lev_* ]]; then
                pattern="bpred_2lev\.misses"
            else
                pattern="bpred_.*\.misses"
            fi
            
            mispred_count=$(grep -E "$pattern" "$data_file" | awk '{print $2}' | tr -d '[:space:]')
            
            # 如果未找到，使用通用搜索
            if [[ -z "$mispred_count" ]]; then
                mispred_count=$(grep -E "bpred_.*\.misses" "$data_file" | awk '{print $2}' | head -1 | tr -d '[:space:]')
            fi
            
            # 计算准确率
            if [[ -n "$branch_count" && -n "$mispred_count" && "$branch_count" -gt 0 ]]; then
                miss_ratio=$(awk "BEGIN {printf \"%.6f\", $mispred_count / $branch_count}")
                accuracy=$(awk "BEGIN {printf \"%.6f\", 1 - ($mispred_count / $branch_count)}")
                echo "    成功: 准确率=$accuracy"
                
                echo "$bench,$pred_name,$branch_count,$mispred_count,$miss_ratio,$accuracy" >> "$OUTPUT_CSV"
            else
                echo "    失败: 数据不完整"
                echo "$bench,$pred_name,$branch_count,$mispred_count,N/A,N/A" >> "$OUTPUT_CSV"
            fi
        fi
    done
    echo "--------------------------------"
done

echo ""
echo "分析完成!"
echo "统计结果: $OUTPUT_CSV"
echo ""
echo "结果预览:"
echo "=========="
cat "$OUTPUT_CSV"
echo ""
echo "处理的文件数: $(find "$DATA_DIR" -name "*.txt" | wc -l)"
echo "统计记录数: $(wc -l < "$OUTPUT_CSV")"

