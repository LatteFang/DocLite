import os
import json
import logging
import numpy as np
from typing import List, Dict, Optional
from functools import lru_cache
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# 默认使用轻量级模型
DEFAULT_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

# 模型缓存
_model_cache = {}

def get_model(model_name: str = DEFAULT_MODEL_NAME) -> SentenceTransformer:
    """获取缓存的模型实例"""
    if model_name not in _model_cache:
        logger.info(f"加载嵌入模型: {model_name}")
        _model_cache[model_name] = SentenceTransformer(model_name)
        logger.info("模型加载完成")
    return _model_cache[model_name]

class Embedder:
    """文档嵌入生成器"""
    
    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        """
        初始化嵌入生成器
        
        Args:
            model_name: sentence-transformers 模型名称
        """
        self.model_name = model_name
        self.model = get_model(model_name)
    
    @lru_cache(maxsize=1000)
    def _get_cached_embedding(self, text: str) -> np.ndarray:
        """获取缓存的单个文本嵌入"""
        return self.model.encode([text], convert_to_numpy=True)[0]
    
    def generate_embeddings(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        生成文本嵌入
        
        Args:
            texts: 文本列表
            batch_size: 批处理大小
        
        Returns:
            嵌入矩阵
        """
        if not texts:
            return np.array([])
        
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=len(texts) > 100,
                convert_to_numpy=True
            )
            return embeddings
        except Exception as e:
            logger.error(f"生成嵌入失败: {e}")
            raise
    
    def generate_single_embedding(self, text: str) -> np.ndarray:
        """
        生成单个文本的嵌入
        
        Args:
            text: 输入文本
        
        Returns:
            嵌入向量
        """
        return self._get_cached_embedding(text)

class VectorStore:
    """向量存储管理器"""
    
    def __init__(self, storage_dir: str):
        """
        初始化向量存储
        
        Args:
            storage_dir: 存储目录
        """
        self.storage_dir = storage_dir
        self.vectors_file = os.path.join(storage_dir, "vectors.npy")
        self.metadata_file = os.path.join(storage_dir, "metadata.json")
        
        # 缓存
        self._vectors_cache: Optional[np.ndarray] = None
        self._metadata_cache: Optional[List[Dict]] = None
        self._cache_valid = False
        
        # 确保存储目录存在
        os.makedirs(storage_dir, exist_ok=True)
    
    def _invalidate_cache(self):
        """使缓存失效"""
        self._cache_valid = False
        self._vectors_cache = None
        self._metadata_cache = None
    
    def save(self, vectors: np.ndarray, metadata: List[Dict]):
        """
        保存向量和元数据
        
        Args:
            vectors: 向量矩阵
            metadata: 元数据列表
        """
        try:
            np.save(self.vectors_file, vectors)
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # 更新缓存
            self._vectors_cache = vectors
            self._metadata_cache = metadata
            self._cache_valid = True
            
            logger.info(f"保存向量存储: {len(vectors)} 个向量")
        except Exception as e:
            logger.error(f"保存向量存储失败: {e}")
            raise
    
    def load(self) -> tuple:
        """
        加载向量和元数据
        
        Returns:
            (vectors, metadata) 元组
        """
        # 使用缓存
        if self._cache_valid and self._vectors_cache is not None:
            return self._vectors_cache, self._metadata_cache
        
        if not os.path.exists(self.vectors_file):
            return np.array([]), []
        
        try:
            vectors = np.load(self.vectors_file)
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # 更新缓存
            self._vectors_cache = vectors
            self._metadata_cache = metadata
            self._cache_valid = True
            
            logger.info(f"加载向量存储: {len(vectors)} 个向量")
            return vectors, metadata
        except Exception as e:
            logger.error(f"加载向量存储失败: {e}")
            raise
    
    def add_vectors(self, new_vectors: np.ndarray, new_metadata: List[Dict]):
        """
        添加新向量
        
        Args:
            new_vectors: 新向量矩阵
            new_metadata: 新元数据列表
        """
        existing_vectors, existing_metadata = self.load()
        
        if len(existing_vectors) == 0:
            combined_vectors = new_vectors
            combined_metadata = new_metadata
        else:
            combined_vectors = np.vstack([existing_vectors, new_vectors])
            combined_metadata = existing_metadata + new_metadata
        
        self.save(combined_vectors, combined_metadata)
    
    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Dict]:
        """
        搜索最相似的向量
        
        Args:
            query_vector: 查询向量
            top_k: 返回前 k 个结果
        
        Returns:
            包含相似度和元数据的结果列表
        """
        vectors, metadata = self.load()
        
        if len(vectors) == 0:
            return []
        
        # 计算余弦相似度（优化版本）
        query_norm = np.linalg.norm(query_vector)
        if query_norm == 0:
            return []
        
        query_normalized = query_vector / query_norm
        
        # 向量化计算
        vectors_norm = np.linalg.norm(vectors, axis=1, keepdims=True)
        # 避免除以零
        vectors_norm = np.where(vectors_norm == 0, 1, vectors_norm)
        vectors_normalized = vectors / vectors_norm
        
        similarities = np.dot(vectors_normalized, query_normalized)
        
        # 获取 top_k 个最相似的结果（优化排序）
        if top_k >= len(similarities):
            top_indices = np.argsort(similarities)[::-1]
        else:
            # 使用 argpartition 优化大数组排序
            top_indices = np.argpartition(similarities, -top_k)[-top_k:]
            top_indices = top_indices[np.argsort(similarities[top_indices])[::-1]]
        
        results = []
        for idx in top_indices:
            results.append({
                'index': int(idx),
                'similarity': float(similarities[idx]),
                'metadata': metadata[idx] if idx < len(metadata) else {}
            })
        
        return results
