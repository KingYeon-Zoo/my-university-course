#!/bin/bash

# BERT情感分析实验 - 一键运行所有实验
# 用法：bash run_all.sh

echo "=========================================="
echo "  BERT情感分析实验 - 完整实验流程"
echo "=========================================="

# 检查数据集
if [ ! -f "IMDB Dataset.csv" ]; then
    echo "❌ 错误: 未找到 IMDB Dataset.csv 文件！"
    exit 1
fi

# 创建结果目录
mkdir -p results

echo ""
echo "📦 步骤1: 检查并安装依赖包..."
echo "----------------------------------------"
pip install -r requirements.txt -q
if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败，请手动运行: pip install -r requirements.txt"
    exit 1
fi
echo "✅ 依赖安装完成"

echo ""
echo "🚀 步骤2: 开始完整实验"
echo "----------------------------------------"
echo "本次实验包含三个部分："
echo "  实验1: BERT基础实现"
echo "  实验2: BERT vs RoBERTa 模型对比"
echo "  实验3: 数据增强效果对比（在两个模型上）"
echo ""
echo "实验配置："
echo "  - 训练轮数: 3 epochs"
echo "  - 批次大小: 16"
echo "  - 数据增强方法: EDA"
echo ""
echo "⏰ 预计时间: 60-120分钟（取决于硬件）"
echo ""
read -p "按Enter键开始实验，或Ctrl+C取消... " -r

# 运行完整实验
python main.py \
    --data_path "IMDB Dataset.csv" \
    --epochs 3 \
    --batch_size 16 \
    --max_length 256 \
    --aug_type "eda" \
    --aug_ratio 0.1 \
    --results_dir "results"

# 检查是否成功
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "  ✅ 所有实验完成！"
    echo "=========================================="
    echo ""
    echo "📊 生成的结果文件："
    echo "----------------------------------------"
    ls -lh results/ | grep -E '\.(png|json)$'
    echo ""
    echo "📄 主要结果按实验分类："
    echo ""
    echo "🔬 实验1 - BERT基础实现："
    echo "  - exp1_bert_confusion_matrix.png"
    echo ""
    echo "🔬 实验2 - 模型对比："
    echo "  - exp2_training_comparison.png (训练曲线对比)"
    echo "  - exp2_model_comparison.png (性能和速度对比)"
    echo "  - exp2_roberta_confusion_matrix.png"
    echo ""
    echo "🔬 实验3 - 数据增强："
    echo "  - exp3_bert_augmentation_comparison.png"
    echo "  - exp3_roberta_augmentation_comparison.png"
    echo "  - exp3_overall_augmentation_comparison.png (总体对比)"
    echo ""
    echo "📋 实验数据："
    echo "  - experiment_summary.json (所有实验数据)"
    echo ""
    echo "💡 这些图表和数据可以直接用于实验报告！"
    echo ""
else
    echo ""
    echo "❌ 实验过程中出现错误，请检查错误信息"
    exit 1
fi
