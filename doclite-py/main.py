import os
import logging
from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from config import SERVER_PORT, DEFAULT_SCAN_PATH, BASE_DIR, LOG_LEVEL
from indexer.engine import build_index, incremental_index
from searcher.service import search_documents

logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

app = FastAPI(title="DocLite")

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载前端静态页面
static_dir = os.path.join(os.path.dirname(__file__), "web", "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def index():
    return FileResponse(os.path.join(static_dir, "index.html"))

def validate_scan_path(path: str) -> str:
    """验证扫描路径安全性，防止路径遍历攻击"""
    # 转换为绝对路径
    abs_path = os.path.abspath(path)
    
    # 检查路径是否存在
    if not os.path.exists(abs_path):
        raise HTTPException(status_code=400, detail=f"路径不存在: {path}")
    
    # 检查是否是目录
    if not os.path.isdir(abs_path):
        raise HTTPException(status_code=400, detail=f"路径不是目录: {path}")
    
    # 安全检查：允许的路径前缀（可以扩展）
    allowed_prefixes = [
        os.path.abspath(BASE_DIR),
        os.path.abspath(os.path.join(BASE_DIR, "sample_docs")),
    ]
    
    # 检查路径是否在允许的目录下
    is_allowed = any(abs_path.startswith(prefix) for prefix in allowed_prefixes)
    if not is_allowed:
        logger.warning(f"拒绝访问路径: {path} (不在允许目录内)")
        raise HTTPException(status_code=403, detail="访问被拒绝：路径不在允许目录内")
    
    return abs_path

# 构建索引接口
@app.post("/api/index/build")
def api_build_index(path: str = DEFAULT_SCAN_PATH, background_tasks: BackgroundTasks = None):
    try:
        safe_path = validate_scan_path(path)
        
        # 在后台执行索引构建
        if background_tasks:
            background_tasks.add_task(build_index, safe_path)
            return {"status": "ok", "message": "索引构建已在后台启动", "scan_path": safe_path}
        else:
            # 如果没有 BackgroundTasks，同步执行
            count = build_index(safe_path)
            return {"status": "ok", "scanned_files": count, "scan_path": safe_path}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"构建索引失败: {e}")
        raise HTTPException(status_code=500, detail=f"构建索引失败: {str(e)}")

# 增量索引接口
@app.post("/api/index/incremental")
def api_incremental_index(path: str = DEFAULT_SCAN_PATH, background_tasks: BackgroundTasks = None):
    try:
        safe_path = validate_scan_path(path)
        
        # 在后台执行增量索引
        if background_tasks:
            background_tasks.add_task(incremental_index, safe_path)
            return {"status": "ok", "message": "增量索引已在后台启动", "scan_path": safe_path}
        else:
            # 如果没有 BackgroundTasks，同步执行
            result = incremental_index(safe_path)
            return {"status": "ok", "result": result, "scan_path": safe_path}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"增量索引失败: {e}")
        raise HTTPException(status_code=500, detail=f"增量索引失败: {str(e)}")

# 搜索接口
@app.get("/api/search")
def api_search(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=5, le=100),
    file_type: str = Query(None, description="文件类型筛选：pdf, docx, md, txt"),
    start_time: float = Query(None, description="开始时间戳（秒）"),
    end_time: float = Query(None, description="结束时间戳（秒）")
):
    return search_documents(q, page, per_page, file_type, start_time, end_time)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=SERVER_PORT, reload=True)