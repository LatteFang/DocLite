import os
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestAPI:
    """API 测试类"""
    
    def test_index_page(self):
        """测试首页"""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_csrf_token(self):
        """测试获取 CSRF 令牌"""
        response = client.get("/api/csrf-token")
        assert response.status_code == 200
        data = response.json()
        assert 'csrf_token' in data
    
    def test_search_empty(self):
        """测试空搜索"""
        response = client.get("/api/search?q=")
        assert response.status_code == 422  # 验证错误
    
    def test_search_valid(self):
        """测试有效搜索"""
        response = client.get("/api/search?q=test")
        assert response.status_code == 200
        data = response.json()
        assert 'total' in data
        assert 'results' in data
    
    def test_kb_list(self):
        """测试获取知识库列表"""
        response = client.get("/api/kb/list")
        assert response.status_code == 200
        data = response.json()
        assert 'knowledge_bases' in data
    
    def test_preview_nonexistent_file(self):
        """测试预览不存在的文件"""
        response = client.get("/api/preview?file_path=/tmp/nonexistent.txt")
        assert response.status_code == 404
