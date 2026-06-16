"""
数据增强模块
实现EDA（Easy Data Augmentation）和其他数据增强方法
"""

import random
import nlpaug.augmenter.word as naw
import nlpaug.augmenter.sentence as nas
from tqdm import tqdm


class DataAugmenter:
    """数据增强器"""
    
    def __init__(self, aug_type='eda'):
        """
        初始化数据增强器
        
        Args:
            aug_type: 增强类型 ('eda', 'synonym', 'back_translation')
        """
        self.aug_type = aug_type
        
        if aug_type == 'synonym':
            # 同义词替换
            self.augmenter = naw.SynonymAug(aug_src='wordnet')
        elif aug_type == 'back_translation':
            # 回译增强（使用预训练模型）
            self.augmenter = naw.BackTranslationAug(
                from_model_name='facebook/wmt19-en-de',
                to_model_name='facebook/wmt19-de-en'
            )
        else:
            # 默认使用EDA的组合方法
            self.augmenter = None
    
    def eda_augment(self, text, alpha_sr=0.1, alpha_ri=0.1, alpha_rs=0.1, p_rd=0.1, num_aug=1):
        """
        EDA数据增强
        
        Args:
            text: 原始文本
            alpha_sr: 同义词替换比例
            alpha_ri: 随机插入比例
            alpha_rs: 随机交换比例
            p_rd: 随机删除概率
            num_aug: 生成增强样本数量
            
        Returns:
            增强后的文本列表
        """
        words = text.split()
        num_words = len(words)
        augmented_texts = []
        
        for _ in range(num_aug):
            aug_words = words.copy()
            
            # 同义词替换
            n_sr = max(1, int(alpha_sr * num_words))
            for _ in range(n_sr):
                self._synonym_replacement(aug_words)
            
            # 随机插入
            n_ri = max(1, int(alpha_ri * num_words))
            for _ in range(n_ri):
                self._random_insertion(aug_words)
            
            # 随机交换
            n_rs = max(1, int(alpha_rs * num_words))
            for _ in range(n_rs):
                self._random_swap(aug_words)
            
            # 随机删除
            aug_words = self._random_deletion(aug_words, p_rd)
            
            augmented_texts.append(' '.join(aug_words))
        
        return augmented_texts
    
    def _synonym_replacement(self, words):
        """同义词替换（简化版本）"""
        if len(words) == 0:
            return
        
        # 简单的同义词字典
        synonyms = {
            'good': ['great', 'excellent', 'wonderful', 'fantastic'],
            'bad': ['terrible', 'awful', 'poor', 'horrible'],
            'like': ['enjoy', 'love', 'appreciate'],
            'great': ['excellent', 'wonderful', 'amazing', 'good'],
        }
        
        random_idx = random.randint(0, len(words) - 1)
        word = words[random_idx].lower()
        
        if word in synonyms and len(synonyms[word]) > 0:
            words[random_idx] = random.choice(synonyms[word])
    
    def _random_insertion(self, words):
        """随机插入"""
        if len(words) == 0:
            return
        
        random_word = random.choice(words)
        random_idx = random.randint(0, len(words))
        words.insert(random_idx, random_word)
    
    def _random_swap(self, words):
        """随机交换"""
        if len(words) < 2:
            return
        
        idx1 = random.randint(0, len(words) - 1)
        idx2 = random.randint(0, len(words) - 1)
        
        words[idx1], words[idx2] = words[idx2], words[idx1]
    
    def _random_deletion(self, words, p):
        """随机删除"""
        if len(words) == 1:
            return words
        
        new_words = []
        for word in words:
            if random.uniform(0, 1) > p:
                new_words.append(word)
        
        if len(new_words) == 0:
            return [random.choice(words)]
        
        return new_words
    
    def augment_data(self, texts, labels, aug_ratio=0.2, num_aug=1):
        """
        批量数据增强
        
        Args:
            texts: 原始文本列表
            labels: 原始标签列表
            aug_ratio: 需要增强的数据比例
            num_aug: 每个样本生成的增强样本数量
            
        Returns:
            augmented_texts, augmented_labels
        """
        augmented_texts = texts.copy()
        augmented_labels = labels.copy()
        
        # 随机选择需要增强的样本
        num_to_aug = int(len(texts) * aug_ratio)
        indices = random.sample(range(len(texts)), num_to_aug)
        
        print(f"正在对 {num_to_aug} 个样本进行数据增强...")
        
        for idx in tqdm(indices):
            text = texts[idx]
            label = labels[idx]
            
            # 生成增强样本
            if self.aug_type == 'eda':
                aug_texts = self.eda_augment(text, num_aug=num_aug)
            else:
                try:
                    aug_text = self.augmenter.augment(text)
                    aug_texts = [aug_text] if isinstance(aug_text, str) else aug_text
                except:
                    # 如果增强失败，使用原文本
                    aug_texts = [text]
            
            # 添加增强样本
            augmented_texts.extend(aug_texts)
            augmented_labels.extend([label] * len(aug_texts))
        
        print(f"数据增强完成！原始样本数: {len(texts)}, 增强后样本数: {len(augmented_texts)}")
        
        return augmented_texts, augmented_labels

