import os
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestIndexRoutes:
    """索引路由测试类"""
    
    def test_build_index_endpoint_no_folders(self, monkeypatch):
        """测试构建索引接口（无文件夹时返回400）"""
        from api import index as index_api
        monkeypatch.setattr(index_api, "load_folders", lambda: [])

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
    
    def test_incremental_index_endpoint_no_folders(self, monkeypatch):
        """测试增量索引接口（无文件夹时返回400）"""
        from api import index as index_api
        monkeypatch.setattr(index_api, "load_folders", lambda: [])

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


class TestHealthAndCsrf:
    """健康检查与 CSRF 令牌"""

    def test_health_check(self):
        """GET /api/health 不需令牌，返回 200 与版本号"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_csrf_token_endpoint(self):
        """GET /api/csrf-token 返回 csrf_token 字段"""
        response = client.get("/api/csrf-token")
        assert response.status_code == 200
        data = response.json()
        assert "csrf_token" in data
        assert isinstance(data["csrf_token"], str)
        assert len(data["csrf_token"]) > 0


class TestFolderRoutes:
    """文件夹管理路由"""

    def test_list_folders(self, monkeypatch):
        """GET /api/folders/list 返回 folders 列表"""
        from api import folders
        monkeypatch.setattr(folders, "load_folders", lambda: ["/tmp/a", "/tmp/b"])

        response = client.get("/api/folders/list")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["folders"] == ["/tmp/a", "/tmp/b"]

    def test_add_folder_success(self, monkeypatch, tmp_path):
        """POST /api/folders/add 写入新文件夹并返回更新后列表"""
        from api import folders
        target = str(tmp_path)
        monkeypatch.setattr(folders, "load_folders", lambda: [])
        monkeypatch.setattr(folders, "save_folders", lambda xs: None)

        token = client.get("/api/csrf-token").json()["csrf_token"]
        response = client.post(
            f"/api/folders/add?path={target}",
            headers={"x-csrf-token": token}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        # 返回绝对路径
        assert os.path.abspath(target) in data["folders"]

    def test_add_folder_nonexistent_returns_400(self, monkeypatch):
        """POST /api/folders/add 对不存在路径返回 400"""
        from api import folders
        monkeypatch.setattr(folders, "save_folders", lambda xs: None)

        token = client.get("/api/csrf-token").json()["csrf_token"]
        response = client.post(
            "/api/folders/add?path=/tmp/definitely-does-not-exist-12345",
            headers={"x-csrf-token": token}
        )
        assert response.status_code == 400

    def test_add_folder_without_csrf_returns_403(self):
        """POST /api/folders/add 缺少 CSRF 令牌返回 403"""
        response = client.post("/api/folders/add?path=/tmp")
        assert response.status_code == 403

    def test_remove_folder_success(self, monkeypatch):
        """POST /api/folders/remove 从列表移除已存在文件夹"""
        from api import folders
        monkeypatch.setattr(folders, "load_folders", lambda: ["/tmp/a", "/tmp/b"])
        monkeypatch.setattr(folders, "save_folders", lambda xs: None)

        token = client.get("/api/csrf-token").json()["csrf_token"]
        response = client.post(
            "/api/folders/remove?path=/tmp/a",
            headers={"x-csrf-token": token}
        )
        assert response.status_code == 200
        assert response.json()["folders"] == ["/tmp/b"]

    def test_remove_folder_not_in_list_returns_404(self, monkeypatch):
        """POST /api/folders/remove 对未注册文件夹返回 404"""
        from api import folders
        monkeypatch.setattr(folders, "load_folders", lambda: ["/tmp/a"])
        monkeypatch.setattr(folders, "save_folders", lambda xs: None)

        token = client.get("/api/csrf-token").json()["csrf_token"]
        response = client.post(
            "/api/folders/remove?path=/tmp/not-registered",
            headers={"x-csrf-token": token}
        )
        assert response.status_code == 404

    def test_browse_directory(self):
        """GET /api/folders/browse?path=<sample_docs> 返回目录项"""
        from config import BASE_DIR
        sample_docs = os.path.join(BASE_DIR, "sample_docs")
        os.makedirs(sample_docs, exist_ok=True)

        response = client.get(f"/api/folders/browse?path={sample_docs}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["current_path"] == os.path.abspath(sample_docs)
        assert "items" in data
        assert "parent_path" in data


class TestSettingsRoutes:
    """应用设置路由"""

    def test_get_settings(self):
        """GET /api/settings 返回 settings 字典"""
        response = client.get("/api/settings")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        settings = data["settings"]
        # 必含字段
        assert "ocr_enabled" in settings
        assert "ocr_language" in settings
        assert "embedding_provider" in settings
        assert "api_provider" in settings

    def test_post_settings_updates_and_persists(self, monkeypatch):
        """POST /api/settings JSON body 整体覆盖并返回成功"""
        from api import settings as settings_api
        saved_payloads = []
        monkeypatch.setattr(settings_api, "save_settings",
                            lambda s: saved_payloads.append(s.model_dump()))

        token = client.get("/api/csrf-token").json()["csrf_token"]
        response = client.post(
            "/api/settings",
            headers={"x-csrf-token": token, "Content-Type": "application/json"},
            json={
                "ocr_enabled": False,
                "ocr_language": "eng",
                "embedding_provider": "local",
                "embedding_model": "all-MiniLM-L6-v2",
                "embedding_api_url": "http://localhost:11434",
                "embedding_api_model": "",
                "api_provider": "openai",
                "api_base_url": "https://api.openai.com/v1",
                "api_key": "sk-test",
                "api_model": "gpt-4o-mini",
                "app_name": "DocLite",
                "app_icon": "",
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        # save_settings 真的被调用了一次，参数字段对得上
        assert len(saved_payloads) == 1
        assert saved_payloads[0]["ocr_language"] == "eng"
        assert saved_payloads[0]["api_provider"] == "openai"

    def test_post_settings_missing_csrf_returns_403(self):
        """POST /api/settings 缺 CSRF 令牌返回 403"""
        response = client.post(
            "/api/settings",
            json={"app_name": "x"},
        )
        assert response.status_code == 403

    def test_post_api_config(self, monkeypatch):
        """POST /api/settings/api-config 以 query 形式更新 LLM 配置"""
        from api import settings as settings_api
        saved_payloads = []
        monkeypatch.setattr(settings_api, "save_settings",
                            lambda s: saved_payloads.append(s.model_dump()))

        token = client.get("/api/csrf-token").json()["csrf_token"]
        response = client.post(
            "/api/settings/api-config"
            "?provider=openai&base_url=https://api.openai.com/v1&api_key=sk-abc&model=gpt-4o-mini",
            headers={"x-csrf-token": token},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert saved_payloads[-1]["api_provider"] == "openai"
        assert saved_payloads[-1]["api_key"] == "sk-abc"
        assert saved_payloads[-1]["api_model"] == "gpt-4o-mini"

    def test_post_embedding_model(self, monkeypatch):
        """POST /api/settings/embedding-model 切换 Embedding 模型"""
        from api import settings as settings_api
        saved_payloads = []
        monkeypatch.setattr(settings_api, "save_settings",
                            lambda s: saved_payloads.append(s.model_dump()))

        token = client.get("/api/csrf-token").json()["csrf_token"]
        response = client.post(
            "/api/settings/embedding-model?model_name=bge-small-zh-v1.5",
            headers={"x-csrf-token": token},
        )
        assert response.status_code == 200
        assert saved_payloads[-1]["embedding_model"] == "bge-small-zh-v1.5"

    def test_post_logo(self, monkeypatch):
        """POST /api/settings/logo 更新 app_icon"""
        from api import settings as settings_api
        saved_payloads = []
        monkeypatch.setattr(settings_api, "save_settings",
                            lambda s: saved_payloads.append(s.model_dump()))

        token = client.get("/api/csrf-token").json()["csrf_token"]
        response = client.post(
            "/api/settings/logo?logo_data=data:image/png;base64,AAAA",
            headers={"x-csrf-token": token},
        )
        assert response.status_code == 200
        assert saved_payloads[-1]["app_icon"].startswith("data:image/png;base64,")

    def test_get_providers(self):
        """GET /api/settings/providers 返回 ollama/openai/custom 三家"""
        response = client.get("/api/settings/providers")
        assert response.status_code == 200
        ids = [p["id"] for p in response.json()["providers"]]
        assert {"ollama", "openai", "custom"} <= set(ids)

    def test_get_embedding_models(self):
        """GET /api/settings/embedding-models 至少含 local provider"""
        response = client.get("/api/settings/embedding-models")
        assert response.status_code == 200
        providers = response.json()["providers"]
        assert any(p["id"] == "local" for p in providers)

    def test_get_ocr_languages(self):
        """GET /api/settings/ocr-languages 含中英混合选项"""
        response = client.get("/api/settings/ocr-languages")
        assert response.status_code == 200
        langs = response.json()["languages"]
        ids = [l["id"] for l in langs]
        assert "chi_sim+eng" in ids
        assert "eng" in ids
