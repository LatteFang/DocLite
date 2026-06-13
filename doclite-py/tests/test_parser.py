import os
import pytest
import tempfile
from scanner.parser import extract_text, _extract_plain_text, EXTRACTORS

class TestParser:
    """解析器测试类"""
    
    def test_extract_plain_text(self):
        """测试纯文本提取"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("这是一段测试文本。\n第二行内容。")
            temp_path = f.name
        
        try:
            result = _extract_plain_text(temp_path)
            assert "测试文本" in result
            assert "第二行内容" in result
        finally:
            os.unlink(temp_path)
    
    def test_extract_text_with_file_info(self):
        """测试通过文件信息提取文本"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("测试内容")
            temp_path = f.name
        
        try:
            file_info = {
                'path': temp_path,
                'filename': os.path.basename(temp_path),
                'file_type': 'txt'
            }
            result = extract_text(file_info)
            assert "测试内容" in result
        finally:
            os.unlink(temp_path)
    
    def test_extract_text_unsupported_format(self):
        """测试不支持的文件格式"""
        file_info = {
            'path': '/tmp/test.xyz',
            'filename': 'test.xyz',
            'file_type': 'xyz'
        }
        result = extract_text(file_info)
        assert result == ""
    
    def test_extract_text_nonexistent_file(self):
        """测试不存在的文件"""
        file_info = {
            'path': '/tmp/nonexistent.txt',
            'filename': 'nonexistent.txt',
            'file_type': 'txt'
        }
        result = extract_text(file_info)
        assert result == ""
    
    def test_extractors_registry(self):
        """测试提取器注册表"""
        assert "pdf" in EXTRACTORS
        assert "docx" in EXTRACTORS
        assert "pptx" in EXTRACTORS
        assert "xlsx" in EXTRACTORS
        assert "md" in EXTRACTORS
        assert "txt" in EXTRACTORS
        assert "png" in EXTRACTORS
        assert "jpg" in EXTRACTORS
        assert "jpeg" in EXTRACTORS
        assert "bmp" in EXTRACTORS
        assert "tiff" in EXTRACTORS
        assert "tif" in EXTRACTORS
        assert "webp" in EXTRACTORS
        assert "gif" in EXTRACTORS
    
    def test_extract_markdown(self):
        """测试 Markdown 文件提取"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write("# 标题\n\n这是内容。")
            temp_path = f.name
        
        try:
            file_info = {
                'path': temp_path,
                'filename': os.path.basename(temp_path),
                'file_type': 'md'
            }
            result = extract_text(file_info)
            assert "标题" in result
            assert "这是内容" in result
        finally:
            os.unlink(temp_path)
