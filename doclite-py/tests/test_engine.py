import os
import pytest
import tempfile
import shutil
from indexer.engine import build_index, incremental_index, get_index, init_index
from config import INDEX_DIR

class TestEngine:
    """索引引擎测试类"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_files(self, temp_dir):
        """创建测试文件"""
        # 创建测试文件
        for i in range(5):
            file_path = os.path.join(temp_dir, f"test_{i}.txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"这是测试文档 {i}。\n" * 10)
        return temp_dir
    
    def test_init_index(self):
        """测试初始化索引"""
        # 清理旧索引
        if os.path.exists(INDEX_DIR):
            shutil.rmtree(INDEX_DIR)
        
        ix = init_index()
        assert ix is not None
        assert os.path.exists(INDEX_DIR)
    
    def test_build_index(self, sample_files):
        """测试构建索引"""
        # 清理旧索引
        if os.path.exists(INDEX_DIR):
            shutil.rmtree(INDEX_DIR)
        
        count = build_index(sample_files)
        assert count > 0
    
    def test_get_index(self):
        """测试获取索引实例"""
        ix = get_index()
        assert ix is not None
    
    def test_incremental_index(self, sample_files):
        """测试增量索引"""
        # 先构建索引
        if os.path.exists(INDEX_DIR):
            shutil.rmtree(INDEX_DIR)
        build_index(sample_files)
        
        # 运行增量索引
        result = incremental_index(sample_files)
        assert "added" in result
        assert "updated" in result
        assert "removed" in result
