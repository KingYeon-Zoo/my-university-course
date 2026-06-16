# 基于BERT的IMDB情感分析实验

## 📝 项目简介

本项目实现了基于BERT（Bidirectional Encoder Representations from Transformers）的电影评论情感分析任务，使用IMDB数据集进行训练和评估。项目完成了以下实验要求：

**三个独立实验：**

1. ✅ **实验1 - BERT基础实现**：完整的数据处理、模型训练、评估流程
2. ✅ **实验2 - 模型对比**：对比BERT和RoBERTa的性能和训练速度差异
3. ✅ **实验3 - 数据增强**：在两个模型上都应用EDA数据增强，对比增强效果
4. ✅ **可视化分析**：为每个实验生成对应的可视化图表和数据

## 📂 项目结构

```
算法实验/
├── IMDB Dataset.csv          # IMDB数据集
├── requirements.txt          # 依赖包列表
├── README.md                 # 项目说明文档
├── main.py                   # 主程序入口
├── quick_test.py             # 快速测试脚本
├── data_loader.py            # 数据加载和预处理
├── data_augmentation.py      # 数据增强模块
├── model.py                  # 模型定义
├── train.py                  # 训练和评估
├── visualization.py          # 可视化模块
└── results/                  # 实验结果目录
    ├── training_history.png      # 训练历史曲线
    ├── model_comparison.png      # 模型性能对比
    ├── augmentation_comparison.png  # 数据增强效果对比
    ├── *_confusion_matrix.png    # 各模型混淆矩阵
    └── experiment_summary.json   # 实验总结报告
```

## 🚀 快速开始

### 1. 环境配置

首先安装所需依赖包：

```bash
pip install -r requirements.txt
```

**主要依赖：**
- PyTorch >= 2.0.0
- Transformers >= 4.30.0
- Pandas, NumPy, Scikit-learn
- Matplotlib, Seaborn（用于可视化）
- nlpaug（用于数据增强）

### 2. 数据准备

确保 `IMDB Dataset.csv` 文件在项目根目录下。数据集包含50000条电影评论，每条评论都标注了情感（positive/negative）。

**数据格式：**
- `review`: 评论文本
- `sentiment`: 情感标签（positive/negative）

### 3. 快速测试

在运行完整实验前，建议先运行快速测试验证环境配置：

```bash
python quick_test.py
```

这将使用500条数据进行快速测试（约5-10分钟），验证代码是否正常运行。

### 4. 运行完整实验

**一键运行所有三个实验：**

```bash
bash run_all.sh
```

或直接运行Python：

```bash
python main.py \
  --data_path "IMDB Dataset.csv" \
  --epochs 3 \
  --batch_size 16 \
  --aug_type "eda" \
  --aug_ratio 0.1
```

程序会自动依次完成：
- 实验1：BERT基础实现
- 实验2：BERT vs RoBERTa对比
- 实验3：数据增强效果对比（在两个模型上）

## ⚙️ 参数说明

### 数据参数
- `--data_path`: 数据集路径（默认: `IMDB Dataset.csv`）
- `--results_dir`: 结果保存目录（默认: `results`）

### 模型参数
- 程序固定使用 `bert-base-uncased` 和 `roberta-base` 两个模型

### 训练参数
- `--batch_size`: 批次大小（默认: 16，GPU内存不足可减小）
- `--epochs`: 训练轮数（默认: 3）
- `--learning_rate`: 学习率（默认: 2e-5）
- `--max_length`: 最大序列长度（默认: 256）
- `--seed`: 随机种子（默认: 42）

### 数据增强参数
- `--aug_type`: 数据增强类型（默认: `eda`）
  - `eda`: Easy Data Augmentation（同义词替换、随机插入、随机交换、随机删除）
  - `synonym`: 同义词替换
  - `back_translation`: 回译增强
- `--aug_ratio`: 数据增强比例（默认: 0.1，即10%的数据会被增强）

## 📊 实验结果说明

运行完成后，`results/` 目录下会生成以下文件：

