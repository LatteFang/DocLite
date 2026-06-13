import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock
from scanner.parser import extract_text, _extract_plain_text, _extract_image, EXTRACTORS

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
    
    def test_extract_image_ocr(self):
        """测试图片 OCR 提取"""
        with patch('pytesseract.image_to_string') as mock_ocr, \
             patch('PIL.Image.open') as mock_open, \
             patch('api.settings.load_settings') as mock_settings:
            
            # 设置 mock
            mock_settings.return_value.ocr_enabled = True
            mock_settings.return_value.ocr_language = 'chi_sim+eng'
            mock_ocr.return_value = "OCR 识别结果"
            mock_open.return_value = MagicMock()
            
            # 创建临时图片文件
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                temp_path = f.name
            
            try:
                result = _extract_image(temp_path)
                assert result == "OCR 识别结果"
                mock_ocr.assert_called_once()
            finally:
                os.unlink(temp_path)
    
    def test_extract_image_ocr_disabled(self):
        """测试 OCR 禁用时的图片提取"""
        with patch('api.settings.load_settings') as mock_settings:
            mock_settings.return_value.ocr_enabled = False

            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                temp_path = f.name

            try:
                result = _extract_image(temp_path)
                assert result == ""
            finally:
                os.unlink(temp_path)

    def test_extract_pdf_with_images(self):
        """测试 PDF 文本抽取 + 嵌入图片 OCR 拼接"""
        # 构造 mock 的 fitz.Document：1 页 + 1 张图，文本为 "正文内容"
        mock_page = MagicMock()
        mock_page.get_text.return_value = "正文内容"
        mock_page.get_images.return_value = [(1, 0, 0, 0, 0, 0, 0)]  # xref, smask, w, h, bpc, cs, name

        mock_pix = MagicMock()
        mock_pix.save = MagicMock()
        mock_pix.n = 3
        mock_pix.alpha = 0

        mock_doc = MagicMock()
        mock_doc.__enter__ = MagicMock(return_value=mock_doc)
        mock_doc.__exit__ = MagicMock(return_value=False)
        mock_doc.__iter__ = MagicMock(return_value=iter([mock_page]))
        mock_doc.get_page_images.return_value = [(1, 0, 0, 0, 0, 0, 0)]
        mock_doc.extract_image.return_value = (0, b"", 0, 0, 0, 0, "")
        # Pixmap(doc, xref) 返回 mock_pix
        mock_doc.__getitem__ = MagicMock(return_value=mock_pix)

        with patch('scanner.parser.fitz.open', return_value=mock_doc), \
             patch('scanner.parser.fitz.Pixmap', return_value=mock_pix), \
             patch('pytesseract.image_to_string', return_value="图片文字") as mock_ocr, \
             patch('api.settings.load_settings') as mock_settings, \
             patch('scanner.parser.os.unlink') as mock_unlink:
            mock_settings.return_value.ocr_enabled = True
            mock_settings.return_value.ocr_language = 'chi_sim+eng'

            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                temp_path = f.name

            try:
                file_info = {'path': temp_path, 'filename': 'x.pdf', 'file_type': 'pdf'}
                result = extract_text(file_info)

                # 正文 + 图片 OCR 标记
                assert "正文内容" in result
                assert "[图片OCR]" in result
                assert "图片文字" in result
                mock_ocr.assert_called_once()
                # 临时文件清理
                mock_unlink.assert_called()
            finally:
                os.unlink(temp_path)

    def test_extract_pdf_ocr_disabled(self):
        """测试 OCR 禁用时 PDF 不调用图片 OCR"""
        mock_page = MagicMock()
        mock_page.get_text.return_value = "正文内容"

        mock_doc = MagicMock()
        mock_doc.__enter__ = MagicMock(return_value=mock_doc)
        mock_doc.__exit__ = MagicMock(return_value=False)
        mock_doc.__iter__ = MagicMock(return_value=iter([mock_page]))
        mock_doc.get_page_images.return_value = [(1, 0, 0, 0, 0, 0, 0)]

        with patch('scanner.parser.fitz.open', return_value=mock_doc), \
             patch('pytesseract.image_to_string') as mock_ocr, \
             patch('api.settings.load_settings') as mock_settings, \
             patch('scanner.parser.os.unlink') as mock_unlink:
            mock_settings.return_value.ocr_enabled = False

            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                temp_path = f.name

            try:
                file_info = {'path': temp_path, 'filename': 'x.pdf', 'file_type': 'pdf'}
                result = extract_text(file_info)

                assert "正文内容" in result
                assert "[图片OCR]" not in result
                mock_ocr.assert_not_called()
                mock_unlink.assert_not_called()
            finally:
                os.unlink(temp_path)
