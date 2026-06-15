# 大模智学：基于大模型的个性化资源生成与学习多智能体系统

面向中国软件杯 A3 赛题的高校计算机能力画像、知识库 RAG 与智能学习资源生成系统。

## 项目简介

本系统面向高校教师、学生和管理员三类用户，通过**对话式学习画像**、**多智能体协同**、**知识库 RAG**、**个性化学习计划**与**学习资源生成**，帮助教师精准掌握学生学习状态，帮助学生获得可信、可追溯、可执行的学习支持。

### 系统架构

```
┌──────────────────────────────────────────────────────────────┐
│                        用户层 (3角色)                          │
│         管理员              教师              学生              │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                      前端展示层 (49 HTML)                       │
│    Bootstrap 5 深墨蓝科技风 + ECharts + Mermaid + SSE流式       │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    Flask Blueprint 路由层 (10个)                │
│   auth / analysis / student / quiz / assistant / agent / ...  │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    AgentCoordinator (协调器单例)                │
│                    会话管理 / 并行调度 / 执行日志                 │
├──────────┬──────────┬──────────┬──────────┬──────────────────┤
│ Profile  │ Resource │ Planner  │  Tutor   │  Evaluator       │
│ Builder  │Generator │  Agent   │  Agent   │    Agent         │
│ 10维画像 │ 6种资源  │ 5里程碑  │ 6种答案  │ 8维加权          │
├──────────┴──────────┴──────────┴──────────┴──────────────────┤
│              KnowledgeBase Agent (RAG全链路)                   │
│        8格式解析 / 智能分块 / TF-IDF+ChromaDB / 引用追溯       │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                  数据层 (SQLite + SQLAlchemy ORM)              │
│          用户 / 画像 / 答题 / 知识库 / 资源 / 日志 / ...         │
└──────────────────────────────────────────────────────────────┘
```

## 功能特性

### 管理员端
- 与教师端功能一致，可管理所有学生数据、题库和系统设置
- 适合系统管理维护角色使用

### 教师端
- **数据分析仪表盘**：实时查看学生参与度、正确率、用时等核心指标
- **学生群像分析**：可视化展示学生群体的能力分布与学习特征
- **知识点掌握分析**：掌握各知识点的学习情况，识别薄弱环节
- **高级分析功能**：
  - 学习风格聚类分析 (KMeans)
  - 能力雷达图 (8维)
  - 学习效率分析
  - 预测预警系统
- **学生管理**：查看学生答题详情，追踪学习轨迹
- **题库管理**：添加、编辑、删除题目

### 学生端
- **10维个人画像**：对话式构建，清晰了解自身计算机能力的优势与不足
- **智能问答助手**：AI 学习助手，解答学习疑问（支持流式输出+追问纠错）
- **知识库 RAG 问答**：支持 8 种格式上传（TXT/MD/CSV/JSON/DOCX/PDF/PPTX/PPT），自动解析、分块、语义检索，并生成带来源引用的可信回答
- **个性化学习计划**：基于个人能力画像的定制化学习路径（甘特图/日历/列表三视图）
- **能力测试中心**：双方向题库（普通高校+民航特色），含逐题解析
- **学习报告**：8维雷达图 + 趋势分析 + 个性化改进建议
- **资源生成**：6种AI生成资源（讲义/导图/练习/阅读/视频脚本/代码实操）

### 多智能体系统
| Agent | 角色类比 | 核心功能 |
|-------|---------|---------|
| **ProfileBuilderAgent** | 班主任 | 通过自然语言对话构建10维学习画像 |
| **KnowledgeBaseAgent** | 图书管理员 | 管理课程资料上传、分块索引、TF-IDF/ChromaDB双后端检索和RAG问答 |
| **ResourceGeneratorAgent** | 教研组长 | 生成6种学习资源，支持ThreadPool并行 |
| **LearningPlannerAgent** | 教务主任 | 生成阶段化学习路径、周计划、甘特图视图和动态调整 |
| **TutorAgent** | 任课教师 | 提供多轮问答、追问纠错和个性化解释（SSE流式） |
| **EvaluatorAgent** | 考试中心 | 输出8维学习评估报告并反向更新画像/路径 |
| **AgentCoordinator** | 教导主任 | 全局协调、会话管理、Agent调度、执行日志 |

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **后端** | Python 3.9+ / Flask 3.x | 10个Blueprint路由蓝图 |
| **数据库** | SQLite (开发) / PostgreSQL (生产) | SQLAlchemy ORM |
| **前端** | HTML5 / CSS3 / JavaScript / Bootstrap 5 | 49个Jinja2模板 |
| **数据可视化** | ECharts 5 / Mermaid.js / Chart.js | 雷达图/甘特图/思维导图 |
| **机器学习** | scikit-learn | TF-IDF检索/KMeans聚类/余弦相似度 |
| **向量检索** | ChromaDB (可选) | 双后端自动切换 |
| **部署** | Docker + Nginx + Gunicorn/Waitress | 生产级容器化 |

