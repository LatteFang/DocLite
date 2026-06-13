# DocLite
> 极简本地离线文档全文检索工具 · 零配置 · 开箱即用 · 隐私优先

DocLite 是一款轻量级本地文档检索工具，专为解决「本地文件查找难、重型 RAG 工具部署复杂、敏感文档不敢上云」的痛点设计。无需 Docker、无需数据库、无需复杂配置，两行命令即可启动，毫秒级实现 PDF/Word/PPT/Excel/Markdown/TXT/图片 等多格式文档的全文关键词搜索与 AI 问答。

---

## ✨ 核心特性
- **🔒 完全离线，隐私优先**：所有索引与文档数据均存储在本地，无网络请求、无数据上传、无账号体系，敏感文档放心使用
- **⚡ 毫秒级全文检索**：基于成熟全文检索引擎，支持关键词匹配与结果高亮，千份文档内搜索响应低于 100ms
- **📄 多格式支持**：原生支持 PDF、DOCX、PPTX、XLSX、Markdown、TXT 六种主流文档格式，外加 **PNG/JPG/JPEG/BMP/TIFF/WEBP/GIF** 八种图片的 OCR 文字识别（含 PDF 内嵌入图片）
- **🤖 智能问答**：集成 RAG 技术，支持本地文档 AI 问答；可对接 Ollama / OpenAI 兼容 API
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
项目根目录自带 `sample_docs` 文件夹，可放入你的测试文档（PDF/DOCX/PPTX/XLSX/MD/TXT/图片 均可）；也可后续修改配置指定任意目录。

