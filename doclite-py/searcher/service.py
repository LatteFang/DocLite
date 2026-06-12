from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.highlight import HtmlFormatter, ContextFragmenter
from whoosh.query import Term, NumericRange
from indexer.engine import get_index

def search_documents(query_str: str, page: int = 1, per_page: int = 20, 
                    file_type: str = None, start_time: float = None, end_time: float = None):
    """关键词搜索，返回高亮结果"""
    ix = get_index()

    with ix.searcher() as searcher:
        # 同时搜索文件名和正文
        parser = MultifieldParser(["filename", "content"], schema=ix.schema)
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
            from whoosh.query import And
            query = And(filters)

        results = searcher.search_page(query, page, pagelen=per_page)
        # 高亮配置：用 <mark> 标签包裹关键词
        results.fragmenter = ContextFragmenter(maxchars=200, surround=30)
        results.formatter = HtmlFormatter(tagname="mark", classname="search-hl")

        result_list = []
        for hit in results:
            result_list.append({
                "path": hit["path"],
                "filename": hit["filename"],
                "file_type": hit["file_type"],
                "snippet": hit.highlights("content") or hit.highlights("filename") or "无预览",
                "size": round(hit["size"] / 1024, 1)  # 转KB
            })

        return {
            "total": results.total,
            "page": page,
            "per_page": per_page,
            "results": result_list
        }