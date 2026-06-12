import os
import logging
import fitz  # PyMuPDF
from docx import Document

logger = logging.getLogger(__name__)

def extract_text(file_info: dict) -> str:
    """根据文件类型提取纯文本内容"""
    path = file_info["path"]
    file_type = file_info["file_type"]

    try:
        if file_type == "pdf":
            return _extract_pdf(path)
        elif file_type == "docx":
            return _extract_docx(path)
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

def _extract_plain_text(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()