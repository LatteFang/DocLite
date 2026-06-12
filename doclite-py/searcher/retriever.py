import os
import logging
from typing import List, Dict, Optional
from functools import lru_cache
from indexer.embedder import Embedder, VectorStore
from scanner.chunker import chunk_document
from scanner.parser import extract_text

logger = logging.getLogger(__name__)

class DocumentRetriever:
    """文档检索器"""
    
    def __init__(self, vector_store_dir: str, model_name: str = None):
        """
        初始化文档检索器
        
        Args:
            vector_store_dir: 向量存储目录
            model_name: 嵌入模型名称
        """
        self.vector_store_dir = vector_store_dir
        self.vector_store = VectorStore(vector_store_dir)
        self.embedder = Embedder(model_name)
        
        # 缓存向量和元数据
        self._vectors_cache = None
        self._metadata_cache = None
        self._cache_loaded = False
    
    def _load_cache(self):
        """加载缓存的向量和元数据"""
        if not self._cache_loaded:
            self._vectors_cache, self._metadata_cache = self.vector_store.load()
            self._cache_loaded = True
    
    def invalidate_cache(self):
        """使缓存失效"""
        self._cache_loaded = False
        self._vectors_cache = None
        self._metadata_cache = None
    
    def index_document(self, file_info: dict, content: str = None):
        """
        索引单个文档
        
        Args:
            file_info: 文件信息
            content: 文档内容（可选，如果不提供则自动提取）
        """
        if content is None:
            content = extract_text(file_info)
        
        if not content:
            logger.warning(f"无法提取文档内容: {file_info['path']}")
            return
        
        # 切分文档
        chunks = chunk_document(file_info, content)
        
        if not chunks:
            logger.warning(f"文档切分后无内容: {file_info['path']}")
            return
        
        # 生成嵌入
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embedder.generate_embeddings(texts)
        
        # 保存到向量存储
        self.vector_store.add_vectors(embeddings, chunks)
        logger.info(f"索引文档完成: {file_info['path']}，共 {len(chunks)} 个块")
    
    def index_documents(self, file_infos: List[dict]):
        """
        批量索引文档
        
        Args:
            file_infos: 文件信息列表
        """
        for file_info in file_infos:
            try:
                self.index_document(file_info)
            except Exception as e:
                logger.error(f"索引文档失败 {file_info['path']}: {e}")
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        检索与查询相关的文档块
        
        Args:
            query: 查询文本
            top_k: 返回前 k 个结果
        
        Returns:
            相关文档块列表
        """
        # 加载缓存
        self._load_cache()
        
        # 如果没有缓存数据，使用向量存储搜索
        if self._vectors_cache is None or len(self._vectors_cache) == 0:
            return []
        
        # 生成查询嵌入
        query_embedding = self.embedder.generate_single_embedding(query)
        
        # 使用缓存数据搜索
        import numpy as np
        
        # 计算余弦相似度
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        vectors_norm = self._vectors_cache / np.linalg.norm(self._vectors_cache, axis=1, keepdims=True)
        similarities = np.dot(vectors_norm, query_norm)
        
        # 获取 top_k 个最相似的结果
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                'index': int(idx),
                'similarity': float(similarities[idx]),
                'metadata': self._metadata_cache[idx] if idx < len(self._metadata_cache) else {}
            })
        
        return results
    
    def retrieve_with_context(self, query: str, top_k: int = 5, context_window: int = 1) -> List[Dict]:
        """
        检索与查询相关的文档块，并包含上下文
        
        Args:
            query: 查询文本
            top_k: 返回前 k 个结果
            context_window: 上下文窗口大小（前后各多少个块）
        
        Returns:
            相关文档块列表（包含上下文）
        """
        # 获取初始检索结果
        results = self.retrieve(query, top_k)
        
        # 获取所有元数据用于上下文
        _, all_metadata = self.vector_store.load()
        
        enhanced_results = []
        for result in results:
            metadata = result['metadata']
            chunk_index = metadata.get('index', 0)
            file_path = metadata.get('path', '')
            
            # 查找同一文档的其他块
            context_chunks = []
            for i in range(max(0, chunk_index - context_window), 
                          min(len(all_metadata), chunk_index + context_window + 1)):
                if all_metadata[i].get('path') == file_path:
                    context_chunks.append(all_metadata[i])
            
            # 按块索引排序
            context_chunks.sort(key=lambda x: x.get('index', 0))
            
            enhanced_results.append({
                'text': metadata.get('text', ''),
                'filename': metadata.get('filename', ''),
                'path': metadata.get('path', ''),
                'file_type': metadata.get('file_type', ''),
                'similarity': result['similarity'],
                'context': [chunk.get('text', '') for chunk in context_chunks]
            })
        
        return enhanced_results
