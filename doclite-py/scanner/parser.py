import os
import logging
from typing import Dict
import fitz  # PyMuPDF
from docx import Document

logger = logging.getLogger(__name__)

def extract_text(file_info: Dict[str, any]) -> str:
    """
    根据文件类型提取纯文本内容
    
    Args:
        file_info: 文件信息字典，包含 path, file_type 等字段
    
    Returns:
        提取的文本内容，失败返回空字符串
    """
    path: str = file_info["path"]
    file_type: str = file_info["file_type"]

    try:
        if file_type == "pdf":
            return _extract_pdf(path)
        elif file_type == "docx":
            return _extract_docx(path)
        elif file_type == "pptx":
            return _extract_pptx(path)
        elif file_type == "xlsx":
            return _extract_xlsx(path)
        elif file_type in ("md", "txt"):
            return _extract_plain_text(path)
        else:
            return ""
    except Exception as e:
        logger.error(f"解析文件失败 {path}: {e}")
        return ""

def _extract_pdf(file_path: str) -> str:
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()

def _extract_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs]).strip()

def _extract_pptx(file_path: str) -> str:
    """提取 PowerPoint 文件文本"""
    from pptx import Presentation
    
    prs = Presentation(file_path)
    text_parts = []
    
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text_parts.append(shape.text)
    
    return "\n".join(text_parts).strip()

def _extract_xlsx(file_path: str) -> str:
    """提取 Excel 文件文本"""
    from openpyxl import load_workbook
    
    wb = load_workbook(file_path, read_only=True, data_only=True)
    text_parts = []
    
    for sheet in wb.sheetnames:
        ws = wb[sheet]
        text_parts.append(f"[工作表: {sheet}]")
        
        for row in ws.iter_rows(values_only=True):
            row_text = [str(cell) if cell is not None else "" for cell in row]
            row_str = "\t".join(row_text)
            if row_str.strip():
                text_parts.append(row_str)
    
    wb.close()
    return "\n".join(text_parts).strip()

def _extract_plain_text(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()