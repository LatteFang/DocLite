# DocLite
> 极简本地离线文档全文检索工具 · 零配置 · 开箱即用 · 隐私优先

DocLite 是一款轻量级本地文档检索工具，专为解决「本地文件查找难、重型 RAG 工具部署复杂、敏感文档不敢上云」的痛点设计。无需 Docker、无需数据库、无需复杂配置，两行命令即可启动，毫秒级实现 PDF/Word/Markdown/TXT 等多格式文档的全文关键词搜索。

---

## ✨ 核心特性
- **🔒 完全离线，隐私优先**：所有索引与文档数据均存储在本地，无网络请求、无数据上传、无账号体系，敏感文档放心使用
- **⚡ 毫秒级全文检索**：基于成熟全文检索引擎，支持关键词匹配与结果高亮，千份文档内搜索响应低于 100ms
- **📄 多格式支持**：原生支持 PDF、DOCX、PPTX、XLSX、Markdown、TXT 六种主流文档格式
- **🤖 智能问答**：集成 RAG 技术，支持本地文档 AI 问答，无需调用外部 API
- **🖥️ 极简 Web 界面**：自带清爽的网页操作界面，无需命令行操作，浏览器即可完成搜索与索引管理
- **📦 零重型依赖**：无需安装数据库、中间件，纯 Python 实现，安装即用
- **🔧 易二次开发**：代码结构清晰、模块化设计，可轻松扩展更多功能

---

## 🚀 快速开始
### 环境要求
- Python 3.8 及以上版本
- Windows / macOS / Linux 全平台兼容

### 1. 克隆项目
```bash
git clone https://github.com/你的用户名/doclite-py.git
cd doclite-py
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 准备测试文档
项目根目录自带 `sample_docs` 文件夹，可放入你的测试文档（PDF/DOCX/MD/TXT 均可）；也可后续修改配置指定任意目录。

### 4. 启动服务
```bash
python main.py
```

### 5. 开始使用
1. 浏览器打开 `http://localhost:8000`
2. 点击右上角「重建索引」，等待扫描完成
3. 输入关键词，即可获得全文检索结果

---

## 📋 功能说明

### 全文检索
- 支持同时搜索文件名与文档正文
- 搜索结果自动高亮匹配关键词，展示上下文预览片段
- 支持按文件类型（PDF/DOCX/PPTX/XLSX/MD/TXT）筛选
- 支持按修改时间范围筛选
- 支持分页加载，适配大量文档场景
- 搜索历史记录，支持快速重复搜索

### 智能问答 (RAG)
- 本地文档 AI 问答，无需调用外部 API
- 基于文档内容的精准回答，附带引用来源
- 支持多轮对话，自动关联上下文
- 支持多个知识库管理

### 文档管理
- 支持文档在线预览（PDF/DOCX/MD/TXT）
- 支持一键打开原文件
- 增量索引：自动检测新增/修改文件，无需全量重建

### 命令行工具
```bash
# 搜索文档
python cli.py "搜索关键词"

# 按文件类型筛选
python cli.py "搜索关键词" --type pdf

# JSON 格式输出
python cli.py "搜索关键词" --json
```

### 隐私安全
- 全程本地运行，无任何外发网络请求
- 不收集任何用户数据与使用信息
- 索引数据可随时手动删除，不留痕迹
- CSRF 防护，防止跨站请求伪造攻击

---

## 🛠️ 技术栈
| 模块 | 技术选型 | 说明 |
| :--- | :--- | :--- |
| Web 框架 | FastAPI | 轻量高性能，自带接口文档 |
| 全文检索 | Whoosh | 纯 Python 实现，零外部依赖 |
| PDF 解析 | PyMuPDF (fitz) | 高效稳定，文本提取准确率高 |
| Word 解析 | python-docx | 原生 DOCX 文本提取 |
| PPT 解析 | python-pptx | PowerPoint 文本提取 |
| Excel 解析 | openpyxl | Excel 文本提取 |
| Embedding | sentence-transformers | 本地轻量化 Embedding 模型 |
| 向量计算 | NumPy | 高性能向量相似度计算 |
| 前端界面 | 原生 HTML + Tailwind CSS | 无构建流程，直接运行 |

