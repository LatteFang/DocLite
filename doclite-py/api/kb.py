import re
import logging
from fastapi import APIRouter, Query, HTTPException, Depends

from indexer.knowledge_base import KnowledgeBaseManager
from .security import verify_csrf_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/kb", tags=["knowledge_base"])

@router.get("/list")
def list_knowledge_bases():
    """列出所有知识库"""
    try:
        kb_manager = KnowledgeBaseManager()
        kbs = kb_manager.list_knowledge_bases()
        current = kb_manager.get_current_knowledge_base()
        
        return {
            "status": "ok",
            "knowledge_bases": kbs,
            "current": current["id"] if current else None
        }
    except Exception as e:
        logger.error(f"获取知识库列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取知识库列表失败: {str(e)}")

@router.post("/create")
def create_knowledge_base(
    name: str = Query(..., min_length=1, max_length=100, description="知识库名称"),
    description: str = Query("", max_length=500, description="知识库描述"),
    csrf_token: str = Depends(verify_csrf_token)
):
    """创建知识库"""
    try:
        name = name.strip()
        description = description.strip()
        
        if not re.match(r'^[\w\-\u4e00-\u9fa5]+$', name):
            raise HTTPException(status_code=400, detail="知识库名称只能包含字母、数字、中文、下划线和连字符")
        
        kb_manager = KnowledgeBaseManager()
        kb_info = kb_manager.create_knowledge_base(name, description)
        return {"status": "ok", "knowledge_base": kb_info}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建知识库失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建知识库失败: {str(e)}")

@router.post("/switch")
def switch_knowledge_base(
    kb_id: str = Query(..., description="知识库ID"),
    csrf_token: str = Depends(verify_csrf_token)
):
    """切换当前知识库"""
    try:
        kb_manager = KnowledgeBaseManager()
        success = kb_manager.set_current_knowledge_base(kb_id)
        if success:
            return {"status": "ok", "message": f"已切换到知识库: {kb_id}"}
        else:
            raise HTTPException(status_code=404, detail=f"知识库 '{kb_id}' 不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"切换知识库失败: {e}")
        raise HTTPException(status_code=500, detail=f"切换知识库失败: {str(e)}")

@router.delete("/delete")
def delete_knowledge_base(
    kb_id: str = Query(..., description="知识库ID"),
    csrf_token: str = Depends(verify_csrf_token)
):
    """删除知识库"""
    try:
        kb_manager = KnowledgeBaseManager()
        success = kb_manager.delete_knowledge_base(kb_id)
        if success:
            return {"status": "ok", "message": f"已删除知识库: {kb_id}"}
        else:
            raise HTTPException(status_code=404, detail=f"知识库 '{kb_id}' 不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除知识库失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除知识库失败: {str(e)}")