## 目录结构

```
.
├── app/                       # 应用主目录
│   ├── __init__.py           # Flask应用工厂 (create_app)
│   ├── models/               # 数据模型 (User / Quiz / Profile / ...)
│   ├── routes/               # 路由控制器 (10个Blueprint)
│   │   ├── auth/            # 认证 (登录/注册/注销)
│   │   ├── main/            # 首页/导航
│   │   ├── student/         # 学生功能 (画像/计划/学习)
│   │   ├── teacher/         # 教师功能 (分析/管理)
│   │   ├── admin/           # 管理员功能
│   │   ├── quiz/            # 能力测试 (答题/评分/解析)
│   │   ├── analysis/        # 学习分析 (报告/趋势/建议)
│   │   ├── assistant/       # 智能问答 (对话/流式/多Agent)
│   │   ├── agent/           # Agent系统 (画像/资源/知识库)
│   │   └── api/             # REST API
│   ├── agents/              # 多智能体核心
│   │   ├── coordinator.py  # AgentCoordinator 协调器
│   │   ├── profile.py      # ProfileBuilderAgent
│   │   ├── knowledge.py    # KnowledgeBaseAgent
│   │   ├── resource.py     # ResourceGeneratorAgent
│   │   ├── planner.py      # LearningPlannerAgent
│   │   ├── tutor.py        # TutorAgent
│   │   └── evaluator.py    # LearningEvaluatorAgent
│   ├── templates/           # Jinja2 模板 (49个HTML)
│   ├── static/              # 静态资源 (CSS/JS/图片)
│   └── utils/               # 工具函数 (安全过滤/幻觉检测/...)
├── data/
│   └── knowledge_base/
│       └── computer_organization_sample/  # 课程样例包(6文件)
├── docs/                     # 文档套件 (8份v3.0)
│   ├── A3_SRS_requirements_spec.md       # 需求规格说明书
│   ├── A3_system_development_manual.md    # 系统开发说明书
│   ├── A3_testing_spec.md                # 测试说明书
│   ├── A3_user_manual.md                 # 用户使用手册
│   ├── A3_innovation_statement.md         # 项目创新说明书
│   ├── A3_open_source_notice.md          # 开源组件说明
│   ├── A3_user_journey_maps.md           # 用户使用路径图
│   ├── A3_document_checklist.md          # 文档清单
│   └── evidence/                         # 证据包
├── tests/                    # 单元测试 (pytest)
├── outputs/                  # 输出产物 (PPTX等)
├── instance/                 # 实例数据 (SQLite数据库)
├── run.py                    # 开发环境入口
├── wsgi.py                   # 生产环境 WSGI 入口
├── set_db.py                 # 数据库初始化与测试数据生成
├── deploy.py                 # 部署脚本
├── requirements.txt          # 完整 Python 依赖
├── requirements_light.txt    # 精简 Python 依赖
├── Dockerfile                # Docker 镜像配置
├── docker-compose.yml        # Docker 编排
├── nginx.conf                # Nginx 反向代理配置
├── install.bat               # Windows 一键安装脚本
└── start.bat                 # Windows 一键启动脚本
```

## 快速部署

### 方式一：Windows本地部署

1. **安装Python**
   - 下载Python 3.9+：https://www.python.org/downloads/
   - 安装时勾选"Add Python to PATH"

2. **克隆/下载项目**
   ```bash
   git clone https://github.com/lakeart/DaMo-ZhiXue.git
   cd DaMo-ZhiXue
   ```

3. **创建虚拟环境（推荐）**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

4. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

5. **初始化数据库**
   ```bash
   python set_db.py
   ```

6. **启动应用**
   ```bash
   python run.py
   ```