> 图片 OCR 识别需要本机额外安装 [Tesseract](https://github.com/tesseract-ocr/tesseract)：
> ```bash
> # macOS
> brew install tesseract tesseract-lang   # tesseract-lang 提供中文等额外语言
> # Ubuntu / Debian
> sudo apt install tesseract-ocr tesseract-ocr-chi-sim
> # Windows: 从 https://github.com/UB-Mannheim/tesseract/wiki 下载安装包
> ```

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

### 图片 OCR（基于 Tesseract）
- 自动识别 PNG/JPG/JPEG/BMP/TIFF/WEBP/GIF 图片中的文字
- 自动识别 PDF 文档中嵌入的图片（扫描件、截图、照片）
- 可在 Web 设置面板一键开关，并切换识别语言（英文/简体中文/繁體中文/中英混合/日文/韩文）
- 未安装 Tesseract 或依赖时自动跳过，不影响其他功能

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
| 图片 OCR | pytesseract + Pillow + Tesseract | 图片及 PDF 嵌入图片文字识别（可选） |
| 前端界面 | 原生 HTML + Tailwind CSS | 无构建流程，直接运行 |

---

## 📁 项目结构
```
doclite-py/
├── main.py              # 程序入口，FastAPI 服务启动
├── config.py            # 全局配置项
├── cli.py               # 命令行搜索工具
├── requirements.txt     # 依赖清单
├── pyproject.toml       # 包元数据，支持 pip install
├── sample_docs/         # 默认扫描的测试文档目录
├── scanner/
│   ├── walker.py        # 文件夹遍历与文件收集
│   ├── parser.py        # 多格式文档文本提取（含 OCR）
│   └── chunker.py       # 文档切块（用于 RAG）
├── indexer/
│   ├── schema.py        # 索引字段结构定义
│   ├── engine.py        # 索引构建、全量/增量引擎
│   ├── embedder.py      # Embedding 生成与向量存储
│   └── knowledge_base.py # 知识库管理
├── searcher/
│   ├── service.py       # 搜索逻辑封装、结果高亮、分页
│   ├── retriever.py     # 文档检索器（向量 + 关键词）
│   └── chat.py          # 对话管理器（Ollama / OpenAI 兼容）
├── api/                 # FastAPI 路由拆分
│   ├── index.py         # 索引构建接口
│   ├── search.py        # 搜索接口
│   ├── kb.py            # 知识库接口
│   ├── file.py          # 文档预览 / 打开
│   ├── folders.py       # 扫描文件夹管理
│   ├── settings.py      # 应用设置（含 OCR / Embedding / API Provider）
│   └── security.py      # CSRF 防护
├── tests/               # 单元 + 接口测试（pytest）
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
GET  /api/preview?file_path=/path/to/file
POST /api/open?file_path=/path/to/file
```

### 文件夹 / 设置 / 安全
```http
GET  /api/folders/list                    # 已保存的扫描文件夹
POST /api/folders/add?path=...            # 新增扫描文件夹
POST /api/folders/remove?path=...         # 移除扫描文件夹
GET  /api/folders/browse?path=...         # 浏览目录（用于前端选择）

GET  /api/settings                        # 读取应用设置
POST /api/settings                        # 更新应用设置（OCR / Embedding / API Provider）
GET  /api/settings/providers              # LLM Provider 列表（ollama / openai / custom）
GET  /api/settings/embedding-models       # Embedding 模型列表
GET  /api/settings/ocr-languages          # Tesseract 语言列表
GET  /api/settings/logo?logo_data=...     # 更新应用 Logo

GET  /api/csrf-token                      # 获取 CSRF 令牌
GET  /api/health                          # 健康检查
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

## 🤖 Ollama 集成（可选）

DocLite 支持集成 Ollama 进行更智能的文档问答。Ollama 是一个本地运行大语言模型的工具。

### 安装 Ollama

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# 或访问 https://ollama.com 下载安装包
```

### 下载模型

```bash
# 下载轻量级模型（推荐）
ollama pull qwen2:1.5b

# 或下载其他模型
ollama pull llama3.2
ollama pull mistral
```

### 集成 DocLite

DocLite 已内置 Ollama 对接（`searcher/chat.py`），无需自行扩展代码：

1. 启动 Ollama 服务：
```bash
ollama serve
```

2. 打开 Web 界面「设置」面板，将 LLM Provider 切换为 `Ollama (本地)`，地址默认为 `http://localhost:11434`，模型填入已下载的模型名（如 `qwen2:1.5b`），保存即可在问答模式使用。

若需接入其他 OpenAI 兼容 API（OpenAI、Azure、第三方代理等），同样在设置面板中选择 `OpenAI` 或 `自定义 API`，填入 `Base URL` / `API Key` / 模型名即可。

### 注意事项
- Ollama 需要单独安装，不是 DocLite 的必需依赖
- 首次运行模型会自动下载，需要网络连接
- 建议使用 1.5B-3B 参数的轻量级模型
- 本地运行需要足够的内存（建议 4GB+）

---

## ❓ 常见问题

### Q: 如何修改默认扫描的文件夹路径？
A: 打开 `config.py`，修改 `DEFAULT_SCAN_PATH` 为你的目标目录即可；也可在 Web 界面通过「文件夹」面板添加任意路径，或调用构建索引接口时通过 `path` 参数临时指定。

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
5. 在「设置」中配置 LLM Provider（Ollama / OpenAI 兼容 API）

### Q: 支持哪些文件格式？
A: 当前支持 PDF、DOCX、PPTX、XLSX、Markdown、TXT 六种文本格式，外加 PNG/JPG/JPEG/BMP/TIFF/WEBP/GIF 八种图片格式（OCR 识别）。PDF 文档中嵌入的图片也会自动走 OCR 识别。

### Q: 图片 OCR 识别需要什么？
A: 需要本机安装 Tesseract OCR 引擎和 Python 包 `pytesseract` + `Pillow`（见「快速开始」）。在 Web 设置面板里可一键开关 OCR，或切换识别语言。未安装时图片会被跳过，不影响其他文档类型的检索。

### Q: 增量索引和全量重建有什么区别？
A: 全量重建会清空旧索引目录后重新扫描（`POST /api/index/build`），适合首次使用或索引异常修复；增量索引（`POST /api/index/incremental`）只对比 mtime，自动添加/更新/删除变更文件，速度更快，推荐日常使用。

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
