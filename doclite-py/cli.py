#!/usr/bin/env python3
"""
DocLite 命令行搜索工具
"""

import argparse
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from searcher.service import search_documents
from config import DEFAULT_SCAN_PATH

def main():
    parser = argparse.ArgumentParser(
        description='DocLite - 本地文档全文检索工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s "搜索关键词"
  %(prog)s "搜索关键词" --type pdf
  %(prog)s "搜索关键词" --page 2 --per-page 10
  %(prog)s "搜索关键词" --json
        """
    )
    
    parser.add_argument('query', help='搜索关键词')
    parser.add_argument('--type', '-t', choices=['pdf', 'docx', 'md', 'txt'],
                       help='按文件类型筛选')
    parser.add_argument('--page', '-p', type=int, default=1, help='页码 (默认: 1)')
    parser.add_argument('--per-page', '-n', type=int, default=20, 
                       help='每页结果数 (默认: 20, 范围: 5-100)')
    parser.add_argument('--json', '-j', action='store_true', 
                       help='以 JSON 格式输出结果')
    parser.add_argument('--path', help='指定扫描目录 (默认: sample_docs)')
    
    args = parser.parse_args()
    
    # 验证参数
    if args.per_page < 5 or args.per_page > 100:
        parser.error("--per-page 必须在 5-100 之间")
    
    # 执行搜索
    try:
        result = search_documents(
            query_str=args.query,
            page=args.page,
            per_page=args.per_page,
            file_type=args.type
        )
        
        if args.json:
            # JSON 格式输出
            import json
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # 文本格式输出
            print(f"\n搜索结果: {args.query}")
            print(f"共找到 {result['total']} 条结果 (第 {result['page']}/{max(1, (result['total'] + result['per_page'] - 1) // result['per_page'])} 页)\n")
            
            if not result['results']:
                print("未找到匹配结果")
                return
            
            for i, item in enumerate(result['results'], 1):
                print(f"{i}. {item['filename']} [{item['file_type']}]")
                print(f"   路径: {item['path']}")
                print(f"   大小: {item['size']} KB")
                # 清理高亮标签用于命令行显示
                snippet = item['snippet'].replace('<mark>', '').replace('</mark>', '')
                print(f"   预览: {snippet}")
                print()
                
    except Exception as e:
        print(f"搜索失败: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
