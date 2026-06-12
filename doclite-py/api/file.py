import os
import sys
import subprocess
import logging
from fastapi import APIRouter, Query, HTTPException, Depends

from config import BASE_DIR
from .security import verify_csrf_token

logger = logging.getLogger(__name__)

router = APIRouter(tags=["file"])

def validate_file_path(file_path: str) -> str:
    """验证文件路径安全性"""
    abs_path = os.path.abspath(file_path)
    
    if not os.path.exists(abs_path):
        raise HTTPException(status_code=404, detail=f"文件不存在: {file_path}")
    
    if not os.path.isfile(abs_path):
        raise HTTPException(status_code=400, detail=f"路径不是文件: {file_path}")
    
    allowed_prefixes = [
        os.path.abspath(BASE_DIR),
        os.path.abspath(os.path.join(BASE_DIR, "sample_docs")),
    ]
    
    is_allowed = any(abs_path.startswith(prefix) for prefix in allowed_prefixes)
    if not is_allowed:
        logger.warning(f"拒绝访问文件: {file_path} (不在允许目录内)")
        raise HTTPException(status_code=403, detail="访问被拒绝：文件不在允许目录内")
    
    return abs_path

@router.post("/api/open")
def open_file_endpoint(
    file_path: str = Query(..., description="文件路径"),
    csrf_token: str = Depends(verify_csrf_token)
):
    """打开原文件"""
    try:
        abs_path = validate_file_path(file_path)
        
        if sys.platform == 'darwin':
            subprocess.run(['open', abs_path], check=True)
        elif sys.platform == 'win32':
            os.startfile(abs_path)
        else:
            subprocess.run(['xdg-open', abs_path], check=True)
        
        return {"status": "ok", "message": f"已打开文件: {os.path.basename(abs_path)}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"打开文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"打开文件失败: {str(e)}")

@router.get("/api/preview")
def preview_file_endpoint(file_path: str = Query(..., description="文件路径")):
    """文档预览"""
    try:
        abs_path = validate_file_path(file_path)
        
        ext = os.path.splitext(abs_path)[1].lower()
        
        if ext == '.md':
            with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return {"type": "markdown", "content": content}
        elif ext == '.txt':
            with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return {"type": "text", "content": content}
        elif ext == '.pdf':
            from scanner.parser import _extract_pdf
            content = _extract_pdf(abs_path)
            return {"type": "pdf", "content": content}
        elif ext == '.docx':
            from scanner.parser import _extract_docx
            content = _extract_docx(abs_path)
            return {"type": "docx", "content": content}
        else:
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {ext}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"预览文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"预览文件失败: {str(e)}")
