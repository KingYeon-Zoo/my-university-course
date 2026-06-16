#!/bin/bash

# 进入Simplescalar工作目录
cd /opt/simplescalar_all/simplesim-3.0 || {
    echo "错误: 无法进入目录 /opt/simplescalar_all/simplesim-3.0"
    exit 1
}

# 配置输出路径
OUTPUT_PATH="/opt/simplescalar_all/simplesim-3.0/exp_results"
mkdir -p $OUTPUT_PATH

# 测试程序配置
declare -A test_programs=(
    ["bzip2"]="./bzip200.peak.ev6 bzip2.lgred.graphic 1"
    ["gcc"]="./gcc00.peak.ev6 gcc.lgred.cp-decl.i"
    ["mcf"]="./mcf00.peak.ev6 mcf.lgred.in"
)

# 预测器配置
declare -A bp_configs=(
    ["taken_always"]="-bpred taken"
    ["nottaken_always"]="-bpred nottaken"
    ["bimod_1024"]="-bpred bimod -bpred:bimod 1024"
    ["bimod_512"]="-bpred bimod -bpred:bimod 512"
    ["2lev_1_64_6_1"]="-bpred 2lev -bpred:2lev 1 64 6 1"
    ["2lev_1_1024_8_0"]="-bpred 2lev -bpred:2lev 1 1024 8 0"
)

echo "开始执行分支预测实验..."
echo "结果保存至: $OUTPUT_PATH"
echo "========================================"

# 执行实验
for test_name in "${!test_programs[@]}"; do
    cmd_line="${test_programs[$test_name]}"
    
    for bp_name in "${!bp_configs[@]}"; do
        config_str="${bp_configs[$bp_name]}"
        
        # 输出文件
        result_file="${OUTPUT_PATH}/${test_name}.${bp_name}.txt"
        
        # 执行命令
        full_cmd="./sim-bpred $config_str $cmd_line"
        
        echo "正在运行: $test_name - $bp_name"
        
        # 运行并保存结果
        eval $full_cmd > "$result_file" 2>&1
        
        if [ $? -eq 0 ]; then
            echo "完成: $test_name - $bp_name"
        else
            echo "失败: $test_name - $bp_name"
        fi
        echo
    done
done

echo "实验完成!"
echo "输出目录: $OUTPUT_PATH"
echo "生成文件数: $(ls -1 $OUTPUT_PATH | wc -l)"

