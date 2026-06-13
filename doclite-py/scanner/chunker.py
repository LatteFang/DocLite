import re
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

# 句子分隔符列表（按优先级排序）
SENTENCE_SEPARATORS = ['。', '！', '？', '. ', '! ', '? ', '\n']

def clean_text(text: str) -> str:
    """
    清理文本，去除多余空白字符
    
    Args:
        text: 输入文本
    
    Returns:
        清理后的文本
    """
    # 合并多个换行符
    text = re.sub(r'\n+', '\n', text)
    # 合并多个空格
    text = re.sub(r' +', ' ', text)
    # 去除首尾空白
    return text.strip()

def find_best_split_point(text: str, start: int, end: int) -> int:
    """
    查找最佳分割点（句子或段落边界）
    
    Args:
        text: 文本内容
        start: 起始位置
        end: 结束位置
    
    Returns:
        最佳分割位置
    """
    # 在指定范围内查找分隔符
    for separator in SENTENCE_SEPARATORS:
        last_sep = text.rfind(separator, start, end)
        if last_sep > start:
            return last_sep + len(separator)
    
    # 如果没有找到分隔符，返回原始结束位置
    return end

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict[str, Any]]:
    """
    将文本切分为固定大小的块
    
    Args:
        text: 输入文本
        chunk_size: 每个块的最大字符数
        overlap: 块之间的重叠字符数
    
    Returns:
        包含块文本和元数据的列表
    """
    if not text or not text.strip():
        return []
    
    # 清理文本
    text = clean_text(text)
    
    chunks = []
    start = 0
    chunk_index = 0
    
    while start < len(text):
        # 计算当前块的结束位置
        end = start + chunk_size
        
        # 如果不是最后一块，尝试在句子或段落边界处断开
        if end < len(text):
            end = find_best_split_point(text, start, end)
        
        # 提取块文本
        chunk_content = text[start:end].strip()
        
        if chunk_content:
            chunks.append({
                'text': chunk_content,
                'index': chunk_index,
                'start_pos': start,
                'end_pos': end
            })
            chunk_index += 1
        
        # 移动到下一个块（考虑重叠）
        start = end - overlap if end < len(text) else len(text)
    
    return chunks

def chunk_document(file_info: dict, content: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict]:
    """
    为文档生成带元数据的块
    
    Args:
        file_info: 文件信息字典
        content: 文档内容
        chunk_size: 每个块的最大字符数
        overlap: 块之间的重叠字符数
    
    Returns:
        包含块文本和元数据的列表
    """
    chunks = chunk_text(content, chunk_size, overlap)
    
    # 为每个块添加文档元数据
    for chunk in chunks:
        chunk['path'] = file_info.get('path', '')
        chunk['filename'] = file_info.get('filename', '')
        chunk['file_type'] = file_info.get('file_type', '')
        chunk['mtime'] = file_info.get('mtime', 0)
        chunk['size'] = file_info.get('size', 0)
    
    return chunks
