import os
import logging
from fastapi import APIRouter, Query, HTTPException, Depends

from config import DEFAULT_SCAN_PATH, BASE_DIR
from searcher.service import search_documents
from searcher.retriever import DocumentRetriever
from searcher.chat import DocumentChat
from .security import validate_scan_path, verify_csrf_token

logger = logging.getLogger(__name__)

router = APIRouter(tags=["search"])

@router.get("/api/search")
def search_endpoint(
    q: str = Query(..., min_length=1, max_length=500, description="搜索关键词"),
    page: int = Query(1, ge=1, le=1000, description="页码"),
    per_page: int = Query(20, ge=5, le=100, description="每页结果数"),
    file_type: str = Query(None, description="文件类型筛选"),
    start_time: float = Query(None, description="开始时间戳"),
    end_time: float = Query(None, description="结束时间戳")
):
    """搜索文档"""
    q = q.strip()
    
    if file_type and file_type not in ['pdf', 'docx', 'pptx', 'xlsx', 'md', 'txt']:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file_type}")
    
    if start_time is not None and end_time is not None:
        if start_time > end_time:
            raise HTTPException(status_code=400, detail="开始时间不能大于结束时间")
    
    return search_documents(q, page, per_page, file_type, start_time, end_time)

@router.post("/api/chat")
def chat_endpoint(
    question: str = Query(..., min_length=1, max_length=1000, description="用户问题"),
    top_k: int = Query(5, ge=1, le=20, description="检索的文档块数量"),
    path: str = DEFAULT_SCAN_PATH,
    csrf_token: str = Depends(verify_csrf_token)
):
    """文档问答"""
    try:
        question = question.strip()
        safe_path = validate_scan_path(path)
        
        vector_store_dir = os.path.join(BASE_DIR, ".doclite_vectors")
        retriever = DocumentRetriever(vector_store_dir)
        chat = DocumentChat(retriever)
        
        result = chat.answer_question(question, top_k)
        
        return {
            "status": "ok",
            "question": question,
            "answer": result["answer"],
            "sources": result["sources"],
            "confidence": result["confidence"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"对话失败: {e}")
        raise HTTPException(status_code=500, detail=f"对话失败: {str(e)}")

@router.post("/api/rag/index")
def rag_index_endpoint(
    path: str = DEFAULT_SCAN_PATH,
    background_tasks: BackgroundTasks = None,
    csrf_token: str = Depends(verify_csrf_token)
):
    """RAG 索引"""
    try:
        safe_path = validate_scan_path(path)
        
        def index_documents_for_rag(scan_path):
            from scanner.walker import get_all_files
            from scanner.parser import extract_text
            
            vector_store_dir = os.path.join(BASE_DIR, ".doclite_vectors")
            retriever = DocumentRetriever(vector_store_dir)
            
            files = get_all_files(scan_path)
            for file_info in files:
                try:
                    content = extract_text(file_info)
                    if content:
                        retriever.index_document(file_info, content)
                except Exception as e:
                    logger.error(f"RAG 索引文档失败 {file_info['path']}: {e}")
        
        if background_tasks:
            background_tasks.add_task(index_documents_for_rag, safe_path)
            return {"status": "ok", "message": "RAG 索引已在后台启动", "scan_path": safe_path}
        else:
            index_documents_for_rag(safe_path)
            return {"status": "ok", "message": "RAG 索引完成", "scan_path": safe_path}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RAG 索引失败: {e}")
        raise HTTPException(status_code=500, detail=f"RAG 索引失败: {str(e)}")
