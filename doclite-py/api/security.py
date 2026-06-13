import os
import secrets
import logging
from typing import Optional
from fastapi import HTTPException, Header

from config import BASE_DIR

logger = logging.getLogger(__name__)

# CSRF 令牌存储
csrf_tokens = set()

def generate_csrf_token() -> str:
    """生成 CSRF 令牌"""
    token = secrets.token_hex(32)
    csrf_tokens.add(token)
    if len(csrf_tokens) > 1000:
        csrf_tokens.clear()
    return token

def validate_csrf_token(token: str) -> bool:
    """验证 CSRF 令牌"""
    if token in csrf_tokens:
        csrf_tokens.remove(token)
        return True
    return False

def verify_csrf_token(x_csrf_token: Optional[str] = Header(None)):
    """验证请求中的 CSRF 令牌"""
    if not x_csrf_token:
        raise HTTPException(status_code=403, detail="缺少 CSRF 令牌")
    if not validate_csrf_token(x_csrf_token):
        raise HTTPException(status_code=403, detail="CSRF 令牌无效或已过期")

def validate_scan_path(path: str) -> str:
    """验证扫描路径安全性"""
    abs_path = os.path.abspath(path)
    
    if not os.path.exists(abs_path):
        raise HTTPException(status_code=400, detail=f"路径不存在: {path}")
    
    if not os.path.isdir(abs_path):
        raise HTTPException(status_code=400, detail=f"路径不是目录: {path}")
    
    allowed_prefixes = [
        os.path.abspath(BASE_DIR),
        os.path.abspath(os.path.join(BASE_DIR, "sample_docs")),
        os.path.expanduser("~"),  # 允许用户主目录下的所有路径
    ]
    
    is_allowed = any(abs_path.startswith(prefix) for prefix in allowed_prefixes)
    if not is_allowed:
        logger.warning(f"拒绝访问路径: {path} (不在允许目录内)")
        raise HTTPException(status_code=403, detail="访问被拒绝：路径不在允许目录内")
    
    return abs_path
