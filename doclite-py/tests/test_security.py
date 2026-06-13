import os
import pytest
from api.security import (
    generate_csrf_token,
    validate_csrf_token,
    validate_scan_path
)
from fastapi import HTTPException

class TestCSRFToken:
    """CSRF 令牌测试类"""
    
    def test_generate_csrf_token(self):
        """测试生成 CSRF 令牌"""
        token = generate_csrf_token()
        assert token is not None
        assert len(token) == 64  # hex(32 bytes) = 64 chars
    
    def test_validate_csrf_token_valid(self):
        """测试验证有效的 CSRF 令牌"""
        token = generate_csrf_token()
        assert validate_csrf_token(token) is True
    
    def test_validate_csrf_token_invalid(self):
        """测试验证无效的 CSRF 令牌"""
        assert validate_csrf_token("invalid_token") is False
    
    def test_validate_csrf_token_used(self):
        """测试使用后删除 CSRF 令牌"""
        token = generate_csrf_token()
        assert validate_csrf_token(token) is True
        assert validate_csrf_token(token) is False  # 第二次使用应该失败

class TestValidateScanPath:
    """扫描路径验证测试类"""
    
    def test_validate_existing_directory(self):
        """测试验证存在的目录"""
        from config import BASE_DIR
        # 使用项目根目录下的 sample_docs 目录进行测试
        sample_docs_path = os.path.join(BASE_DIR, "sample_docs")
        os.makedirs(sample_docs_path, exist_ok=True)
        
        result = validate_scan_path(sample_docs_path)
        assert result == sample_docs_path
    
    def test_validate_nonexistent_path(self):
        """测试验证不存在的路径"""
        with pytest.raises(HTTPException) as exc_info:
            validate_scan_path("/tmp/nonexistent_dir")
        assert exc_info.value.status_code == 400
    
    def test_validate_file_not_directory(self):
        """测试验证文件路径（不是目录）"""
        import tempfile
        with tempfile.NamedTemporaryFile() as temp_file:
            with pytest.raises(HTTPException) as exc_info:
                validate_scan_path(temp_file.name)
            assert exc_info.value.status_code == 400
