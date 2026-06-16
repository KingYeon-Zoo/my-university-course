"""
模型定义模块
定义用于情感分类的BERT和RoBERTa模型
"""

import torch
import torch.nn as nn
from transformers import AutoModel, AutoConfig


class SentimentClassifier(nn.Module):
    """情感分类器"""
    
    def __init__(self, model_name, num_classes=2, dropout=0.3):
        """
        初始化模型
        
        Args:
            model_name: 预训练模型名称
            num_classes: 分类类别数
            dropout: dropout比例
        """
        super(SentimentClassifier, self).__init__()
        
        self.model_name = model_name
        
        # 加载预训练模型
        self.bert = AutoModel.from_pretrained(model_name)
        
        # 获取隐藏层维度
        config = AutoConfig.from_pretrained(model_name)
        hidden_size = config.hidden_size
        
        # 分类头
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(hidden_size, num_classes)
    
    def forward(self, input_ids, attention_mask):
        """
        前向传播
        
        Args:
            input_ids: 输入token ids
            attention_mask: 注意力掩码
            
        Returns:
            logits: 分类logits
        """
        # 通过BERT获取特征
        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
        # 使用[CLS]标记的输出
        pooled_output = outputs.pooler_output
        
        # 应用dropout和分类层
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        
        return logits


def get_model(model_name, num_classes=2, dropout=0.3):
    """
    获取模型实例
    
    Args:
        model_name: 模型名称
        num_classes: 分类类别数
        dropout: dropout比例
        
    Returns:
        model: 模型实例
    """
    model = SentimentClassifier(model_name, num_classes, dropout)
    return model

