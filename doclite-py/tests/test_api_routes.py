import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestIndexRoutes:
    """索引路由测试类"""
    
    def test_build_index_endpoint_no_folders(self):
        """测试构建索引接口（无文件夹时返回400）"""
        token_response = client.get("/api/csrf-token")
        csrf_token = token_response.json()["csrf_token"]
        
        response = client.post(
            "/api/index/build",
            headers={"x-csrf-token": csrf_token}
        )
        # 没有选择文件夹时返回 400
        assert response.status_code == 400
    
    def test_build_index_endpoint_with_path(self):
        """测试构建索引接口（指定路径）"""
        token_response = client.get("/api/csrf-token")
        csrf_token = token_response.json()["csrf_token"]
        
        import os
        from config import BASE_DIR
        
        # 使用项目内的 sample_docs 目录
        sample_docs_path = os.path.join(BASE_DIR, "sample_docs")
        os.makedirs(sample_docs_path, exist_ok=True)
        
        # 创建测试文件
        test_file = os.path.join(sample_docs_path, "test.txt")
        with open(test_file, "w") as f:
            f.write("测试内容")
        
        try:
            response = client.post(
                f"/api/index/build?path={sample_docs_path}",
                headers={"x-csrf-token": csrf_token}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
        finally:
            # 清理测试文件
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_incremental_index_endpoint_no_folders(self):
        """测试增量索引接口（无文件夹时返回400）"""
        token_response = client.get("/api/csrf-token")
        csrf_token = token_response.json()["csrf_token"]
        
        response = client.post(
            "/api/index/incremental",
            headers={"x-csrf-token": csrf_token}
        )
        # 没有选择文件夹时返回 400
        assert response.status_code == 400

class TestKnowledgeBaseRoutes:
    """知识库路由测试类"""
    
    def test_list_knowledge_bases(self):
        """测试列出知识库"""
        response = client.get("/api/kb/list")
        assert response.status_code == 200
        data = response.json()
        assert "knowledge_bases" in data
    
    def test_create_knowledge_base(self):
        """测试创建知识库"""
        token_response = client.get("/api/csrf-token")
        csrf_token = token_response.json()["csrf_token"]
        
        response = client.post(
            "/api/kb/create?name=test_kb&description=test",
            headers={"x-csrf-token": csrf_token}
        )
        # 可能返回 200 或 400（如果知识库已存在）
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "ok"

class TestFileRoutes:
    """文件路由测试类"""
    
    def test_preview_nonexistent_file(self):
        """测试预览不存在的文件"""
        response = client.get("/api/preview?file_path=/tmp/nonexistent.txt")
        assert response.status_code == 404
    
    def test_open_nonexistent_file(self):
        """测试打开不存在的文件"""
        token_response = client.get("/api/csrf-token")
        csrf_token = token_response.json()["csrf_token"]
        
        response = client.post(
            "/api/open?file_path=/tmp/nonexistent.txt",
            headers={"x-csrf-token": csrf_token}
        )
        assert response.status_code == 404

class TestSearchRoutes:
    """搜索路由测试类"""
    
    def test_search_valid_query(self):
        """测试有效搜索查询"""
        response = client.get("/api/search?q=test")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "results" in data
    
    def test_search_with_file_type(self):
        """测试带文件类型的搜索"""
        response = client.get("/api/search?q=test&file_type=txt")
        assert response.status_code == 200
    
    def test_search_invalid_file_type(self):
        """测试无效文件类型"""
        response = client.get("/api/search?q=test&file_type=invalid")
        assert response.status_code == 400
