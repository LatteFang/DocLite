import os
import pytest
from config import Config, config, BASE_DIR, INDEX_DIR, DEFAULT_SCAN_PATH

class TestConfig:
    """配置测试类"""
    
    def test_config_initialization(self):
        """测试配置初始化"""
        assert config is not None
        assert isinstance(config, Config)
    
    def test_base_dir(self):
        """测试项目根目录"""
        assert config.base_dir is not None
        assert os.path.isabs(config.base_dir)
        assert os.path.exists(config.base_dir)
    
    def test_index_dir(self):
        """测试索引目录"""
        index_dir = config.index_dir
        assert index_dir is not None
        assert os.path.isabs(index_dir)
        assert index_dir.endswith(".doclite_index")
    
    def test_default_scan_path(self):
        """测试默认扫描路径"""
        scan_path = config.default_scan_path
        assert scan_path is not None
        assert os.path.isabs(scan_path)
    
    def test_supported_extensions(self):
        """测试支持的文件格式"""
        extensions = config.supported_extensions
        assert isinstance(extensions, set)
        assert ".pdf" in extensions
        assert ".docx" in extensions
        assert ".md" in extensions
        assert ".txt" in extensions
    
    def test_server_port(self):
        """测试服务端口"""
        port = config.server_port
        assert isinstance(port, int)
        assert 1 <= port <= 65535
    
    def test_log_level(self):
        """测试日志级别"""
        log_level = config.log_level
        assert isinstance(log_level, str)
        assert log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    
    def test_vector_store_dir(self):
        """测试向量存储目录"""
        vector_dir = config.vector_store_dir
        assert vector_dir is not None
        assert os.path.isabs(vector_dir)
        assert vector_dir.endswith(".doclite_vectors")
    
    def test_backward_compatibility(self):
        """测试向后兼容性"""
        assert BASE_DIR == config.base_dir
        assert INDEX_DIR == config.index_dir
        assert DEFAULT_SCAN_PATH == config.default_scan_path
