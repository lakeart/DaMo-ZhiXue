# A3 开源组件与协议说明

**项目名称**：大模智学  
**版本**：v3.0  
**最后更新**：2026-06-15

---

## 1. 说明目的

根据赛题要求，项目开发过程中若使用开源项目、前沿AI工具或框架，需要在显著位置标注名称、来源与相关协议要求。本文件系统整理当前项目中已使用的所有主要开源组件、外部服务和工具。

### 1.1 合规原则

本项目遵循以下四条合规原则：
1. 所有Python依赖通过`pip` + `requirements.txt`管理，版本可追溯
2. 前端组件通过CDN引入，保留原始版权声明
3. 外部API服务在文档中明确标注来源与用途
4. 未对任何开源组件进行源码修改（仅通过标准API调用）

### 1.2 许可证兼容性

本项目使用的所有开源组件均使用商业友好的开源许可证（MIT、BSD-3-Clause、Apache 2.0），**不存在GPL等强传染性许可证限制**。所有组件均允许商业使用、修改和再分发。

---

## 2. 后端框架与核心组件

| 组件 | 版本 | 用途 | 来源 | 协议 | 选型理由 |
|------|:---:|------|------|------|---------|
| **Python** | ≥3.8 | 编程语言 | https://python.org | PSF License | 生态系统成熟，AI/教育领域首选 |
| **Flask** | 3.x | Web后端框架 | https://palletsprojects.com/p/flask/ | BSD-3-Clause | 轻量灵活，适合比赛项目快速迭代 |
| **Flask-SQLAlchemy** | 3.x | ORM数据库集成 | https://flask-sqlalchemy.palletsprojects.com/ | BSD-3-Clause | 统一数据库操作接口 |
| **Flask-Login** | 0.6.x | 用户登录鉴权 | https://flask-login.readthedocs.io/ | MIT License | 会话管理+权限控制开箱即用 |
| **Flask-WTF** | 1.x | 表单处理与CSRF | https://flask-wtf.readthedocs.io/ | BSD-3-Clause | CSRF防护+表单验证 |
| **SQLAlchemy** | 2.x | 数据库ORM核心 | https://www.sqlalchemy.org/ | MIT License | 支持SQLite/PostgreSQL无缝切换 |
| **Werkzeug** | 3.x | WSGI工具库 | https://werkzeug.palletsprojects.com/ | BSD-3-Clause | Flask底层依赖，密码哈希等 |
| **Jinja2** | 3.x | 模板引擎 | https://jinja.palletsprojects.com/ | BSD-3-Clause | 49个HTML模板的统一渲染引擎 |

### 核心依赖关系图

```
Flask (3.x)
├── Werkzeug (3.x) ─── WSGI + 安全工具
├── Jinja2 (3.x) ──── 模板渲染
├── Flask-SQLAlchemy (3.x)
│   └── SQLAlchemy (2.x) ─── ORM → SQLite/PostgreSQL
├── Flask-Login (0.6.x) ─── 会话管理
└── Flask-WTF (1.x) ─────── CSRF + 表单
```

---

## 3. 数据处理与科学计算

| 组件 | 版本 | 用途 | 来源 | 协议 | 选型理由 |
|------|:---:|------|------|------|---------|
| **pandas** | 2.x | 数据分析与处理 | https://pandas.pydata.org/ | BSD-3-Clause | DataFrame操作，学生数据统计 |
| **numpy** | 1.x | 数值计算基础库 | https://numpy.org/ | BSD-3-Clause | pandas/scikit-learn底层依赖 |
| **scikit-learn** | 1.x | TF-IDF向量化与余弦相似度 | https://scikit-learn.org/ | BSD-3-Clause | 知识库检索核心算法 |
| **PyPDF2 / pypdf** | 3.x | PDF文档文本提取 | https://pypdf2.readthedocs.io/ | BSD-3-Clause | PDF格式解析（无外部依赖） |

### scikit-learn在本项目中的具体使用

```python
# 1. TF-IDF向量化 — 知识库检索引擎
from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4))

# 2. 余弦相似度 — 查询与文档块匹配
from sklearn.metrics.pairwise import cosine_similarity
similarity = cosine_similarity(query_vector, chunk_vectors)

# 3. 聚类分析(可选) — 学习风格聚类
from sklearn.cluster import KMeans
# 用于教师分析工作台的学生群体画像
```

