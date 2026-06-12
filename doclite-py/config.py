import os
from typing import Set

# 项目根目录
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))

# 索引存储目录
INDEX_DIR: str = os.environ.get(
    "DOCLITE_INDEX_DIR",
    os.path.join(BASE_DIR, ".doclite_index")
)

# 默认扫描的文档目录（可在前端修改）
DEFAULT_SCAN_PATH: str = os.environ.get(
    "DOCLITE_SCAN_PATH",
    os.path.join(BASE_DIR, "sample_docs")
)

# 支持的文件格式
SUPPORTED_EXTENSIONS: Set[str] = {".pdf", ".docx", ".pptx", ".xlsx", ".md", ".txt"}

# 服务端口
SERVER_PORT: int = int(os.environ.get("DOCLITE_PORT", "8000"))

# 日志级别
LOG_LEVEL: str = os.environ.get("DOCLITE_LOG_LEVEL", "INFO")