### 1. 可视化图表（按实验分类）

**实验1 - BERT基础实现：**
- `exp1_bert_confusion_matrix.png`: BERT混淆矩阵

**实验2 - 模型对比：**
- `exp2_training_comparison.png`: BERT vs RoBERTa训练曲线对比
- `exp2_model_comparison.png`: 性能指标和训练速度对比
- `exp2_roberta_confusion_matrix.png`: RoBERTa混淆矩阵

**实验3 - 数据增强：**
- `exp3_bert_augmentation_comparison.png`: BERT数据增强效果
- `exp3_roberta_augmentation_comparison.png`: RoBERTa数据增强效果
- `exp3_overall_augmentation_comparison.png`: 总体对比（两个模型）
- `exp3_bert_augmented_confusion_matrix.png`: BERT增强后混淆矩阵
- `exp3_roberta_augmented_confusion_matrix.png`: RoBERTa增强后混淆矩阵

### 2. JSON结果文件

- **experiment_summary.json**: 实验总结报告
  - 对比的模型列表
  - 最佳模型及其性能
  - 所有模型的详细指标
  - 数据增强实验结果
  - 超参数配置

- **{model_name}_history.json**: 每个模型的训练历史
  - 每个epoch的训练/验证损失和准确率
  - 每个epoch的训练时间

- **{model_name}_results.json**: 每个模型的最终结果
  - 准确率、精确率、召回率、F1分数
  - 平均epoch训练时间

## 🔬 实验流程详解

### 实验1：BERT基础实现

1. 加载IMDB数据集并预处理
2. 创建BERT tokenizer和数据加载器
3. 训练BERT模型（3个epoch）
4. 评估性能并生成混淆矩阵

### 实验2：模型对比

1. 训练RoBERTa模型
2. 收集BERT和RoBERTa的训练历史
3. 对比性能指标：准确率、精确率、召回率、F1
4. 对比训练速度：平均epoch时间
5. 生成对比图表

### 实验3：数据增强

1. **应用数据增强（EDA方法）**：
   - 同义词替换（Synonym Replacement）
   - 随机插入（Random Insertion）
   - 随机交换（Random Swap）
   - 随机删除（Random Deletion）

2. **在BERT上测试增强效果**：
   - 使用增强数据重新训练BERT
   - 对比增强前后的性能

3. **在RoBERTa上测试增强效果**：
   - 使用增强数据重新训练RoBERTa
   - 对比增强前后的性能

4. **生成总体对比**：
   - 对比两个模型的增强效果
   - 分析数据增强的影响

## 📈 预期结果

根据IMDB数据集的特点，预期结果如下：

### 模型性能（3个epoch）

| 模型 | 准确率 | F1分数 | 平均Epoch时间 |
|------|--------|--------|---------------|
| BERT-base | ~88-90% | ~88-90% | 8-12分钟 |
| RoBERTa-base | ~89-91% | ~89-91% | 8-12分钟 |

*注：实际结果受硬件配置、数据划分等因素影响*

### 数据增强效果

使用EDA方法通常可以带来：
- 准确率提升：0.5-2%
- 模型鲁棒性增强
- 在小样本情况下效果更明显

## 🎯 实验要点

### 1. BERT模型架构

- **输入**：[CLS] + 文本tokens + [SEP]
- **编码**：12层Transformer Encoder（BERT-base）
- **输出**：使用[CLS]位置的输出作为句子表示
- **分类**：在[CLS]输出上添加全连接层

### 2. 关键超参数

- **学习率**：2e-5（BERT论文推荐值）
- **Batch Size**：16（根据GPU内存调整）
- **Max Length**：256（根据IMDB评论长度特点）
- **Warmup**：使用linear warmup避免训练初期不稳定

### 3. 评估指标

- **准确率（Accuracy）**：正确分类的样本比例
- **精确率（Precision）**：预测为正的样本中实际为正的比例
- **召回率（Recall）**：实际为正的样本中被正确预测的比例
- **F1分数**：精确率和召回率的调和平均