---

## 4. 前端框架与可视化

| 组件 | 版本 | 用途 | 来源 | 协议 | 选型理由 |
|------|:---:|------|------|------|---------|
| **Bootstrap** | 5.x | UI框架与响应式布局 | https://getbootstrap.com/ | MIT License | 深色主题定制，卡片/栅格/导航 |
| **ECharts** | 5.x | 雷达图、趋势图数据可视化 | https://echarts.apache.org/ | Apache 2.0 | 8维雷达图 + 甘特图 + 能力趋势 |
| **Font Awesome** | 6.x | 图标库(Free版) | https://fontawesome.com/ | Font Awesome Free License | 导航栏/卡片/按钮图标 |
| **Mermaid.js** | latest | 思维导图实时渲染 | https://mermaid.js.org/ | MIT License | 学习导图 + 流程图渲染 |
| **Chart.js** | 4.x | 辅助图表 | https://www.chartjs.org/ | MIT License | 柱状图/饼图等补充图表 |

### CDN引入方式

```html
<!-- Bootstrap 5 CSS -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.x/dist/css/bootstrap.min.css" rel="stylesheet">

<!-- ECharts 5 -->
<script src="https://cdn.jsdelivr.net/npm/echarts@5.x/dist/echarts.min.js"></script>

<!-- Mermaid -->
<script src="https://cdn.jsdelivr.net/npm/mermaid@latest/dist/mermaid.min.js"></script>

<!-- Font Awesome 6 -->
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.x/css/all.min.css" rel="stylesheet">

<!-- Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.x/dist/chart.umd.min.js"></script>
```

### 离线部署方案

如需完全离线运行（无CDN），可将上述资源下载到 `app/static/vendor/` 目录并修改模板引用路径。当前版本默认为在线CDN模式。

---

## 5. 文档解析组件

| 组件 | 来源 | 用途 | 说明 |
|------|------|------|------|
| **zipfile** | Python标准库 | DOCX/PPTX文件解压 | OpenXML格式本质为ZIP压缩包 |
| **xml.etree.ElementTree** | Python标准库 | Office文档XML解析 | 提取`word/document.xml`和slide内容 |
| **re** | Python标准库 | 正则表达式 | .ppt二进制文本提取 + 文本清洗 |
| **hashlib** | Python标准库 | SHA256哈希 | 文档去重检测（文件级唯一标识） |
| **chardet** | PyPI (LGPL) | 文本编码检测 | 自动检测TXT/MD/CSV文件的编码(UTF-8/GBK等) |
| **csv** | Python标准库 | CSV表格解析 | CSV文件的结构化读取 |
| **json** | Python标准库 | JSON数据解析 | JSON文件的递归文本提取 |

---

## 6. HTTP与网络组件

| 组件 | 版本 | 用途 | 来源 | 协议 | 选型理由 |
|------|:---:|------|------|------|---------|
| **requests** | 2.x | HTTP客户端（LLM API调用） | https://requests.readthedocs.io/ | Apache 2.0 | Python HTTP客户端事实标准 |
| **python-dotenv** | 1.x | 环境变量管理 | https://github.com/theskumar/python-dotenv | BSD-3-Clause | 从.env文件加载配置 |

---

## 7. 向量检索（可选组件）

| 组件 | 版本 | 用途 | 来源 | 协议 |
|------|:---:|------|------|------|
| **ChromaDB** | 0.4.x | 向量数据库检索（可选） | https://www.trychroma.com/ | Apache 2.0 |

> ChromaDB为可选组件，不在`requirements.txt`中硬依赖。系统默认使用scikit-learn TF-IDF进行语义检索。设置环境变量 `KNOWLEDGE_RETRIEVAL_BACKEND=chroma` 可启用向量检索模式，未安装或不可用时自动回退到TF-IDF。

**双后端架构说明**：

| 后端 | 安装方式 | 启动方式 | 适用场景 |
|------|---------|---------|---------|
| TF-IDF (默认) | 已在requirements.txt | 自动 | 精确术语匹配/零配置启动 |
| ChromaDB | `pip install chromadb` | 环境变量切换 | 语义级检索/同义词匹配 |

---

## 8. 并发与系统组件（Python标准库）

