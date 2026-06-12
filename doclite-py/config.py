import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 索引存储目录
INDEX_DIR = os.path.join(BASE_DIR, ".doclite_index")

# 默认扫描的文档目录（可在前端修改）
DEFAULT_SCAN_PATH = os.path.join(BASE_DIR, "sample_docs")

# 支持的文件格式
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".md", ".txt"}

# 服务端口
SERVER_PORT = 8000