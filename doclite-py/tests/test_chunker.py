import pytest
from scanner.chunker import chunk_text, chunk_document

class TestChunker:
    """切块器测试类"""
    
    def test_chunk_text_basic(self):
        """测试基本文本切块"""
        text = "这是一段测试文本。" * 100  # 创建足够长的文本
        chunks = chunk_text(text, chunk_size=50, overlap=10)
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert 'text' in chunk
            assert 'index' in chunk
            assert 'start_pos' in chunk
            assert 'end_pos' in chunk
    
    def test_chunk_text_empty(self):
        """测试空文本切块"""
        chunks = chunk_text("", chunk_size=50, overlap=10)
        assert len(chunks) == 0
    
    def test_chunk_text_short(self):
        """测试短文本切块"""
        text = "短文本"
        chunks = chunk_text(text, chunk_size=50, overlap=10)
        assert len(chunks) == 1
        assert chunks[0]['text'] == text
    
    def test_chunk_document(self):
        """测试文档切块"""
        file_info = {
            'path': '/tmp/test.txt',
            'filename': 'test.txt',
            'file_type': 'txt',
            'mtime': 1234567890,
            'size': 1024
        }
        content = "这是文档内容。" * 50
        
        chunks = chunk_document(file_info, content, chunk_size=50, overlap=10)
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert 'text' in chunk
            assert 'path' in chunk
            assert 'filename' in chunk
            assert 'file_type' in chunk
            assert chunk['path'] == file_info['path']
            assert chunk['filename'] == file_info['filename']