### 4. 数据增强策略

EDA的四种操作：

1. **同义词替换（SR）**：随机选择n个非停用词，替换为同义词
2. **随机插入（RI）**：随机插入n个同义词到句子中
3. **随机交换（RS）**：随机交换句子中的两个词，重复n次
4. **随机删除（RD）**：以概率p随机删除句子中的词

## 💡 使用建议

### 硬件要求

- **最低配置**：
  - CPU：4核以上
  - 内存：16GB
  - 训练时间：约2-3小时/模型（CPU）

- **推荐配置**：
  - GPU：NVIDIA GPU（8GB+ 显存）
  - 内存：16GB
  - 训练时间：约20-30分钟/模型（GPU）

### 显存优化

如果遇到显存不足（OOM）问题：

```bash
# 减小batch size
python main.py --batch_size 8

# 减小最大序列长度
python main.py --max_length 128

# 使用梯度累积（需修改代码）
# 或使用更小的模型如distilbert
python main.py --models "distilbert-base-uncased"
```

### 加速训练

1. **减少数据量**：在 `data_loader.py` 中采样部分数据
2. **减少epoch数**：`--epochs 2`
3. **使用小模型**：如 `distilbert-base-uncased`
4. **使用GPU**：确保PyTorch正确安装CUDA版本

## 🐛 常见问题

### 1. 网络连接问题（无法下载预训练模型）

**解决方案**：
```python
# 方案1：使用镜像源
export HF_ENDPOINT=https://hf-mirror.com

# 方案2：手动下载模型并指定本地路径
# 从 https://huggingface.co/ 下载模型文件
# 然后在代码中使用本地路径
```

### 2. 显存不足

**解决方案**：
- 减小 batch_size
- 减小 max_length
- 使用 DistilBERT 等更小的模型
- 使用梯度累积

### 3. 训练速度慢

**解决方案**：
- 确保使用GPU训练
- 减少数据量（采样）
- 减少epoch数
- 减小max_length

### 4. 准确率不理想

**解决方案**：
- 增加训练epoch数
- 调整学习率
- 使用数据增强
- 尝试不同的预训练模型
- 增加训练数据量

## 📚 参考资料

1. **BERT论文**：[BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding](https://arxiv.org/abs/1810.04805)

2. **RoBERTa论文**：[RoBERTa: A Robustly Optimized BERT Pretraining Approach](https://arxiv.org/abs/1907.11692)

3. **EDA论文**：[EDA: Easy Data Augmentation Techniques for Boosting Performance on Text Classification Tasks](https://arxiv.org/abs/1901.11196)

4. **IMDB数据集**：[Large Movie Review Dataset](https://ai.stanford.edu/~amaas/data/sentiment/)

5. **Hugging Face Transformers文档**：[https://huggingface.co/docs/transformers](https://huggingface.co/docs/transformers)

## 📝 实验报告建议

根据 `报告模板.md`，建议报告包含以下内容：

### 1. 实验内容和要求
- 复述实验要求
- 说明实验目标

### 2. 问题背景和相关工作
- BERT模型原理介绍
- 情感分析任务背景
- 已有研究和方法

### 3. 解题思路
- 数据预处理流程
- 模型架构设计
- 训练策略

### 4. 算法伪代码
- 数据加载算法
- 模型训练算法
- 数据增强算法

### 5. 实验设置
- 使用本README中的参数配置
- 说明硬件环境
- 列出对比的模型

### 6. 实验结果
- 插入生成的可视化图表
- 列出性能指标表格
- 展示混淆矩阵

### 7. 实验结果分析
- 分析不同模型的性能差异
- 分析训练速度差异的原因
- 分析数据增强的效果
- 讨论改进空间

### 8. 总结
- 实验收获
- 遇到的问题和解决方案
- 后续改进建议

## 🤝 贡献

欢迎提出问题和改进建议！

## 📄 许可证

本项目仅用于学习和研究目的。

---

**祝实验顺利！** 🎉

如有任何问题，请参考上述文档或查看代码注释。

