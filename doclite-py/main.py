import os
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from config import SERVER_PORT, DEFAULT_SCAN_PATH
from indexer.engine import build_index
from searcher.service import search_documents

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

# 构建索引接口
@app.post("/api/index/build")
def api_build_index(path: str = DEFAULT_SCAN_PATH):
    count = build_index(path)
    return {"status": "ok", "scanned_files": count, "scan_path": path}

# 搜索接口
@app.get("/api/search")
def api_search(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=5, le=100)
):
    return search_documents(q, page, per_page)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=SERVER_PORT, reload=True)