7. **访问应用**
   打开浏览器访问：http://127.0.0.1:5000

8. **查看赛题契合度演示页**
   打开：http://127.0.0.1:5000/competition-readiness

### 方式二：使用启动脚本（Windows，推荐演示）

双击运行 `start.bat`，脚本会自动：
- 检查Python环境
- 创建虚拟环境（如不存在）
- 安装依赖
- 初始化数据库
- 启动服务器

### 方式三：Docker部署（推荐生产环境）

```bash
# 构建并启动
docker-compose up -d

# 访问 http://localhost:80
```

## 默认账号

部署完成后可使用以下测试账号登录：

| 角色 | 用户名 | 密码 | 用途 |
|------|--------|------|------|
| 管理员 | `admin` | `admin123` | 全局管理+知识库管理+RAG演示 |
| 教师 | `teacher` | `teacher123` | 教师分析工作台+材料上传 |
| 学生 | `student` | `student123` | 核心功能全链路体验 |

> 运行 `python set_db.py` 后会额外生成 50 个模拟学生账号（学号即密码）。

## 环境变量配置

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|:--:|
| `SECRET_KEY` | Flask密钥 | dev-secret-key | - |
| `FLASK_ENV` | 运行环境 | development | - |
| `DATABASE_URL` | 数据库连接 | sqlite:///instance/quiz_system.db | - |
| `OPENAI_API_KEY` | OpenAI兼容模型密钥 | 空 | 可选 |
| `OPENAI_BASE_URL` | OpenAI兼容接口地址 | https://api.openai.com/v1 | 可选 |
| `OPENAI_MODEL` | 问答/生成模型名 | gpt-3.5-turbo | 可选 |
| `OLLAMA_BASE_URL` | 本地Ollama地址 | http://localhost:11434 | 可选 |
| `OLLAMA_MODEL` | 本地Ollama模型名 | llama2 | 可选 |
| `KNOWLEDGE_RETRIEVAL_BACKEND` | 检索后端 (auto/tfidf/chroma) | auto | 可选 |
| `CHROMA_DB_PATH` | ChromaDB持久化目录 | instance/chroma/knowledge | 可选 |

## 开发指南

### 运行测试
```bash
pytest tests/ -v -q
# 预期: 10 passed
```

### 编译检查
```bash
python -m compileall app
# 预期: 无语法错误
```

### 使用精简依赖
如果不需要完整功能（如机器学习分析），可安装精简依赖：
```bash
pip install -r requirements_light.txt
```

## 项目特色

1. **赛题高度契合**：围绕 A3 赛题的对话式画像、多智能体协同、个性化资源生成、反幻觉问答全面展开
2. **知识库 RAG 闭环**：完成文件上传→文档解析→分块索引→语义检索→带引用回答的完整链路，六层工程保障
3. **可视化学习规划**：学习路径支持甘特图、日历、列表三种视图，便于答辩演示与教学执行
4. **画像动态演进**：10维画像通过对话实时更新，置信度递增，全链路注入所有Agent决策
5. **评测回流闭环**：测试→评估→画像更新→路径调整，打破传统"测学分离"
6. **移动端知识卡片**：自动将生成资源切片为手机端复习卡片
7. **深色科技风 UI**：深墨蓝主题（`#0a1628`），突出多智能体节点与数据可视化
8. **一键部署**：`start.bat` Windows一键启动 + Docker容器化部署

## 项目统计

| 指标 | 数值 |
|------|:--:|
| Agent 数量 | 7 |
| 资源类型 | 6 |
| 画像维度 | 10 |
| 评估指标 | 8 (加权) |
| 文件格式支持 | 8 |
| HTML 模板 | 49 |
| 路由蓝图 | 10 |
| 测试项 | 68 (100%通过) |
| 文档 | 8份 v3.0 (~80,000+字) |
| 代码量 | ~50,000+行 |

## 参赛信息

- **赛事**：第十五届中国软件杯大赛
- **赛题**：A3-基于大模型的个性化资源生成与学习多智能体系统开发
- **作品名称**：大模智学：基于大模型的个性化资源生成与学习多智能体系统

## 许可证

本项目仅供学习交流使用。

## 联系方式

如有问题，请通过以下方式联系：
- 提交 Issue：https://github.com/lakeart/DaMo-ZhiXue/issues
- 发送邮件至项目维护者
