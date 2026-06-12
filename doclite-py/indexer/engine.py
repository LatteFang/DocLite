import os
import shutil
import logging
from whoosh.index import create_in, open_dir
from whoosh.writing import AsyncWriter
from .schema import doc_schema
from config import INDEX_DIR
from scanner.walker import get_all_files
from scanner.parser import extract_text

logger = logging.getLogger(__name__)

def init_index():
    """初始化索引目录"""
    if not os.path.exists(INDEX_DIR):
        os.makedirs(INDEX_DIR)
        return create_in(INDEX_DIR, doc_schema)
    return open_dir(INDEX_DIR)

def build_index(scan_path: str):
    """全量重建索引"""
    # 清空旧索引目录
    if os.path.exists(INDEX_DIR):
        logger.info(f"清空旧索引目录: {INDEX_DIR}")
        shutil.rmtree(INDEX_DIR)
    
    # 创建新的索引目录
    os.makedirs(INDEX_DIR)
    ix = create_in(INDEX_DIR, doc_schema)
    
    files = get_all_files(scan_path)
    indexed_count = 0
    
    with AsyncWriter(ix) as writer:
        for file_info in files:
            try:
                content = extract_text(file_info)
                if not content:
                    logger.warning(f"无法提取内容: {file_info['path']}")
                    continue
                writer.add_document(
                    path=file_info["path"],
                    filename=file_info["filename"],
                    content=content,
                    file_type=file_info["file_type"],
                    mtime=file_info["mtime"],
                    size=file_info["size"]
                )
                indexed_count += 1
            except Exception as e:
                logger.error(f"索引文件失败 {file_info['path']}: {e}")
    
    logger.info(f"索引构建完成，成功索引 {indexed_count}/{len(files)} 个文件")
    return indexed_count

def get_index():
    """获取索引实例"""
    return init_index()

def incremental_index(scan_path: str):
    """增量索引：只更新新增或修改的文件"""
    ix = init_index()
    
    # 获取当前索引中的所有文件路径和修改时间
    indexed_files = {}
    with ix.searcher() as searcher:
        # 搜索所有文档（使用空查询）
        from whoosh.qparser import QueryParser
        parser = QueryParser("content", ix.schema)
        query = parser.parse("*")  # 匹配所有文档
        
        for docnum in range(searcher.doc_count_all()):
            try:
                doc = searcher.stored_fields(docnum)
                if doc:
                    indexed_files[doc["path"]] = doc["mtime"]
            except:
                continue
    
    # 获取文件系统中的所有文件
    fs_files = get_all_files(scan_path)
    fs_file_dict = {f["path"]: f for f in fs_files}
    
    # 统计信息
    added = 0
    updated = 0
    removed = 0
    
    with AsyncWriter(ix) as writer:
        # 1. 处理新增和修改的文件
        for file_info in fs_files:
            path = file_info["path"]
            mtime = file_info["mtime"]
            
            if path not in indexed_files:
                # 新文件：添加到索引
                try:
                    content = extract_text(file_info)
                    if not content:
                        logger.warning(f"无法提取内容: {path}")
                        continue
                    writer.add_document(
                        path=path,
                        filename=file_info["filename"],
                        content=content,
                        file_type=file_info["file_type"],
                        mtime=mtime,
                        size=file_info["size"]
                    )
                    added += 1
                except Exception as e:
                    logger.error(f"索引新文件失败 {path}: {e}")
            elif mtime > indexed_files[path]:
                # 文件已修改：更新索引
                try:
                    content = extract_text(file_info)
                    if not content:
                        logger.warning(f"无法提取内容: {path}")
                        continue
                    writer.update_document(
                        path=path,
                        filename=file_info["filename"],
                        content=content,
                        file_type=file_info["file_type"],
                        mtime=mtime,
                        size=file_info["size"]
                    )
                    updated += 1
                except Exception as e:
                    logger.error(f"更新索引失败 {path}: {e}")
        
        # 2. 处理删除的文件
        for path in indexed_files:
            if path not in fs_file_dict:
                try:
                    writer.delete_by_term("path", path)
                    removed += 1
                except Exception as e:
                    logger.error(f"删除索引失败 {path}: {e}")
    
    total = added + updated + removed
    logger.info(f"增量索引完成：新增 {added}，更新 {updated}，删除 {removed}")
    return {"added": added, "updated": updated, "removed": removed, "total": total}