---

## 📁 项目结构
```
doclite-py/
├── main.py              # 程序入口，FastAPI 服务启动
├── config.py            # 全局配置项
├── cli.py               # 命令行搜索工具
├── requirements.txt     # 依赖清单
├── sample_docs/         # 默认扫描的测试文档目录
├── scanner/
│   ├── __init__.py
│   ├── walker.py        # 文件夹遍历与文件收集
│   ├── parser.py        # 多格式文档文本提取
│   └── chunker.py       # 文档切块（用于 RAG）
├── indexer/
│   ├── __init__.py
│   ├── schema.py        # 索引字段结构定义
│   ├── engine.py        # 索引构建、更新、查询引擎
│   ├── embedder.py      # Embedding 生成与向量存储
│   └── knowledge_base.py # 知识库管理
├── searcher/
│   ├── __init__.py
│   ├── service.py       # 搜索逻辑封装、结果高亮、分页
│   ├── retriever.py     # 文档检索器
│   └── chat.py          # 对话管理器
├── tests/
│   ├── conftest.py
│   ├── test_parser.py
│   ├── test_chunker.py
│   ├── test_embedder.py
│   ├── test_service.py
│   └── test_knowledge_base.py
└── web/
    └── static/
        └── index.html   # 前端单页界面
```

---

## 📡 API 接口

### 搜索接口
```http
GET /api/search?q=关键词&page=1&per_page=20&file_type=pdf
```

### 对话接口
```http
POST /api/chat?question=你的问题&top_k=5
```

### 索引构建
```http
POST /api/index/build
POST /api/index/incremental
POST /api/rag/index
```

### 知识库管理
```http
GET /api/kb/list
POST /api/kb/create?name=知识库名称
POST /api/kb/switch?kb_id=知识库ID
DELETE /api/kb/delete?kb_id=知识库ID
```

### 文档操作
```http
GET /api/preview?file_path=/path/to/file
POST /api/open?file_path=/path/to/file
```

---

## ⚙️ 配置说明

环境变量配置：
```bash
# 索引存储目录
export DOCLITE_INDEX_DIR=/path/to/index

# 默认扫描目录
export DOCLITE_SCAN_PATH=/path/to/docs

# 服务端口
export DOCLITE_PORT=8000

# 日志级别
export DOCLITE_LOG_LEVEL=INFO
```

---

## ❓ 常见问题

### Q: 如何修改默认扫描的文件夹路径？
A: 打开 `config.py`，修改 `DEFAULT_SCAN_PATH` 为你的目标目录即可；也可在调用构建索引接口时通过 `path` 参数临时指定。

### Q: 索引会占用很大空间吗？
A: 索引体积通常为原始文档的 20%~30%，纯文本文档占比更低。千份普通文档的索引体积通常在百兆级别。

### Q: 支持加密 PDF 吗？
A: 当前版本暂不支持加密 PDF 的解析，后续版本会考虑加入密码配置选项。

### Q: 如何使用 RAG 问答功能？
A: 
1. 在搜索模式下点击「重建索引」
2. 切换到「问答」模式
3. 点击「构建 RAG 索引」
4. 输入问题即可获得基于文档内容的回答

### Q: 支持哪些文件格式？
A: 当前支持 PDF、DOCX、PPTX、XLSX、Markdown、TXT 六种格式。

---

## 🤝 贡献指南
欢迎任何形式的贡献！无论是提交 Bug、提出新功能，还是提交代码 PR，都非常感谢。

1. Fork 本仓库
2. 创建你的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

---

## 📄 开源协议
本项目基于 **MIT License** 开源，可自由用于个人与商业场景，保留版权声明即可。
