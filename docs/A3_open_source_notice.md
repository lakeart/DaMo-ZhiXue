# A3 开源组件与协议说明

**项目名称**：大模智学  
**版本**：v2.0  
**最后更新**：2026-06-15

---

## 1. 说明目的

根据赛题要求，项目开发过程中若使用开源项目、前沿AI工具或框架，需要在显著位置标注名称、来源与相关协议要求。本文件系统整理当前项目中已使用的所有主要开源组件、外部服务和工具。

---

## 2. 后端框架与核心组件

| 组件 | 版本 | 用途 | 来源 | 协议 |
|------|:---:|------|------|------|
| **Python** | ≥3.8 | 编程语言 | https://python.org | PSF License |
| **Flask** | 3.x | Web后端框架 | https://palletsprojects.com/p/flask/ | BSD-3-Clause |
| **Flask-SQLAlchemy** | 3.x | ORM数据库集成 | https://flask-sqlalchemy.palletsprojects.com/ | BSD-3-Clause |
| **Flask-Login** | 0.6.x | 用户登录鉴权 | https://flask-login.readthedocs.io/ | MIT License |
| **Flask-WTF** | 1.x | 表单处理与CSRF | https://flask-wtf.readthedocs.io/ | BSD-3-Clause |
| **SQLAlchemy** | 2.x | 数据库ORM核心 | https://www.sqlalchemy.org/ | MIT License |
| **Werkzeug** | 3.x | WSGI工具库 | https://werkzeug.palletsprojects.com/ | BSD-3-Clause |
| **Jinja2** | 3.x | 模板引擎 | https://jinja.palletsprojects.com/ | BSD-3-Clause |

---

## 3. 数据处理与科学计算

| 组件 | 版本 | 用途 | 来源 | 协议 |
|------|:---:|------|------|------|
| **pandas** | 2.x | 数据分析与处理 | https://pandas.pydata.org/ | BSD-3-Clause |
| **numpy** | 1.x | 数值计算基础库 | https://numpy.org/ | BSD-3-Clause |
| **scikit-learn** | 1.x | TF-IDF向量化与余弦相似度 | https://scikit-learn.org/ | BSD-3-Clause |
| **PyPDF2 / pypdf** | 3.x | PDF文档文本提取 | https://pypdf2.readthedocs.io/ | BSD-3-Clause |

---

## 4. 前端框架与可视化

| 组件 | 版本 | 用途 | 来源 | 协议 |
|------|:---:|------|------|------|
| **Bootstrap** | 5.x | UI框架与响应式布局 | https://getbootstrap.com/ | MIT License |
| **ECharts** | 5.x | 雷达图、趋势图等数据可视化 | https://echarts.apache.org/ | Apache 2.0 |
| **Font Awesome** | 6.x | 图标库 | https://fontawesome.com/ | Font Awesome Free License |
| **Mermaid.js** | latest | 思维导图实时渲染 | https://mermaid.js.org/ | MIT License |

---

## 5. 文档解析组件

| 组件 | 用途 | 说明 |
|------|------|------|
| **zipfile** (Python标准库) | DOCX/PPTX文件解压 | OpenXML格式为ZIP压缩包 |
| **xml.etree.ElementTree** (Python标准库) | Office文档XML解析 | 提取word/document.xml和slide内容 |
| **re** (Python标准库) | 正则表达式 | .ppt二进制文本提取 + 文本清理 |
| **hashlib** (Python标准库) | SHA256哈希 | 文档去重检测 |

---

## 6. HTTP与网络组件

| 组件 | 版本 | 用途 | 来源 | 协议 |
|------|:---:|------|------|------|
| **requests** | 2.x | HTTP客户端（LLM API调用） | https://requests.readthedocs.io/ | Apache 2.0 |
| **python-dotenv** | 1.x | 环境变量管理 | https://github.com/theskumar/python-dotenv | BSD-3-Clause |

---

## 7. 向量检索（可选组件）

| 组件 | 版本 | 用途 | 来源 | 协议 |
|------|:---:|------|------|------|
| **ChromaDB** | 0.4.x | 向量数据库检索（可选） | https://www.trychroma.com/ | Apache 2.0 |

> ChromaDB为可选组件，系统默认使用scikit-learn TF-IDF进行语义检索。设置环境变量 `KNOWLEDGE_RETRIEVAL_BACKEND=chroma` 可启用向量检索模式，未安装或不可用时自动回退到TF-IDF。

---

## 8. 并发与系统

| 组件 | 用途 |
|------|------|
| **concurrent.futures** (Python标准库) | 资源生成并行调度 (ThreadPoolExecutor) |
| **threading** (Python标准库) | 多线程支持 |
| **uuid** (Python标准库) | 资源/文档/会话唯一标识生成 |
| **dataclasses** (Python标准库) | 数据结构定义 |
| **json** (Python标准库) | JSON序列化/反序列化 |
| **os** (Python标准库) | 文件系统与路径操作 |
| **logging** (Python标准库) | 日志记录 |

---

## 9. 外部服务与API

### 9.1 大语言模型服务

| 服务 | 用途 | 接口类型 | 配置方式 |
|------|------|---------|---------|
| OpenAI兼容API | 所有Agent的LLM调用 | REST API (POST /v1/chat/completions) | 环境变量 `OPENAI_API_KEY` + `OPENAI_BASE_URL` |
| Ollama本地模型 | 离线LLM推理 | REST API (POST /api/chat) | 默认 `http://localhost:11434`，自动探测 |

**LLM自动选择逻辑**：
1. 优先检测本地Ollama服务（`GET /api/tags`, timeout=2s）
2. 其次检查OpenAI兼容API环境变量
3. 否则使用本地Ollama（需用户自行启动）

### 9.2 科大讯飞相关接口

| 用途 | 说明 |
|------|------|
| PPT生成 | 通过讯飞智文API生成PPTX文件 |
| 视频/数字人 | 数字人视频生成任务 |

> 需配置相应的API密钥和端点信息。答辩演示时可优先使用已生成截图和本地知识库链路，降低对外部服务的实时依赖。

### 9.3 Coze相关接口

| 用途 | 说明 |
|------|------|
| 课程文档生成 | 文档级资源生成增强 |
| 题库生成 | 批量习题生成 |

> 需在正式提交文档中明确使用方式与配置要求。

---

## 10. 当前未完全补齐项

| 项目 | 说明 | 优先级 |
|------|------|:----:|
| 前端CDN精确版本号 | 需统一核对Bootstrap/ECharts/Font Awesome/Mermaid CDN的具体版本 | P2 |
| 外部接口完整授权说明 | 讯飞/Coze接口的账号来源、调用边界、使用范围需补全 | P1 |
| PPT中的开源声明页 | 答辩PPT需增加"开源与工具声明"页面 | P1 |
| 第三方素材/字体来源 | 如使用非标准字体或图标，需补授权说明 | P2 |

---

## 11. 协议合规声明

本项目使用的所有开源组件均使用商业友好的开源许可证（MIT、BSD-3-Clause、Apache 2.0），不存在GPL等强传染性许可证限制。所有第三方代码的使用均遵循以下原则：
1. 通过pip/requirements.txt管理Python依赖
2. 前端组件通过CDN引入，保留原始版权声明
3. 外部API服务在文档中明确标注来源与用途
4. 未对任何开源组件进行源码修改（仅通过标准API调用）

---

*本说明基于大模智学 v2.0 实际依赖整理，`requirements.txt` 中的完整依赖列表请参见项目根目录。*
