# Changelog

## v0.6.0 (2026-06-13)

### 文档
- README 全面更新：对齐 v0.6.0 实际能力，补全图片 OCR、API 端点（含 curl 调用示例）、FAQ
- CHANGELOG / 项目结构 / 技术栈 同步更新

### 测试
- `tests/test_api_routes.py` 新增 18 个端点测试（`/api/health`、`/api/csrf-token`、`/api/folders/*`、`/api/settings/*`），覆盖此前零覆盖的 13 个端点
- 修复合并 monkeypatch 问题：两个 `no_folders` 用例用 `monkeypatch.setattr` 隔离 `load_folders`，恢复测试独立性

### 文件变更
- `README.md`: 端点表 + curl 调用示例 + FAQ 扩展
- `doclite-py/tests/test_api_routes.py`: 新增 3 个测试类

## 用户体验优化 (2026-06-12)

### 加载状态
- 搜索加载动画：显示旋转图标和"搜索中..."提示
- 聊天加载动画：显示"思考中..."和旋转图标
- 按钮禁用状态：操作时禁用按钮并添加半透明效果

### 错误提示改进
- 网络错误：显示"网络错误，请检查服务是否启动"
- 业务错误：显示服务器返回的具体错误信息
- 操作成功：打开文件成功时不显示提示，减少干扰

### 文件变更
- `doclite-py/web/static/index.html`: 添加加载状态和改进错误提示

## 安全性优化 (2026-06-12)

### 输入验证
- 搜索查询：添加长度限制（1-500 字符），清理输入防止注入
- 知识库名称：添加格式验证（只允许字母、数字、中文、下划线、连字符）
- 时间范围验证：确保开始时间不大于结束时间
- 文件类型验证：限制为预定义的文件类型列表

### CSRF 防护
- 实现基于令牌的 CSRF 防护机制
- 新增 `GET /api/csrf-token` 接口获取令牌
- 为所有 POST/DELETE 接口添加 CSRF 令牌验证
- 令牌使用后自动删除，防止重放攻击

### 权限控制
- 添加操作级别的权限配置
- 定义允许的操作列表和描述
- 为权限系统预留扩展接口

### 文件变更
- `doclite-py/main.py`: 添加输入验证、CSRF 防护和权限控制

## 代码质量优化 (2026-06-12)

### 单元测试
- 添加 `tests/` 目录，创建完整的测试套件
- `test_parser.py`: 测试文本提取功能
- `test_chunker.py`: 测试文档切块功能
- `test_embedder.py`: 测试 Embedding 生成和向量存储
- `test_service.py`: 测试搜索服务功能
- `test_knowledge_base.py`: 测试知识库管理功能
- `conftest.py`: 测试配置和路径设置

### 类型注解
- `config.py`: 添加类型注解，明确配置项类型
- `scanner/parser.py`: 添加函数参数和返回值类型注解
- `scanner/chunker.py`: 添加类型注解，提升代码可读性

### 依赖变更
- 新增 `pytest>=7.0.0`：测试框架

## 性能优化 (2026-06-12)

### 索引构建优化
- 使用 `ThreadPoolExecutor` 并行提取文本，提升索引构建速度
- 实现批量提交机制，每 500 个文档提交一次，减少 IO 开销
- 添加进度日志，实时显示索引进度

### 搜索性能优化
- 缓存 `MultifieldParser` 实例，避免重复创建
- 优化查询处理，减少不必要的排序操作
- 改进大小格式化，支持 MB 单位显示

### RAG 查询优化
- 添加向量和元数据缓存，避免重复加载
- 实现缓存失效机制，确保数据一致性
- 优化相似度计算，使用 NumPy 向量化操作

### 文件变更
- `doclite-py/indexer/engine.py`: 添加并行处理和批量提交
- `doclite-py/searcher/service.py`: 添加解析器缓存和优化查询
- `doclite-py/searcher/retriever.py`: 添加向量缓存和优化搜索

## v0.6 (2026-06-12)

### 新功能
- 多轮对话：支持上下文感知的多轮对话，自动关联历史问题
- 引用溯源增强：显示详细来源信息，支持预览文件
- 知识库管理：支持创建、切换、删除多个知识库
- 更多格式支持：新增 PPT (pptx) 和 Excel (xlsx) 文件格式支持

### API 变更
- 新增 `GET /api/kb/list` 接口：列出所有知识库
- 新增 `POST /api/kb/create` 接口：创建知识库
- 新增 `POST /api/kb/switch` 接口：切换当前知识库
- 新增 `DELETE /api/kb/delete` 接口：删除知识库

### 依赖变更
- 新增 `python-pptx>=0.6.21`：PowerPoint 文件解析
- 新增 `openpyxl>=3.0.10`：Excel 文件解析

