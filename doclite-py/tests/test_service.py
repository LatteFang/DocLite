import os
import pytest
import tempfile
from indexer.engine import build_index
from searcher.service import search_documents

class TestSearchService:
    """搜索服务测试类"""
    
    @pytest.fixture
    def sample_index(self):
        """创建测试索引"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建测试文件
            test_file = os.path.join(temp_dir, "test.txt")
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write("这是一个测试文档，包含搜索关键词。")
            
            # 构建索引
            build_index(temp_dir)
            
            yield temp_dir
    
    def test_search_basic(self, sample_index):
        """测试基本搜索"""
        results = search_documents("测试", page=1, per_page=10)
        
        assert 'total' in results
        assert 'results' in results
        assert isinstance(results['results'], list)
    
    def test_search_with_file_type(self, sample_index):
        """测试文件类型筛选"""
        results = search_documents("测试", page=1, per_page=10, file_type="txt")
        
        assert 'total' in results
        for result in results['results']:
            assert result['file_type'] == 'txt'
    
    def test_search_empty_query(self, sample_index):
        """测试空查询"""
        results = search_documents("", page=1, per_page=10)
        
        # 空查询应该返回所有结果或特定处理
        assert 'total' in results
