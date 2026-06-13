import os
import logging
from typing import List
from fastapi import APIRouter, Query, HTTPException, BackgroundTasks, Depends

from config import DEFAULT_SCAN_PATH, BASE_DIR
from indexer.engine import build_index, incremental_index
from .security import validate_scan_path, verify_csrf_token
from .folders import load_folders

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/index", tags=["index"])

@router.post("/build")
def build_index_endpoint(
    path: str = None,
    background_tasks: BackgroundTasks = None,
    csrf_token: str = Depends(verify_csrf_token)
):
    """构建索引"""
    try:
        # 如果没有指定路径，使用已保存的文件夹列表
        if path:
            paths = [validate_scan_path(path)]
        else:
            saved_folders = load_folders()
            if not saved_folders:
                raise HTTPException(status_code=400, detail="请先选择要索引的文件夹")
            paths = [validate_scan_path(p) for p in saved_folders]
        
        def build_index_for_paths(paths: List[str]):
            """为多个路径构建索引"""
            total_count = 0
            for p in paths:
                try:
                    count = build_index(p)
                    total_count += count
                except Exception as e:
                    logger.error(f"索引路径 {p} 失败: {e}")
            return total_count
        
        if background_tasks:
            background_tasks.add_task(build_index_for_paths, paths)
            return {"status": "ok", "message": "索引构建已在后台启动", "scan_paths": paths}
        else:
            total_count = 0
            for p in paths:
                count = build_index(p)
                total_count += count
            return {"status": "ok", "scanned_files": total_count, "scan_paths": paths}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"构建索引失败: {e}")
        raise HTTPException(status_code=500, detail=f"构建索引失败: {str(e)}")

@router.post("/incremental")
def incremental_index_endpoint(
    path: str = None,
    background_tasks: BackgroundTasks = None,
    csrf_token: str = Depends(verify_csrf_token)
):
    """增量索引"""
    try:
        # 如果没有指定路径，使用已保存的文件夹列表
        if path:
            paths = [validate_scan_path(path)]
        else:
            saved_folders = load_folders()
            if not saved_folders:
                raise HTTPException(status_code=400, detail="请先选择要索引的文件夹")
            paths = [validate_scan_path(p) for p in saved_folders]
        
        def incremental_index_for_paths(paths: List[str]):
            """为多个路径执行增量索引"""
            results = []
            for p in paths:
                try:
                    result = incremental_index(p)
                    results.append(result)
                except Exception as e:
                    logger.error(f"增量索引路径 {p} 失败: {e}")
            return results
        
        if background_tasks:
            background_tasks.add_task(incremental_index_for_paths, paths)
            return {"status": "ok", "message": "增量索引已在后台启动", "scan_paths": paths}
        else:
            results = []
            for p in paths:
                result = incremental_index(p)
                results.append(result)
            return {"status": "ok", "results": results, "scan_paths": paths}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"增量索引失败: {e}")
        raise HTTPException(status_code=500, detail=f"增量索引失败: {str(e)}")
