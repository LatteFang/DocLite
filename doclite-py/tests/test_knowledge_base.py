import os
import pytest
import tempfile
from indexer.knowledge_base import KnowledgeBaseManager

class TestKnowledgeBaseManager:
    """知识库管理器测试类"""
    
    @pytest.fixture
    def kb_manager(self):
        """创建测试知识库管理器"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = KnowledgeBaseManager(temp_dir)
            yield manager
    
    def test_create_knowledge_base(self, kb_manager):
        """测试创建知识库"""
        kb_info = kb_manager.create_knowledge_base("测试知识库", "这是测试描述")
        
        assert kb_info['name'] == "测试知识库"
        assert kb_info['description'] == "这是测试描述"
        assert 'id' in kb_info
        assert 'vector_dir' in kb_info
    
    def test_list_knowledge_bases(self, kb_manager):
        """测试列出知识库"""
        # 创建多个知识库
        kb_manager.create_knowledge_base("知识库1")
        kb_manager.create_knowledge_base("知识库2")
        
        kbs = kb_manager.list_knowledge_bases()
        
        assert len(kbs) == 2
        assert kbs[0]['name'] == "知识库1"
        assert kbs[1]['name'] == "知识库2"
    
    def test_set_current_knowledge_base(self, kb_manager):
        """测试设置当前知识库"""
        kb_manager.create_knowledge_base("知识库1")
        kb_manager.create_knowledge_base("知识库2")
        
        # 设置当前知识库
        success = kb_manager.set_current_knowledge_base("知识库2")
        assert success is True
        
        current = kb_manager.get_current_knowledge_base()
        assert current['name'] == "知识库2"
    
    def test_delete_knowledge_base(self, kb_manager):
        """测试删除知识库"""
        kb_manager.create_knowledge_base("待删除知识库")
        
        success = kb_manager.delete_knowledge_base("待删除知识库")
        assert success is True
        
        kbs = kb_manager.list_knowledge_bases()
        assert len(kbs) == 0
    
    def test_create_duplicate_knowledge_base(self, kb_manager):
        """测试创建重复知识库"""
        kb_manager.create_knowledge_base("重复知识库")
        
        with pytest.raises(ValueError, match="已存在"):
            kb_manager.create_knowledge_base("重复知识库")
