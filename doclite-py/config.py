"""
DocLite 配置模块
"""

import os
from typing import Set, Optional
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    """DocLite 配置类"""
    
    # 项目根目录
    base_dir: str = os.path.dirname(os.path.abspath(__file__))
    
    @property
    def index_dir(self) -> str:
        """索引存储目录"""
        return os.environ.get(
            "DOCLITE_INDEX_DIR",
            os.path.join(self.base_dir, ".doclite_index")
        )
    
    @property
    def default_scan_path(self) -> str:
        """默认扫描的文档目录"""
        return os.environ.get(
            "DOCLITE_SCAN_PATH",
            os.path.join(self.base_dir, "sample_docs")
        )
    
    @property
    def supported_extensions(self) -> Set[str]:
        """支持的文件格式"""
        return {".pdf", ".docx", ".pptx", ".xlsx", ".md", ".txt",
                ".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp", ".gif"}
    
    @property
    def server_port(self) -> int:
        """服务端口"""
        return int(os.environ.get("DOCLITE_PORT", "8000"))
    
    @property
    def log_level(self) -> str:
        """日志级别"""
        return os.environ.get("DOCLITE_LOG_LEVEL", "INFO")
    
    @property
    def vector_store_dir(self) -> str:
        """向量存储目录"""
        return os.path.join(self.base_dir, ".doclite_vectors")

# 全局配置实例
config = Config()

# 为了向后兼容，保留原始变量名
BASE_DIR = config.base_dir
INDEX_DIR = config.index_dir
DEFAULT_SCAN_PATH = config.default_scan_path
SUPPORTED_EXTENSIONS = config.supported_extensions
SERVER_PORT = config.server_port
LOG_LEVEL = config.log_level