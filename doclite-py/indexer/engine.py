import os
from whoosh.index import create_in, open_dir
from whoosh.writing import AsyncWriter
from .schema import doc_schema
from config import INDEX_DIR
from scanner.walker import get_all_files
from scanner.parser import extract_text

def init_index():
    """初始化索引目录"""
    if not os.path.exists(INDEX_DIR):
        os.makedirs(INDEX_DIR)
        return create_in(INDEX_DIR, doc_schema)
    return open_dir(INDEX_DIR)

def build_index(scan_path: str):
    """全量重建索引"""
    ix = init_index()
    # 清空旧索引
    writer = AsyncWriter(ix)
    writer.mergetype = "FULL"
    writer.commit()

    writer = AsyncWriter(ix)
    files = get_all_files(scan_path)

    for file_info in files:
        content = extract_text(file_info)
        if not content:
            continue
        writer.add_document(
            path=file_info["path"],
            filename=file_info["filename"],
            content=content,
            file_type=file_info["file_type"],
            mtime=file_info["mtime"],
            size=file_info["size"]
        )
    writer.commit()
    return len(files)

def get_index():
    """获取索引实例"""
    return init_index()