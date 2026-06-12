import os
import pytest
import tempfile
import numpy as np
from indexer.embedder import Embedder, VectorStore

class TestEmbedder:
    """嵌入生成器测试类"""
    
    def test_generate_single_embedding(self):
        """测试单个文本嵌入生成"""
        embedder = Embedder()
        embedding = embedder.generate_single_embedding("测试文本")
        
        assert embedding is not None
        assert isinstance(embedding, np.ndarray)
        assert len(embedding) > 0
    
    def test_generate_embeddings_batch(self):
        """测试批量文本嵌入生成"""
        embedder = Embedder()
        texts = ["文本1", "文本2", "文本3"]
        embeddings = embedder.generate_embeddings(texts)
        
        assert embeddings is not None
        assert isinstance(embeddings, np.ndarray)
        assert len(embeddings) == len(texts)
    
    def test_generate_embeddings_empty(self):
        """测试空文本列表嵌入生成"""
        embedder = Embedder()
        embeddings = embedder.generate_embeddings([])
        
        assert len(embeddings) == 0

class TestVectorStore:
    """向量存储测试类"""
    
    def test_save_and_load(self):
        """测试保存和加载向量"""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = VectorStore(temp_dir)
            
            # 创建测试数据
            vectors = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
            metadata = [{'text': '文档1'}, {'text': '文档2'}]
            
            # 保存
            store.save(vectors, metadata)
            
            # 加载
            loaded_vectors, loaded_metadata = store.load()
            
            assert np.array_equal(vectors, loaded_vectors)
            assert metadata == loaded_metadata
    
    def test_add_vectors(self):
        """测试添加向量"""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = VectorStore(temp_dir)
            
            # 初始数据
            vectors1 = np.array([[1.0, 2.0, 3.0]])
            metadata1 = [{'text': '文档1'}]
            store.save(vectors1, metadata1)
            
            # 添加新数据
            vectors2 = np.array([[4.0, 5.0, 6.0]])
            metadata2 = [{'text': '文档2'}]
            store.add_vectors(vectors2, metadata2)
            
            # 验证
            loaded_vectors, loaded_metadata = store.load()
            assert len(loaded_vectors) == 2
            assert len(loaded_metadata) == 2
    
    def test_search(self):
        """测试向量搜索"""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = VectorStore(temp_dir)
            
            # 创建测试数据
            vectors = np.array([
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0]
            ])
            metadata = [
                {'text': '文档1'},
                {'text': '文档2'},
                {'text': '文档3'}
            ]
            store.save(vectors, metadata)
            
            # 搜索
            query = np.array([1.0, 0.0, 0.0])
            results = store.search(query, top_k=2)
            
            assert len(results) == 2
            assert results[0]['similarity'] > results[1]['similarity']
