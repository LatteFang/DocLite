import os
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from config import SERVER_PORT, LOG_LEVEL
from api.security import generate_csrf_token
from api.index import router as index_router
from api.kb import router as kb_router
from api.search import router as search_router
from api.file import router as file_router

logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

app = FastAPI(title="DocLite", version="0.6.0")

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(index_router)
app.include_router(kb_router)
app.include_router(search_router)
app.include_router(file_router)

# 挂载前端静态页面
static_dir = os.path.join(os.path.dirname(__file__), "web", "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def index():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/api/csrf-token")
def api_get_csrf_token():
    """获取 CSRF 令牌"""
    token = generate_csrf_token()
    return {"csrf_token": token}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=SERVER_PORT, reload=True)
