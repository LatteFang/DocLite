import pytest
from collections import deque
import tempfile
import os

class TestDocumentChat:
    """文档对话测试类"""
    
    def test_conversation_history_deque(self):
        """测试对话历史使用 deque 管理"""
        from searcher.chat import DocumentChat
        
        # 创建一个简单的 mock retriever
        class MockRetriever:
            pass
        
        chat = DocumentChat(MockRetriever(), max_history=3)
        assert isinstance(chat.conversation_history, deque)
        assert chat.conversation_history.maxlen == 3
    
    def test_build_context_empty(self):
        """测试空历史上下文构建"""
        from searcher.chat import DocumentChat
        
        class MockRetriever:
            pass
        
        chat = DocumentChat(MockRetriever())
        context = chat._build_context_from_history()
        assert context == ""
    
    def test_conversation_history_append(self):
        """测试对话历史添加"""
        from searcher.chat import DocumentChat
        
        class MockRetriever:
            pass
        
        chat = DocumentChat(MockRetriever(), max_history=5)
        
        # 添加对话历史
        chat.conversation_history.append({
            'question': '测试问题',
            'answer': '测试回答',
            'sources': []
        })
        
        history = chat.get_conversation_history()
        assert len(history) == 1
        assert history[0]['question'] == '测试问题'
    
    def test_clear_history(self):
        """测试清空历史"""
        from searcher.chat import DocumentChat
        
        class MockRetriever:
            pass
        
        chat = DocumentChat(MockRetriever())
        chat.conversation_history.append({
            'question': '测试问题',
            'answer': '测试回答',
            'sources': []
        })
        
        chat.clear_conversation_history()
        assert len(chat.conversation_history) == 0
    
    def test_max_history_limit(self):
        """测试最大历史限制"""
        from searcher.chat import DocumentChat
        
        class MockRetriever:
            pass
        
        chat = DocumentChat(MockRetriever(), max_history=3)
        
        # 添加超过限制的历史
        for i in range(5):
            chat.conversation_history.append({
                'question': f'问题{i}',
                'answer': f'回答{i}',
                'sources': []
            })
        
        # 应该只保留最新的3条
        assert len(chat.conversation_history) == 3
        assert chat.conversation_history[0]['question'] == '问题2'
