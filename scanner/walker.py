import os
from config import SUPPORTED_EXTENSIONS

def get_all_files(root_path: str):
    """遍历目录，返回所有支持格式的文件路径列表"""
    file_list = []
    if not os.path.exists(root_path):
        return file_list

    for root, _, files in os.walk(root_path):
        # 跳过隐藏目录
        if os.path.basename(root).startswith("."):
            continue
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                full_path = os.path.join(root, file)
                file_list.append({
                    "path": full_path,
                    "filename": file,
                    "file_type": ext.lstrip("."),
                    "mtime": os.path.getmtime(full_path),
                    "size": os.path.getsize(full_path)
                })
    return file_list