| 组件 | 用途 | 在本项目中的使用位置 |
|------|------|-------------------|
| **concurrent.futures** | 资源生成并行调度 (ThreadPoolExecutor, max_workers=4) | `ResourceGeneratorAgent` |
| **threading** | 多线程基础支持 | 并行生成底层 |
| **uuid** | 资源/文档/会话唯一标识生成 | 所有Agent和路由 |
| **dataclasses** | 数据结构定义 | Agent输入输出模型 |
| **json** | JSON序列化/反序列化 | API请求响应 |
| **os** | 文件系统与路径操作 | 全局 |
| **logging** | 日志记录 | Agent执行日志+Flask日志 |
| **pathlib** | 现代化路径操作 | 文件上传路径处理 |
| **datetime** | 时间戳处理 | 日志/报告/计划时间计算 |
| **enum** | 枚举类型定义 | 资源类型/答案类型/认知风格枚举 |
| **typing** | 类型提示 | 所有Agent接口定义 |

---

## 9. 外部服务与API

### 9.1 大语言模型服务

| 服务 | 用途 | 接口类型 | 配置方式 |
|------|------|---------|---------|
| OpenAI兼容API | 所有Agent的LLM调用 | REST API (POST /v1/chat/completions) | 环境变量 `OPENAI_API_KEY` + `OPENAI_BASE_URL` |
| Ollama本地模型 | 离线LLM推理 | REST API (POST /api/chat) | 默认 `http://localhost:11434`，自动探测 |

**LLM自动选择逻辑**：
```
启动时:
1. 检测环境变量 OPENAI_API_KEY 是否设置
   ├─ 是 → 使用OpenAI兼容API(云端)
   └─ 否 → 检测本地Ollama服务是否可达(GET /api/tags, timeout=2s)
            ├─ 是 → 使用本地Ollama模型
            └─ 否 → 无LLM可用，启用模板降级模式
```

### 9.2 科大讯飞相关接口

| 用途 | 接口 | 说明 |
|------|------|------|
| PPT生成 | 讯飞智文API | 通过API生成PPTX文件 |
| 视频/数字人 | 数字人视频生成API | 数字人视频生成任务 |

> 需配置相应的API密钥和端点信息。答辩演示时可优先使用已生成截图和本地知识库链路，降低对外部服务的实时依赖。

### 9.3 Coze相关接口

| 用途 | 接口 | 说明 |
|------|------|------|
| 课程文档生成 | Coze API | 文档级资源生成增强 |
| 题库生成 | Coze API | 批量习题生成 |

> 需在正式提交文档中明确使用方式与配置要求。

### 9.4 外部CDN服务

| 服务 | 用途 | 资源 |
|------|------|------|
| jsDelivr CDN | Bootstrap/ECharts/Mermaid | `cdn.jsdelivr.net` |
| Cloudflare CDN | Font Awesome | `cdnjs.cloudflare.com` |

---

## 10. 开发与测试工具

| 组件 | 版本 | 用途 | 来源 | 协议 |
|------|:---:|------|------|------|
| **pytest** | 8.x | 自动化测试框架 | https://pytest.org/ | MIT License |
| **Flask-Testing** | 0.x | Flask测试扩展 | https://pythonhosted.org/Flask-Testing/ | BSD-3-Clause |
| **pip** | 24.x | Python包管理 | https://pip.pypa.io/ | MIT License |
| **venv** | (标准库) | 虚拟环境隔离 | Python标准库 | PSF License |

---

## 11. 部署相关组件

| 组件 | 版本 | 用途 | 来源 | 协议 |
|------|:---:|------|------|------|
| **Docker** | 20.x+ | 容器化部署 | https://www.docker.com/ | Apache 2.0 |
| **Nginx** | 1.x | 反向代理(生产环境) | https://nginx.org/ | 2-Clause BSD |
| **Gunicorn** | 21.x | WSGI服务器(Linux生产) | https://gunicorn.org/ | MIT License |
| **Waitress** | 3.x | WSGI服务器(Windows生产) | https://docs.pylonsproject.org/projects/waitress/ | ZPL 2.1 |

### Docker镜像基础

```dockerfile
FROM python:3.11-slim
# 基础镜像来源: https://hub.docker.com/_/python
# 协议: 遵循Python PSF License和Debian相关协议
```

