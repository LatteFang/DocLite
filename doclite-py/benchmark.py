#!/usr/bin/env python3
"""
DocLite 性能测试脚本
"""

import os
import sys
import time
import tempfile
import shutil
from typing import Dict, List

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import BASE_DIR
from scanner.walker import get_all_files
from scanner.parser import extract_text
from scanner.chunker import chunk_text
from indexer.engine import build_index, incremental_index, get_index
from searcher.service import search_documents

class Benchmark:
    """性能测试类"""
    
    def __init__(self):
        self.results: Dict[str, List[float]] = {}
    
    def measure(self, name: str, func, *args, **kwargs):
        """测量函数执行时间"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        
        if name not in self.results:
            self.results[name] = []
        self.results[name].append(duration)
        
        return result, duration
    
    def create_test_documents(self, count: int = 10) -> str:
        """创建测试文档"""
        temp_dir = tempfile.mkdtemp()
        
        for i in range(count):
            file_path = os.path.join(temp_dir, f"test_{i}.txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"这是测试文档 {i}。\n" * 100)
        
        return temp_dir
    
    def benchmark_file_walking(self, dir_path: str, iterations: int = 3):
        """测试文件遍历性能"""
        print("测试文件遍历性能...")
        
        for i in range(iterations):
            _, duration = self.measure("file_walking", get_all_files, dir_path)
            print(f"  第 {i+1} 次: {duration:.4f}s")
    
    def benchmark_text_extraction(self, dir_path: str, iterations: int = 3):
        """测试文本提取性能"""
        print("测试文本提取性能...")
        
        files = get_all_files(dir_path)
        
        for i in range(iterations):
            total_duration = 0
            for file_info in files:
                _, duration = self.measure("text_extraction", extract_text, file_info)
                total_duration += duration
            print(f"  第 {i+1} 次: {total_duration:.4f}s ({len(files)} 个文件)")
    
    def benchmark_indexing(self, dir_path: str, iterations: int = 3):
        """测试索引构建性能"""
        print("测试索引构建性能...")
        
        for i in range(iterations):
            # 清理旧索引
            index_dir = os.path.join(BASE_DIR, ".doclite_index")
            if os.path.exists(index_dir):
                shutil.rmtree(index_dir)
            
            _, duration = self.measure("indexing", build_index, dir_path)
            print(f"  第 {i+1} 次: {duration:.4f}s")
    
    def benchmark_search(self, dir_path: str, queries: List[str], iterations: int = 3):
        """测试搜索性能"""
        print("测试搜索性能...")
        
        # 先构建索引
        index_dir = os.path.join(BASE_DIR, ".doclite_index")
        if os.path.exists(index_dir):
            shutil.rmtree(index_dir)
        build_index(dir_path)
        
        for query in queries:
            durations = []
            for i in range(iterations):
                _, duration = self.measure(f"search_{query}", search_documents, query)
                durations.append(duration)
            
            avg_duration = sum(durations) / len(durations)
            print(f"  查询 '{query}': 平均 {avg_duration:.4f}s")
    
    def benchmark_chunking(self, iterations: int = 3):
        """测试文档切块性能"""
        print("测试文档切块性能...")
        
        # 创建测试文本
        text = "这是一段测试文本。" * 10000
        
        for i in range(iterations):
            _, duration = self.measure("chunking", chunk_text, text, 500, 50)
            print(f"  第 {i+1} 次: {duration:.4f}s")
    
    def print_summary(self):
        """打印测试结果摘要"""
        print("\n" + "="*50)
        print("性能测试结果摘要")
        print("="*50)
        
        for name, durations in self.results.items():
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            print(f"{name}:")
            print(f"  平均: {avg_duration:.4f}s")
            print(f"  最小: {min_duration:.4f}s")
            print(f"  最大: {max_duration:.4f}s")
            print()

def main():
    """主函数"""
    benchmark = Benchmark()
    
    print("DocLite 性能测试")
    print("="*50)
    
    # 创建测试文档
    print("创建测试文档...")
    temp_dir = benchmark.create_test_documents(50)
    print(f"创建了 50 个测试文档在 {temp_dir}")
    
    try:
        # 运行基准测试
        benchmark.benchmark_file_walking(temp_dir)
        benchmark.benchmark_text_extraction(temp_dir)
        benchmark.benchmark_indexing(temp_dir)
        benchmark.benchmark_search(temp_dir, ["测试", "文档", "性能"])
        benchmark.benchmark_chunking()
        
        # 打印结果
        benchmark.print_summary()
        
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)
        print(f"\n已清理临时目录: {temp_dir}")

if __name__ == '__main__':
    main()
