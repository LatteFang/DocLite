import os
import logging
from typing import List, Dict, Set
from config import SUPPORTED_EXTENSIONS

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.webp', '.gif'}

FILE_TYPE_MAP = {
    '.pdf': 'pdf',
    '.docx': 'docx',
    '.pptx': 'pptx',
    '.xlsx': 'xlsx',
    '.md': 'md',
    '.txt': 'txt',
    '.png': 'png',
    '.jpg': 'jpg',
    '.jpeg': 'jpeg',
    '.bmp': 'bmp',
    '.tiff': 'tiff',
    '.tif': 'tiff',
    '.webp': 'webp',
    '.gif': 'gif',
}

# 跳过的目录名
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".idea", ".vscode"}

def get_all_files(root_path: str, max_file_size: int = 100 * 1024 * 1024) -> List[Dict]:
    """
    遍历目录，返回所有支持格式的文件路径列表
    
    Args:
        root_path: 根目录路径
        max_file_size: 最大文件大小（字节），默认 100MB
    
    Returns:
        文件信息列表
    """
    file_list = []
    
    if not os.path.exists(root_path):
        logger.warning(f"目录不存在: {root_path}")
        return file_list
    
    if not os.path.isdir(root_path):
        logger.warning(f"路径不是目录: {root_path}")
        return file_list
    
    skipped_count = 0
    
    for root, dirs, files in os.walk(root_path):
        # 跳过隐藏目录和不需要索引的目录
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in SKIP_DIRS]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in SUPPORTED_EXTENSIONS:
                continue
            
            full_path = os.path.join(root, file)
            
            try:
                stat_info = os.stat(full_path)
                
                # 跳过空文件和过大的文件
                if stat_info.st_size == 0 or stat_info.st_size > max_file_size:
                    skipped_count += 1
                    continue
                
                file_list.append({
                    "path": full_path,
                    "filename": file,
                    "file_type": ext.lstrip("."),
                    "mtime": stat_info.st_mtime,
                    "size": stat_info.st_size
                })
            except OSError as e:
                logger.warning(f"无法访问文件 {full_path}: {e}")
                skipped_count += 1
    
    if skipped_count > 0:
        logger.info(f"跳过了 {skipped_count} 个文件")
    
    return file_list

def get_file_count(root_path: str) -> int:
    """获取目录下支持格式的文件数量"""
    return len(get_all_files(root_path))
