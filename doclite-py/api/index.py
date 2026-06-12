import os
import logging
from fastapi import APIRouter, Query, HTTPException, BackgroundTasks, Depends

from config import DEFAULT_SCAN_PATH, BASE_DIR
from indexer.engine import build_index, incremental_index
from .security import validate_scan_path, verify_csrf_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/index", tags=["index"])

@router.post("/build")
def build_index_endpoint(
    path: str = DEFAULT_SCAN_PATH,
    background_tasks: BackgroundTasks = None,
    csrf_token: str = Depends(verify_csrf_token)
):
    """构建索引"""
    try:
        safe_path = validate_scan_path(path)
        
        if background_tasks:
            background_tasks.add_task(build_index, safe_path)
            return {"status": "ok", "message": "索引构建已在后台启动", "scan_path": safe_path}
        else:
            count = build_index(safe_path)
            return {"status": "ok", "scanned_files": count, "scan_path": safe_path}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"构建索引失败: {e}")
        raise HTTPException(status_code=500, detail=f"构建索引失败: {str(e)}")

@router.post("/incremental")
def incremental_index_endpoint(
    path: str = DEFAULT_SCAN_PATH,
    background_tasks: BackgroundTasks = None,
    csrf_token: str = Depends(verify_csrf_token)
):
    """增量索引"""
    try:
        safe_path = validate_scan_path(path)
        
        if background_tasks:
            background_tasks.add_task(incremental_index, safe_path)
            return {"status": "ok", "message": "增量索引已在后台启动", "scan_path": safe_path}
        else:
            result = incremental_index(safe_path)
            return {"status": "ok", "result": result, "scan_path": safe_path}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"增量索引失败: {e}")
        raise HTTPException(status_code=500, detail=f"增量索引失败: {str(e)}")
