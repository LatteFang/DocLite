"""
DocLite - 极简本地离线文档全文检索工具
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config import SERVER_PORT, LOG_LEVEL, BASE_DIR
from api.security import generate_csrf_token
from api import index_router, kb_router, search_router, file_router
from api.folders import router as folders_router
from api.settings import router as settings_router

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 应用生命周期
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("DocLite 启动中...")
    logger.info(f"项目根目录: {BASE_DIR}")
    logger.info(f"服务端口: {SERVER_PORT}")
    yield
    logger.info("DocLite 关闭中...")

# 创建 FastAPI 应用
app = FastAPI(
    title="DocLite",
    description="极简本地离线文档全文检索工具",
    version="0.6.0",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(index_router)
app.include_router(kb_router)
app.include_router(search_router)
app.include_router(file_router)
app.include_router(folders_router)
app.include_router(settings_router)

# 挂载前端静态页面
static_dir = os.path.join(os.path.dirname(__file__), "web", "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误，请稍后重试"}
    )

@app.get("/", response_class=FileResponse)
async def index():
    """首页"""
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": "0.6.0"}

@app.get("/api/csrf-token")
async def api_get_csrf_token():
    """获取 CSRF 令牌"""
    token = generate_csrf_token()
    return {"csrf_token": token}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=SERVER_PORT,
        reload=True,
        log_level=LOG_LEVEL.lower()
    )
