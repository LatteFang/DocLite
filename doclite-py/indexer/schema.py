from whoosh.fields import Schema, TEXT, ID, DATETIME, NUMERIC

# 定义索引字段
doc_schema = Schema(
    path=ID(stored=True, unique=True),    # 文件绝对路径，唯一主键
    filename=TEXT(stored=True),           # 文件名
    content=TEXT(stored=True),            # 文件正文
    file_type=ID(stored=True),            # 文件类型
    mtime=NUMERIC(stored=True),           # 修改时间戳
    size=NUMERIC(stored=True)             # 文件大小（字节）
)