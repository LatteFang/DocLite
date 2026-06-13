"""
索引 Schema 模块 - 定义 Whoosh 索引字段结构
"""

from whoosh.fields import Schema, TEXT, ID, NUMERIC

# 文档索引 Schema
# 定义了索引中每个文档的字段结构
doc_schema = Schema(
    # 文件绝对路径，作为唯一主键
    # 使用 ID 类型确保唯一性和快速查找
    path=ID(stored=True, unique=True),
    
    # 文件名，支持全文搜索
    # 使用 TEXT 类型支持分词和搜索
    filename=TEXT(stored=True),
    
    # 文件正文内容，支持全文搜索
    # 这是搜索的主要字段
    content=TEXT(stored=True),
    
    # 文件类型（如 pdf, docx, txt 等）
    # 使用 ID 类型用于精确匹配和筛选
    file_type=ID(stored=True),
    
    # 文件最后修改时间戳（Unix 时间戳）
    # 使用 NUMERIC 类型支持范围查询
    mtime=NUMERIC(stored=True),
    
    # 文件大小（字节）
    # 使用 NUMERIC 类型支持范围查询
    size=NUMERIC(stored=True)
)

# 字段名称常量
FIELD_PATH = "path"
FIELD_FILENAME = "filename"
FIELD_CONTENT = "content"
FIELD_FILE_TYPE = "file_type"
FIELD_MTIME = "mtime"
FIELD_SIZE = "size"