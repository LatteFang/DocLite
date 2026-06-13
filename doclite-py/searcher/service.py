import logging
from functools import lru_cache
from typing import Optional, Dict, Any
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.highlight import HtmlFormatter, ContextFragmenter
from whoosh.query import Term, NumericRange, And
from indexer.engine import get_index

logger = logging.getLogger(__name__)

# 解析器缓存
_parser_cache: Optional[MultifieldParser] = None
_parser_schema = None

def _get_parser():
    """获取缓存的解析器实例"""
    global _parser_cache, _parser_schema
    
    ix = get_index()
    
    # 如果 schema 变化了，重新创建解析器
    if _parser_cache is None or _parser_schema != ix.schema:
        _parser_cache = MultifieldParser(["filename", "content"], schema=ix.schema)
        _parser_schema = ix.schema
    
    return _parser_cache

def search_documents(query_str: str, page: int = 1, per_page: int = 20, 
                    file_type: str = None, start_time: float = None, end_time: float = None):
    """关键词搜索，返回高亮结果"""
    ix = get_index()

    with ix.searcher() as searcher:
        # 使用缓存的解析器
        parser = _get_parser()
        query = parser.parse(query_str)
        
        # 构建过滤条件列表
        filters = [query]
        
        # 如果指定了文件类型，添加过滤条件
        if file_type:
            type_filter = Term("file_type", file_type)
            filters.append(type_filter)
        
        # 如果指定了时间范围，添加过滤条件
        if start_time is not None or end_time is not None:
            time_filter = NumericRange("mtime", start_time, end_time)
            filters.append(time_filter)
        
        # 组合所有过滤条件
        if len(filters) > 1:
            query = And(filters)

        # 优化搜索性能
        results = searcher.search_page(
            query, 
            page, 
            pagelen=per_page,
            sortedby=None,  # 不排序，按相关性返回
            reverse=False
        )
        
        # 高亮配置：用 <mark> 标签包裹关键词
        results.fragmenter = ContextFragmenter(maxchars=200, surround=30)
        results.formatter = HtmlFormatter(tagname="mark", classname="search-hl")

        result_list = []
        for hit in results:
            # 优化大小格式化
            size_kb = hit["size"] / 1024
            size_str = f"{size_kb:.1f}" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
            
            result_list.append({
                "path": hit["path"],
                "filename": hit["filename"],
                "file_type": hit["file_type"],
                "snippet": hit.highlights("content") or hit.highlights("filename") or "无预览",
                "size": size_kb,
                "size_str": size_str
            })

        return {
            "total": results.total,
            "page": page,
            "per_page": per_page,
            "results": result_list
        }