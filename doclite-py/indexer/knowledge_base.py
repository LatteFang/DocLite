import os
import json
import logging
from typing import List, Dict, Optional
from config import BASE_DIR

logger = logging.getLogger(__name__)

class KnowledgeBaseManager:
    """知识库管理器"""
    
    def __init__(self, storage_dir: str = None):
        """
        初始化知识库管理器
        
        Args:
            storage_dir: 存储目录
        """
        if storage_dir is None:
            storage_dir = os.path.join(BASE_DIR, ".doclite_kb")
        
        self.storage_dir = storage_dir
        self.config_file = os.path.join(storage_dir, "config.json")
        
        # 确保存储目录存在
        os.makedirs(storage_dir, exist_ok=True)
        
        # 加载配置
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载配置失败: {e}")
        
        return {"knowledge_bases": {}, "current": None}
    
    def _save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
    
    def create_knowledge_base(self, name: str, description: str = "") -> Dict:
        """
        创建知识库
        
        Args:
            name: 知识库名称
            description: 知识库描述
        
        Returns:
            创建的知识库信息
        """
        if name in self.config["knowledge_bases"]:
            raise ValueError(f"知识库 '{name}' 已存在")
        
        kb_id = name.lower().replace(" ", "_")
        kb_dir = os.path.join(self.storage_dir, kb_id)
        
        kb_info = {
            "id": kb_id,
            "name": name,
            "description": description,
            "created_at": __import__('time').time(),
            "vector_dir": kb_dir,
            "document_count": 0
        }
        
        self.config["knowledge_bases"][kb_id] = kb_info
        
        # 如果是第一个知识库，设为当前
        if len(self.config["knowledge_bases"]) == 1:
            self.config["current"] = kb_id
        
        self._save_config()
        
        # 创建知识库目录
        os.makedirs(kb_dir, exist_ok=True)
        
        logger.info(f"创建知识库: {name}")
        return kb_info
    
    def list_knowledge_bases(self) -> List[Dict]:
        """列出所有知识库"""
        return list(self.config["knowledge_bases"].values())
    
    def get_current_knowledge_base(self) -> Optional[Dict]:
        """获取当前知识库"""
        current_id = self.config.get("current")
        if current_id and current_id in self.config["knowledge_bases"]:
            return self.config["knowledge_bases"][current_id]
        return None
    
    def set_current_knowledge_base(self, kb_id: str) -> bool:
        """
        设置当前知识库
        
        Args:
            kb_id: 知识库ID
        
        Returns:
            是否设置成功
        """
        if kb_id not in self.config["knowledge_bases"]:
            return False
        
        self.config["current"] = kb_id
        self._save_config()
        
        logger.info(f"切换到知识库: {kb_id}")
        return True
    
    def delete_knowledge_base(self, kb_id: str) -> bool:
        """
        删除知识库
        
        Args:
            kb_id: 知识库ID
        
        Returns:
            是否删除成功
        """
        if kb_id not in self.config["knowledge_bases"]:
            return False
        
        # 删除知识库目录
        kb_info = self.config["knowledge_bases"][kb_id]
        kb_dir = kb_info.get("vector_dir")
        if kb_dir and os.path.exists(kb_dir):
            import shutil
            shutil.rmtree(kb_dir)
        
        # 删除配置
        del self.config["knowledge_bases"][kb_id]
        
        # 如果删除的是当前知识库，重置
        if self.config["current"] == kb_id:
            self.config["current"] = None
        
        self._save_config()
        
        logger.info(f"删除知识库: {kb_id}")
        return True
    
    def get_knowledge_base_vector_dir(self, kb_id: str = None) -> str:
        """
        获取知识库的向量存储目录
        
        Args:
            kb_id: 知识库ID，如果为None则使用当前知识库
        
        Returns:
            向量存储目录路径
        """
        if kb_id is None:
            kb_info = self.get_current_knowledge_base()
            if kb_info:
                return kb_info.get("vector_dir")
            # 如果没有当前知识库，使用默认目录
            return os.path.join(BASE_DIR, ".doclite_vectors")
        
        if kb_id in self.config["knowledge_bases"]:
            return self.config["knowledge_bases"][kb_id].get("vector_dir")
        
        return os.path.join(BASE_DIR, ".doclite_vectors")