### 文件变更
- `doclite-py/searcher/chat.py`: 增强多轮对话支持
- `doclite-py/indexer/knowledge_base.py`: 新增知识库管理模块
- `doclite-py/scanner/parser.py`: 新增 PPT 和 Excel 解析
- `doclite-py/config.py`: 更新支持的文件格式
- `doclite-py/main.py`: 新增知识库管理 API
- `doclite-py/web/static/index.html`: 增强引用溯源显示
- `doclite-py/requirements.txt`: 更新依赖列表

## v0.5 (2026-06-12)

### 新功能
- 文档预览：支持 PDF/DOCX/MD/TXT 文件在线预览
- 打开原文件：支持调用系统默认程序打开文件
- CLI 搜索：实现命令行搜索模式，支持 JSON 输出
- 搜索历史：使用 localStorage 保存搜索历史，支持快速搜索

### API 变更
- 新增 `POST /api/open` 接口：打开原文件
- 新增 `GET /api/preview` 接口：文档预览

### 文件变更
- `doclite-py/main.py`: 新增文档预览和打开原文件接口
- `doclite-py/cli.py`: 新增命令行搜索工具
- `doclite-py/web/static/index.html`: 添加预览/打开按钮、搜索历史功能

## v0.4 (2026-06-12)

### 新功能
- 文档切块：支持按段落/句子边界切分文档，生成带元数据的块
- Embedding 生成：集成 sentence-transformers，支持本地轻量化 Embedding 模型
- 向量存储：实现基于 NumPy 的本地向量存储，支持余弦相似度检索
- 相似度检索：支持文档块检索和上下文窗口
- 对话接口：实现文档问答功能，支持引用溯源
- 聊天界面：添加 Web 端对话 UI，支持多轮对话

### API 变更
- 新增 `POST /api/chat` 接口：文档问答
- 新增 `POST /api/rag/index` 接口：构建 RAG 索引

### 依赖变更
- 新增 `sentence-transformers>=2.2.0`：Embedding 模型
- 新增 `numpy>=1.21.0`：向量计算

### 文件变更
- `doclite-py/scanner/chunker.py`: 新增文档切块模块
- `doclite-py/indexer/embedder.py`: 新增 Embedding 生成和向量存储模块
- `doclite-py/searcher/retriever.py`: 新增文档检索器模块
- `doclite-py/searcher/chat.py`: 新增对话管理器模块
- `doclite-py/main.py`: 新增对话和 RAG 索引 API 接口
- `doclite-py/web/static/index.html`: 添加聊天界面和模式切换
- `doclite-py/requirements.txt`: 更新依赖列表

## v0.3 (2026-06-12)

### 新功能
- 增量索引：支持自动检测新增、修改、删除的文件，无需全量重建索引
- 文件类型筛选：搜索时支持按 pdf、docx、md、txt 过滤
- 时间范围筛选：搜索时支持按修改时间范围过滤
- 分页 UI：添加分页控件，支持上一页/下一页导航

### API 变更
- 新增 `POST /api/index/incremental` 接口：增量索引
- `GET /api/search` 接口新增参数：
  - `file_type`：文件类型筛选
  - `start_time`：开始时间戳（秒）
  - `end_time`：结束时间戳（秒）

### 文件变更
- `doclite-py/indexer/engine.py`: 新增 `incremental_index` 函数
- `doclite-py/searcher/service.py`: 添加文件类型和时间范围筛选
- `doclite-py/main.py`: 新增增量索引接口，更新搜索接口参数
- `doclite-py/web/static/index.html`: 添加分页 UI 和相关 JavaScript

## v0.2 (2026-06-12)

### 安全修复
- 修复 XSS 漏洞：在 `web/static/index.html` 中添加 `escapeHtml` 函数，转义所有用户输入
- 修复索引清空逻辑：在 `indexer/engine.py` 中使用 `shutil.rmtree` 正确删除旧索引目录
- 添加路径遍历防护：在 `main.py` 中验证扫描路径安全性，防止目录遍历攻击

### 基础改进
- 替换 print 为 logging：在 `scanner/parser.py` 中使用 logging 模块记录错误
- 添加 `__init__.py` 文件：为 `scanner`、`indexer`、`searcher` 目录添加包初始化文件
- 添加环境变量配置支持：在 `config.py` 中支持 `DOCLITE_INDEX_DIR`、`DOCLITE_SCAN_PATH`、`DOCLITE_PORT`、`DOCLITE_LOG_LEVEL` 环境变量
- 异步索引构建：在 `main.py` 中使用 FastAPI BackgroundTasks 实现后台索引构建

### 文件变更
- `doclite-py/web/static/index.html`: 添加 XSS 防护
- `doclite-py/indexer/engine.py`: 修复索引清空逻辑，添加 logging
- `doclite-py/main.py`: 添加路径遍历防护，异步索引构建，环境变量配置
- `doclite-py/scanner/parser.py`: 替换 print 为 logging
- `doclite-py/config.py`: 添加环境变量支持
- `doclite-py/scanner/__init__.py`: 新增
- `doclite-py/indexer/__init__.py`: 新增
- `doclite-py/searcher/__init__.py`: 新增