---

## 12. 完整依赖树（requirements.txt解析）

### 直接依赖

| 包名 | 版本 | 分类 |
|------|:---:|------|
| Flask | ≥3.0 | Web框架 |
| Flask-SQLAlchemy | ≥3.1 | ORM |
| Flask-Login | ≥0.6 | 认证 |
| Flask-WTF | ≥1.2 | 表单 |
| SQLAlchemy | ≥2.0 | 数据库 |
| pandas | ≥2.0 | 数据分析 |
| numpy | ≥1.24 | 数值计算 |
| scikit-learn | ≥1.3 | 机器学习/TF-IDF |
| pypdf | ≥3.0 | PDF解析 |
| requests | ≥2.31 | HTTP客户端 |
| python-dotenv | ≥1.0 | 环境变量 |
| gunicorn | ≥21.2 | WSGI (Linux) |
| waitress | ≥3.0 | WSGI (Windows) |
| pytest | ≥8.0 | 测试 |

### 传递依赖（自动安装，无需手动管理）

| 包名 | 来自 | 用途 |
|------|------|------|
| Werkzeug | Flask | WSGI工具 |
| Jinja2 | Flask | 模板引擎 |
| MarkupSafe | Jinja2 | XSS防护 |
| click | Flask | CLI工具 |
| itsdangerous | Flask | 安全签名 |
| blinker | Flask | 信号机制 |
| scipy | scikit-learn | 科学计算 |
| joblib | scikit-learn | 模型序列化 |
| threadpoolctl | scikit-learn | 线程控制 |
| python-dateutil | pandas | 日期处理 |
| pytz | pandas | 时区处理 |
| tzdata | pandas | 时区数据 |
| charset-normalizer | requests | 编码检测 |
| urllib3 | requests | HTTP连接池 |
| certifi | requests | SSL证书 |
| idna | requests | 国际化域名 |

---

## 13. 当前未完全补齐项

| 项目 | 说明 | 优先级 |
|------|------|:----:|
| 前端CDN精确版本号锁定 | 当前使用`5.x`/`latest`等范围版本，建议锁定具体版本号 | P2 |
| 外部接口完整授权说明 | 讯飞/Coze接口的账号来源、调用边界、使用范围需补全 | P1 |
| PPT中的开源声明页 | 答辩PPT需增加"开源与工具声明"页面 | P1 |
| 第三方素材/字体来源 | 如使用非标准字体或图标，需补授权说明 | P2 |
| chardet许可证确认 | 当前使用chardet(LGPL)做编码检测，需确认LGPL在参赛中的合规性 | P1 |
| Docker基础镜像协议 | python:3.11-slim镜像包含Debian组件，需标注其协议 | P2 |

---

## 14. 协议合规声明

本项目使用的所有开源组件均使用商业友好的开源许可证（MIT、BSD-3-Clause、Apache 2.0），不存在GPL等强传染性许可证限制。所有第三方代码的使用均遵循以下原则：

1. **Python依赖**：通过`pip` + `requirements.txt`管理，所有版本可追溯
2. **前端组件**：通过CDN引入，保留原始版权声明，未修改源码
3. **外部API服务**：在本文档第9节明确标注来源与用途
4. **源码完整性**：未对任何开源组件进行源码修改（仅通过标准API调用）
5. **许可证兼容**：所有组件的许可证类型允许商业使用和再分发

### 许可证类型统计

| 许可证 | 组件数 | 组件列表 |
|--------|:--:|---------|
| MIT License | 8 | Flask-Login, SQLAlchemy, Bootstrap, Mermaid.js, Chart.js, pytest, pip, Gunicorn |
| BSD-3-Clause | 7 | Flask, Flask-SQLAlchemy, Flask-WTF, Werkzeug, Jinja2, pandas, numpy, scikit-learn, PyPDF2, python-dotenv, Flask-Testing |
| Apache 2.0 | 4 | ECharts, requests, ChromaDB, Docker |
| PSF License | 2 | Python, venv |
| Font Awesome Free | 1 | Font Awesome |
| ZPL 2.1 | 1 | Waitress |
| 2-Clause BSD | 1 | Nginx |

---

*本说明基于大模智学 v3.0 实际依赖整理，`requirements.txt` 中的完整依赖列表请参见项目根目录。*
