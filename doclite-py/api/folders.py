"""
文件夹管理模块 - 浏览和管理扫描文件夹
"""

import os
import sys
import json
import logging
from typing import List, Dict
from fastapi import APIRouter, Query, HTTPException, Depends

from config import BASE_DIR
from .security import verify_csrf_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/folders", tags=["folders"])

# 文件夹配置文件路径
FOLDERS_CONFIG_FILE = os.path.join(BASE_DIR, ".doclite_folders.json")

def load_folders() -> List[str]:
    """加载已保存的文件夹列表"""
    if not os.path.exists(FOLDERS_CONFIG_FILE):
        return []
    
    try:
        with open(FOLDERS_CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("folders", [])
    except Exception as e:
        logger.error(f"加载文件夹配置失败: {e}")
        return []

def save_folders(folders: List[str]):
    """保存文件夹列表"""
    try:
        with open(FOLDERS_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({"folders": folders}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存文件夹配置失败: {e}")
        raise

@router.get("/list")
def list_folders():
    """获取已保存的文件夹列表"""
    folders = load_folders()
    return {"status": "ok", "folders": folders}

@router.post("/add")
def add_folder(
    path: str = Query(..., description="文件夹路径"),
    csrf_token: str = Depends(verify_csrf_token)
):
    """添加文件夹"""
    # 验证路径
    abs_path = os.path.abspath(path)
    
    if not os.path.exists(abs_path):
        raise HTTPException(status_code=400, detail=f"路径不存在: {path}")
    
    if not os.path.isdir(abs_path):
        raise HTTPException(status_code=400, detail=f"路径不是目录: {path}")
    
    # 加载现有列表
    folders = load_folders()
    
    # 检查是否已存在
    if abs_path in folders:
        raise HTTPException(status_code=400, detail="文件夹已存在")
    
    # 添加到列表
    folders.append(abs_path)
    save_folders(folders)
    
    return {"status": "ok", "folders": folders}

@router.post("/remove")
def remove_folder(
    path: str = Query(..., description="文件夹路径"),
    csrf_token: str = Depends(verify_csrf_token)
):
    """移除文件夹"""
    abs_path = os.path.abspath(path)
    
    # 加载现有列表
    folders = load_folders()
    
    # 检查是否存在
    if abs_path not in folders:
        raise HTTPException(status_code=404, detail="文件夹不存在")
    
    # 从列表中移除
    folders.remove(abs_path)
    save_folders(folders)
    
    return {"status": "ok", "folders": folders}

def get_user_home_dir() -> str:
    """获取用户主目录"""
    import sys
    if sys.platform == 'darwin' or sys.platform.startswith('linux'):
        # macOS 和 Linux: 限制在 /Users 目录下
        return "/Users"
    else:
        # Windows: 使用用户主目录
        return os.path.expanduser("~")

def is_path_allowed(path: str) -> bool:
    """检查路径是否在允许的范围内"""
    import sys
    abs_path = os.path.abspath(path)
    
    if sys.platform == 'darwin' or sys.platform.startswith('linux'):
        # macOS 和 Linux: 只允许 /Users 目录及其子目录
        return abs_path.startswith('/Users')
    else:
        # Windows: 允许所有路径（或可以添加其他限制）
        return True

@router.get("/browse")
def browse_directory(
    path: str = Query("/", description="要浏览的目录路径")
):
    """浏览目录内容"""
    abs_path = os.path.abspath(path)
    
    # 检查路径是否在允许范围内
    if not is_path_allowed(abs_path):
        raise HTTPException(status_code=403, detail="访问被拒绝：不允许访问系统目录")
    
    if not os.path.exists(abs_path):
        raise HTTPException(status_code=400, detail=f"路径不存在: {path}")
    
    if not os.path.isdir(abs_path):
        raise HTTPException(status_code=400, detail=f"路径不是目录: {path}")
    
    try:
        items = []
        for item in os.listdir(abs_path):
            item_path = os.path.join(abs_path, item)
            is_dir = os.path.isdir(item_path)
            
            # 跳过隐藏文件/目录
            if item.startswith('.'):
                continue
            
            # 跳过系统目录
            if sys.platform == 'darwin' or sys.platform.startswith('linux'):
                # 在 /Users 目录下，跳过系统用户目录
                if abs_path == '/Users' and item in ('Shared', 'Guest', '.localized'):
                    continue
                # 跳过其他系统目录
                if item in ('System', 'Library', 'Applications', 'bin', 'sbin', 'usr', 'var', 'etc', 'tmp', 'opt'):
                    continue
            
            items.append({
                "name": item,
                "path": item_path,
                "is_dir": is_dir
            })
        
        # 排序：目录在前，文件在后
        items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
        
        # 计算父目录路径
        parent_path = os.path.dirname(abs_path)
        if not is_path_allowed(parent_path):
            parent_path = abs_path  # 如果父目录不允许，则不返回
        
        return {
            "status": "ok",
            "current_path": abs_path,
            "parent_path": parent_path,
            "items": items
        }
    except Exception as e:
        logger.error(f"浏览目录失败: {e}")
        raise HTTPException(status_code=500, detail=f"浏览目录失败: {str(e)}")
