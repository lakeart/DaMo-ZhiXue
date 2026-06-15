# A3 系统开发说明书

**项目名称**：大模智学  
**赛题名称**：A3-基于大模型的个性化资源生成与学习多智能体系统开发  
**版本**：v3.0  
**最后更新**：2026-06-15

---

## 1. 项目概述

### 1.1 系统定位

"大模智学"是一个面向高校大学生的个性化学习多智能体系统，围绕软件杯A3赛题五大核心能力设计：对话式学习画像构建、多智能体协同资源生成、个性化学习路径规划与资源推送、智能辅导与即时答疑、学习效果评估与动态优化。

系统以Web应用为载体，覆盖课程教学辅助、自主学习辅导、知识库RAG问答、多模态资源生成与学习效果追踪等高校核心场景。

### 1.2 核心理念与技术哲学

本系统的本质不是"一个模型回答所有问题"的UI壳，而是将**学习画像**作为中心数据资产，让7类Agent分工协作，贯穿"对话了解学生→定制资源→规划路径→辅导答疑→评估反馈→动态调整"的完整学习闭环。

**关键设计哲学**：

| 原则 | 说明 | 实现体现 |
|------|------|---------|
| **画像驱动** | 所有智能体的输出都应反映学生的个体差异 | 10维画像注入所有Agent的System Prompt |
| **设计取证而非预测** | RAG模式优先于LLM自由生成 | temperature=0.2, System Prompt禁止编造 |
| **优雅降级** | 任何组件失败都不应导致系统不可用 | 每个Agent有独立降级策略，多层兜底 |
| **可解释优先** | 系统行为应可追溯、可验证 | execution_log、引用来源、Mock检测 |
| **工程化优先** | 竞赛代码也应有生产级质量 | 类型标注、单例模式、配置分离、Docker化 |

### 1.3 技术选型与决策理由

| 技术选择 | 决策理由 | 替代方案 | 为何不选替代 |
|---------|---------|---------|------------|
| **Python/Flask** | 生态成熟、文档完善、学习成本低、A3赛题主流选择 | Django/FastAPI | Django过重不适合竞赛演示；FastAPI异步优势在单机场景不明显 |
| **SQLite** | 零配置启动、便携单文件、SQLAlchemy ORM可平滑迁移 | PostgreSQL/MySQL | 外部数据库服务增加部署复杂度，竞赛演示场景不需要 |
| **Jinja2模板渲染** | Flask内置，服务端渲染无前端构建步骤 | React/Vue SPA | SPA需要额外构建工具链和API层，增加复杂度 |
| **Bootstrap 5 CDN** | 快速构建专业UI、响应式、丰富组件 | Tailwind CSS | Tailwind需要构建步骤，竞赛演示更看重开发速度 |
| **ECharts CDN** | 雷达图/趋势图开箱即用、中文文档完善 | Chart.js/D3.js | Chart.js无内置雷达图；D3.js学习曲线陡峭 |
| **Mermaid.js CDN** | 思维导图仅需文本语法、CDN引入即用 | draw.io/vis.js | 其他方案需要额外服务或构建步骤 |
| **scikit-learn TF-IDF** | 零额外依赖、中英文混合友好、性能足够 | 专用搜索引擎(ES) | ES需要Java运行时和额外服务，竞赛场景不适用 |
| **ThreadPoolExecutor** | Python标准库、无需额外依赖、4线程够用 | asyncio/celery | 竞赛演示单机场景，多线程即可满足并行需求 |

---

## 2. 需求分析与赛题对标

### 2.1 用户痛点深度分析

| 痛点 | 根因 | 传统解决方案的局限 | 本系统创新应对 |
|------|------|------------------|--------------|
| 资源碎片化 | 课程材料分散在多平台、版本混乱 | LMS(如Moodle)仅做文件存放，不支持语义检索 | 统一知识库+RAG语义检索 |
| 答疑时延高 | 师生比悬殊，教师无法7×24响应 | 教学论坛/邮件响应慢 | AI+知识库即时答疑，带来源引用 |
| 教学一刀切 | 200+学生难差异化教学 | 分层教学仅分2-3层 | 10维画像实现200+种个性化路径 |
| 测评浅层化 | 考试只给总分，无法定位薄弱点 | 仅统计各题正确率 | 8维雷达图+知识点级诊断+回流调整 |
| AI幻觉风险 | LLM可能生成与教材矛盾的回答 | 禁用AI或接受风险 | RAG六层保障+教师材料优先 |
| 学习持续动力不足 | 缺乏阶段性反馈和激励 | 考勤/平时分外部驱动 | 5级里程碑系统+内部动机激发 |

### 2.2 赛题逐项对标矩阵

| 赛题要求 | 系统实现 | 关键文件 | 完成度 |
|---------|---------|---------|:----:|
| 对话式学习画像自主构建 | ProfileBuilderAgent: 10维画像+LLM对话+关键词匹配+SQLite持久化 | `profile_agent.py` | ✅ 完整 |
| 多智能体协同资源生成(≥5种) | ResourceGeneratorAgent: 6种资源+6套SystemPrompt+并行生成 | `resource_agent.py` | ✅ 完整 |
| 个性化学习路径规划与资源推送 | LearningPlannerAgent: 优先级排序+渐进难度+5级里程碑+动态调整 | `planner_agent.py` | ✅ 完整 |
| 智能辅导与即时答疑 | TutorAgent: 6种答案+流式SSE+上下文保持+追问纠错 | `tutor_agent.py` | ✅ 完整 |
| 学习效果评估 | LearningEvaluatorAgent: 8维加权+ECharts雷达图+趋势+回流 | `evaluator_agent.py` | ✅ 完整 |
| 知识库与防幻觉 | KnowledgeBaseAgent: 8格式解析+双后端+LLM生成+引用+Mock过滤 | `knowledge_agent.py` | ✅ 完整 |
| 提供完整课程知识库样例 | 计算机组成原理6文件+全链路验证JSON证据 | `data/knowledge_base/` | ✅ 完整 |
| 现代AI产品交互规范 | Bootstrap 5+ECharts+Mermaid+流式SSE+进度提示 | `templates/`(49个) | ✅ 完整 |
| 工程化部署 | Docker+Windows一键启动+演示账号自动修正 | `Dockerfile`/`start.bat` | ✅ 完整 |
| 配套文档 | 8类Markdown文档+PPTX+证据包 | `docs/` | ✅ 完整 |

---

## 3. 系统总体架构

### 3.1 四层技术架构

```
┌──────────────────────────────────────────────────────────────────┐
│                        表现层 (Presentation)                      │
│  Bootstrap 5 + ECharts 5 + Mermaid.js + Font Awesome 6           │
│  Jinja2模板引擎 + 49个HTML模板 + 自定义深墨蓝科技风CSS              │
│  响应式布局 / 交互式可视化 / 流式SSE渲染 / 卡片式资源展示           │
├──────────────────────────────────────────────────────────────────┤
│                        路由层 (Routes)                            │
│  Flask Blueprint × 10 模块化路由                                  │
│  ├── main_bp (首页/赛题对照/成就/通知/笔记)                        │
│  ├── auth_bp (登录/注册/登出)                                     │
│  ├── quiz_bp (题库管理/答题/提交/错题本)                           │
│  ├── analysis_bp (数据分析/报告/画像/排名)                         │
│  ├── student_bp (学习计划/专项练习/详情)                           │
│  ├── intelligent_bp (智能问答主页面)                               │
│  ├── agent_bp (多智能体系统API)                                    │
│  ├── test_bp (能力测试中心)                                        │
│  ├── features_bp (功能展示)                                        │
│  └── extra_bp (扩展功能/PPT生成)                                   │
├──────────────────────────────────────────────────────────────────┤
│                      智能体层 (Multi-Agent)                        │
│  AgentCoordinator (单例) ← 全局调度中心                            │
│  ├── ProfileBuilderAgent     ← 10维画像 + LLM对话                 │
│  ├── ResourceGeneratorAgent  ← 6种资源 + 并行生成                  │
│  ├── LearningPlannerAgent    ← 路径规划 + 动态调整                 │
│  ├── TutorAgent              ← 6种答案 + 流式SSE                   │
│  ├── LearningEvaluatorAgent  ← 8维评估 + 数据回流                  │
│  ├── KnowledgeBaseAgent      ← RAG全链路 (563行)                   │
│  └── LLM Client              ← BaseLLM → OpenAI/Ollama            │
│                                                                   │
│  ContentSafetyFilter / HallucinationDetector (安全横切层)          │
├──────────────────────────────────────────────────────────────────┤
│                        数据层 (Data)                               │
│  SQLAlchemy ORM + SQLite (instance/quiz_system.db)                │
│  ├── StudentProfileModel       (student_profiles_agent)            │
│  ├── LearningResourceModel     (learning_resources_agent)          │
│  ├── LearningPathModel         (learning_paths_agent)              │
│  ├── AssessmentReportModel     (assessment_reports_agent)          │
│  ├── KnowledgeDocumentModel    (knowledge_documents_agent)         │
│  ├── KnowledgeChunkModel       (knowledge_chunks_agent)            │
│  ├── ChatHistoryModel          (chat_history_agent)                │
│  ├── DigitalHumanVideoTaskModel (digital_human_video_tasks)        │
│  └── User / Quiz / Feature等模型 (基础业务模型)                     │
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 路由与蓝图体系

| 蓝图变量 | URL前缀 | 核心职责 | 主要端点 |
|---------|--------|---------|---------|
| `main_bp` | `/` | 首页、赛题对照、成就中心、通知中心 | `/`, `/competition-readiness`, `/achievements` |
| `auth_bp` | `/auth` | 登录、注册、注销 | `/auth/login`, `/auth/register`, `/auth/logout` |
| `quiz_bp` | `/quiz` | 题库管理、答题提交、错题本 | `/quiz/`, `/quiz/create`, `/quiz/submit` |
| `analysis_bp` | `/analysis` | 数据分析、学习报告、画像展示 | `/analysis/`, `/analysis/report`, `/analysis/portrait` |
| `student_bp` | `/student` | 学习计划、专项练习、详情 | `/student/learning-plan`, `/student/practice` |
| `intelligent_bp` | `/intelligent-assistant` | 智能问答主页面 | `/intelligent-assistant/` |
| `agent_bp` | `/agent` | 多智能体系统API（核心） | `/agent/init`, `/agent/profile`, `/agent/resources`, `/agent/plan`, `/agent/ask`, `/agent/stream`, `/agent/evaluate`, `/agent/status`, `/agent/reset`, `/agent/export` |
| `test_bp` | `/test` | 能力测试中心 | `/test/assessment` |
| `features_bp` | `/features` | 功能展示页 | `/features/` |
| `extra_bp` | `/extra` | 扩展功能 | `/extra/ppt-generate` |

### 3.3 核心页面路由映射

| 页面名称 | 模板路径 | URL | 访问角色 | 核心展示内容 |
|---------|---------|-----|---------|------------|
| 首页 | `index.html` | `/` | 全部 | 系统入口、能力概览 |
| 登录页 | `auth/login.html` | `/auth/login` | 未登录 | 登录表单、自动填充 |
| 智能问答 | `intelligent_assistant/index.html` | `/intelligent-assistant` | 全部 | 多智能体协同中枢 |
| 学习画像 | `agent_system/learning_agent.html` | `/agent-system/learning-agent` | 学生 | 对话式画像构建 |
| 能力测试 | `test/assessment_pro.html` | `/test/assessment` | 学生 | 双方向专业化测评 |
| 学习报告 | `analysis/learning_report.html` | `/analysis/report` | 学生 | 8维雷达图+趋势 |
| 学习计划 | `student/learning_plan.html` | `/student/learning-plan` | 学生 | 甘特图+日历+列表 |
| 学生画像 | `analysis/student_portrait.html` | `/analysis/portrait` | 学生 | 10维画像详情 |
| 教师仪表盘 | `teacher_dashboard.html` | `/teacher_dashboard` | 教师 | 班级数据分析 |
| 学生管理 | `student/list.html` | `/student/list` | 教师/管理 | 学生列表与搜索 |
| 赛题对照 | `competition_readiness.html` | `/competition-readiness` | 全部 | 赛题完成度总览 |
| 成就中心 | `achievement_center.html` | `/achievements` | 学生 | 徽章与里程碑 |
| 错题本 | (测试结果内嵌) | 测试结果页 | 学生 | 错题汇总与重练 |

---

## 4. 智能体详细设计（深度阐述）

### 4.1 协调器 AgentCoordinator

**文件**：`app/multi_agent/coordinator.py`

#### 4.1.1 单例模式设计

```python
_coordinator_instance: Optional[AgentCoordinator] = None

def get_coordinator() -> AgentCoordinator:
    """全局单例协调器，确保所有请求共享同一组Agent实例"""
    global _coordinator_instance
    if _coordinator_instance is None:
        _coordinator_instance = AgentCoordinator()
    return _coordinator_instance
```

**为什么用单例**：
1. **状态一致性**：所有HTTP请求操作同一组Agent实例，避免会话分裂
2. **资源节省**：避免每次请求重新初始化LLM客户端和向量数据库连接
3. **执行日志连续性**：跨请求的execution_log记录在同一实例中
4. **竞赛演示友好**：单进程模型简化部署和调试

#### 4.1.2 核心职责

| 职责 | 实现方式 | 关键代码 |
|------|---------|---------|
| 会话管理 | `sessions: Dict[str, Session]` 字典，session_id(UUID4)为键 | `initialize_session()` / `reset_session()` |
| 工作流编排 | 按"画像→资源→路径→问答→评估"的顺序编排Agent调用链 | `orchestrate()` 方法 |
| 并行调度 | `ThreadPoolExecutor(max_workers=4)` 资源生成并行 | `generate_learning_resources()` |
| 执行追溯 | `execution_log: List[Dict]` 记录每次Agent调用 | 每条含{timestamp, agent, action, params, result} |
| 生命周期管理 | 负责7个Agent的创建、持有和销毁 | `__init__` 中初始化所有Agent |

#### 4.1.3 会话生命周期

```
[ 初始化阶段 ]
initialize_session(user_id, username)
  ├── 生成 session_id = str(uuid4())
  ├── 创建 Session 对象
  ├── 初始化 ProfileBuilderAgent
  │   └── profile_agent.init_profile(user_id, username)
  ├── sessions[session_id] = session
  └── 返回 {session_id, profile, welcome_message, suggested_questions}

[ 使用阶段 ]
... 各种Agent调用 (profile/resources/plan/ask/evaluate) ...

[ 查询阶段 ]
get_system_status()
  └── 返回: {
      session_id, user_id, username,
      profile_confidence, resources_count, path_steps_count,
      agents_status: {profile_builder, resource_generator, ...},
      execution_log_length
  }

[ 重置阶段 ]
reset_session()
  ├── 销毁所有Agent实例
  ├── 清空 sessions 字典
  └── 重新初始化 → 返回新的 session_id

[ 导出阶段 ]
export_session_data()
  └── 返回: {
      session_id, user_id, username,
      profile(完整10维), resources(所有已生成),
      path(完整路径), execution_log(完整日志)
  }
```

---

### 4.2 画像构建智能体 ProfileBuilderAgent

**文件**：`app/multi_agent/profile_agent.py`

#### 4.2.1 完整工作流

已在前文SRS §4.1.3详述，此处补充设计决策：

**为什么用关键词匹配+LLM双重机制？**
- LLM推断更智能但依赖网络/API，且存在"过度解读"风险
- 关键词匹配零延迟、100%可解释，但不理解复杂语义
- 两者互补：关键词匹配提供确定性的基准推断，LLM提供语义级细粒度理解

**为什么confidence = len(extracted_info)/10？**
- 简单直观：10个维度各贡献0.1置信度
- 渐进式：鼓励多轮对话逐步完善，而非一次填完
- 可监控：前端可展示"画像完成度40%"，激励学生继续对话

#### 4.2.2 关键代码片段

```python
def _extract_keywords(self, response: str) -> None:
    """从LLM响应中提取认知风格和学习速度"""
    # 认知风格关键词集 (中英文)
    cognitive_keywords = {
        'visual': ['看', '图', '画', '视觉', '眼睛', '图表', '可视化', '视频'],
        'verbal': ['读', '写', '说', '文字', '书籍', '阅读', '文本', '笔记'],
        'auditory': ['听', '声音', '音频', '讲', '口头', '讲座', '播客'],
        'kinesthetic': ['做', '动手', '实践', '试', '操作', '试验', '实验']
    }
    # 学习速度关键词集
    speed_keywords = {
        'fast': ['快', '迅速', '很快', '一下子', '不难'],
        'slow': ['慢', '需要时间', '反复', '仔细', '花时间', '困难']
    }
    
    resp_lower = response.lower()
    # 对每种认知风格计算关键词命中数，取最高者
    # 对学习速度同理
    # 仅在命中数超过阈值时才更新画像(避免误判)
```

---

### 4.3 资源生成智能体 ResourceGeneratorAgent

**文件**：`app/multi_agent/resource_agent.py`

#### 4.3.1 6套System Prompt设计原理

| 资源类型 | Prompt设计核心 | 关键约束 | 为何这样设计 |
|---------|-------------|---------|------------|
| COURSE_DOCUMENT | 资深教育专家+6段式结构 | 800-1500字，Markdown | 结构化确保完整覆盖，字数控制保证可读性 |
| MIND_MAP | 知识可视化专家+Mermaid语法 | 3-4层，每节点1-5词 | 层级过深不可读，过浅信息量不足 |
| EXERCISES | 出题专家+分层难度 | 5题型×3难度级 | 题型和难度分层匹配不同学习阶段 |
| EXTENDED_READING | 学术导师+资源推荐 | 3-5个，含链接 | 数量适中避免选择困难，含链接可直接访问 |
| VIDEO_SCRIPT | 视频策划+分镜格式 | 4镜头，3-5分钟 | 标准教学视频结构，时长适合碎片化学习 |
| CODE_PRACTICE | 程序员教育者+逐行注释 | PEP8，每函数≤30行 | 代码质量和可读性是教学材料的第一要求 |

#### 4.3.2 降级策略深度

```python
def _get_fallback_content(self, resource_type: ResourceType, topic: str) -> str:
    """每个资源类型都有预定义模板，确保LLM不可用时系统仍可输出"""
    fallbacks = {
        ResourceType.COURSE_DOCUMENT: f"""# {topic} - 课程讲义

## 学习目标
理解{topic}的核心概念、原理和应用场景。

## 核心概念
{topic}是计算机科学中的重要知识点...

## 详细讲解
（该部分在LLM可用时会生成个性化内容）

## 实例解析
此处将展示2-3个从易到难的实例...

## 应用场景
{topic}广泛应用于...

## 拓展阅读
建议参考教材相关章节和官方文档。
""",
        ResourceType.MIND_MAP: f"""mindmap
  {topic}
    核心概念
      定义
      特性
      分类
    关键原理
      原理1
      原理2
    应用场景
      场景A
      场景B
    常见问题
      误区1
      误区2
""",
        # ... 其他资源类型的降级模板
    }
    return fallbacks.get(resource_type, f"# {topic}\n\n（内容生成中...）")
```

---

### 4.4 知识库智能体 KnowledgeBaseAgent

**文件**：`app/multi_agent/knowledge_agent.py` (563行，系统最大单文件)

#### 4.4.1 文档解析架构的工程决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| DOCX解析方式 | zipfile + xml.etree | Python标准库零依赖，不需要python-docx |
| PDF解析方式 | PyPDF2(优先)→pypdf(回退) | 兼容多种PDF格式，pypdf是PyPDF2的继任者 |
| PPTX解析方式 | zipfile + xml.etree遍历slide.xml | 与DOCX同架构，代码复用 |
| PPT(旧版)解析 | 二进制正则提取UTF-16LE/ASCII | 唯一可行方式，无纯Python库支持旧格式 |
| 编码检测 | utf-8→gbk→gb18030→ignore | 覆盖中英文常见编码，ignore兜底防止崩溃 |

#### 4.4.2 智能分块算法详解

```python
def _chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
    """
    参数选择理由:
    - chunk_size=800: 约400中文字符，足以承载一个完整的概念段落
    - overlap=120: 约15%重叠，确保跨段落的语义不丢失
    - 切割优先级: \n > 。> ；> . — 优先在自然断句处切割
    """
    cleaned = re.sub(r'\n{3,}', '\n\n', text).strip()
    chunks = []
    start = 0
    
    while start < len(cleaned):
        end = min(len(cleaned), start + chunk_size)
        window = cleaned[start:end]
        
        # 智能切割点查找
        cut_positions = [
            ('\n', window.rfind('\n')),
            ('。', window.rfind('。')),
            ('；', window.rfind('；')),
            ('.', window.rfind('. ')),
        ]
        
        best_cut = max(cut_positions, key=lambda x: x[1])
        if best_cut[1] > chunk_size * 0.45:  # 仅当切割点足够靠后
            end = start + best_cut[1] + 1
        
        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = max(0, end - overlap)
    
    return chunks
```

#### 4.4.3 RAG回答生成的工程细节

**System Prompt设计原则**：
1. **角色限定**："高校课程知识库问答助手"——明确领域边界
2. **行为约束**："仅根据提供的材料回答，禁止编造"——硬约束
3. **失败模式明确**："材料不足时明确说资料不足"——给LLM"允许说不知道"的许可
4. **格式规范**："引用时使用[来源1]格式"——统一输出格式

**Mock回答检测的必要性**：
当LLM API不可用但返回了通用回复（如"感谢您的提问，这是一个很好的问题..."），系统需要识别并触发降级：
```python
def _looks_like_mock_answer(answer: str) -> bool:
    mock_patterns = [
        r'感谢您的提问',
        r'这是一个很好的问题',
        r'作为AI助手',
        r'我无法回答',
        r'对不起.*无法',
    ]
    return any(re.search(p, answer) for p in mock_patterns)
```

---

### 4.5 学习规划智能体 LearningPlannerAgent

**文件**：`app/multi_agent/planner_agent.py`

#### 4.5.1 难度曲线设计原理

渐进式难度设计的理论基础来自**维果茨基最近发展区理论**和**布鲁姆掌握学习理论**：

| 阶段 | 难度 | 心理学依据 |
|------|:---:|---------|
| 入门期(0-20%) | easy | 建立自我效能感(bandura)，防止初期挫败导致的放弃 |
| 过渡期(20-40%) | easy/medium交替 | 逐步引入挑战，维持"恰好可应对"的状态 |
| 核心期(40-70%) | medium | 进入常规学习区，稳步推进 |
| 深化期(70-90%) | medium/hard交替 | 增加难度挑战，检验掌握程度 |
| 冲刺期(90-100%) | hard | 最终检验综合应用能力 |

#### 4.5.2 周计划分配算法

```python
def get_weekly_plan(path, weekly_hours=10):
    total_minutes = sum(s.duration for s in path.steps)
    total_weeks = math.ceil(total_minutes / (weekly_hours * 60))
    
    daily_hours = weekly_hours / 7
    plan = []
    step_idx = 0
    
    for week in range(total_weeks):
        for day in range(7):
            remaining = daily_hours * 60  # 当天剩余分钟
            day_tasks = []
            
            while remaining > 0 and step_idx < len(path.steps):
                step = path.steps[step_idx]
                if step.duration <= remaining:
                    day_tasks.append({
                        'step': step.step_number,
                        'topic': step.topics[0],
                        'duration': step.duration,
                        'difficulty': step.difficulty
                    })
                    remaining -= step.duration
                    step_idx += 1
                else:
                    break
            
            plan.append({
                'week': week + 1,
                'day': day + 1,
                'day_name': ['周一','周二','周三','周四','周五','周六','周日'][day],
                'tasks': day_tasks,
                'total_hours': round((daily_hours * 60 - remaining) / 60, 1)
            })
    
    return {"weekly_plan": plan, "total_weeks": total_weeks}
```

---

### 4.6 智能辅导智能体 TutorAgent

**文件**：`app/multi_agent/tutor_agent.py`

#### 4.6.1 流式回答技术实现（SSE）

流式回答对用户体验至关重要——3秒以上等待会导致用户感知延迟，逐字展示则保持"系统正在工作"的心理反馈：

```
前端: EventSource('/agent/stream?question=...')
      ↓ SSE连接
后端: Response(content_type='text/event-stream')
      ↓ yield "data: {type: 'start'}\n\n"
      ↓ for chunk in LLM.stream_chat():
      ↓     yield "data: {type: 'chunk', content: chunk}\n\n"
      ↓ yield "data: {type: 'end'}\n\n"

前端: eventSource.onmessage = (e) => {
          const data = JSON.parse(e.data);
          if (data.type === 'chunk') answerDiv.innerText += data.content;
          if (data.type === 'end') eventSource.close();
      }
```

---

### 4.7 学习评估智能体 LearningEvaluatorAgent

**文件**：`app/multi_agent/evaluator_agent.py`

#### 4.7.1 指标权重设计的理论依据

| 指标 | 权重 | 设计依据 |
|------|:---:|---------|
| 知识掌握度 | 25% | 核心指标，衡量"学到了什么" |
| 练习准确率 | 20% | 直接反映应用能力，"能做对多少" |
| 概念理解度 | 15% | 概念是知识体系的基础单元 |
| 问题解决能力 | 15% | 高难度题目反映"融会贯通"的能力 |
| 学习效率 | 10% | 衡量"投入产出比"，鼓励高效学习 |
| 时间管理 | 5% | 学习纪律的侧面反映 |
| 学习持续性 | 5% | 长期坚持比短期冲刺更重要 |
| 学习投入度 | 5% | 学习态度和深度的综合反映 |

> 前4项(75%)聚焦"学习结果"，后4项(25%)关注"学习过程"——平衡结果导向与过程导向。

---

## 5. LLM集成与安全管理

### 5.1 LLM客户端架构

**文件**：`app/multi_agent/llm_client.py`

```
BaseLLM (抽象基类)
├── chat(messages, temperature, max_tokens, **kwargs) → str
├── stream_chat(messages, **kwargs) → Iterator[str]
└── generate_with_retry(messages, max_retries=3, **kwargs) → str
    └── 实现: 循环调用chat()，捕获异常，指数退避重试

OpenAIClient(BaseLLM)
├── 端点: POST {base_url}/v1/chat/completions
├── 鉴权: Bearer {api_key}
└── 流式: stream=true → SSE逐行解析

LocalLLM(BaseLLM)
├── 端点: POST {base_url}/api/chat
├── 模型: 由OLLAMA_MODEL环境变量指定
└── 流式: stream=true → JSON行解析
```

### 5.2 内容安全过滤器 ContentSafetyFilter

**文件**：`app/multi_agent/__init__.py`

```python
class ContentSafetyFilter:
    SENSITIVE_PATTERNS = [
        r'违法', r'暴力', r'色情',  # ... 具体模式
    ]
    MAX_INPUT_LENGTH = 50000
    
    @staticmethod
    def filter(content: str) -> Tuple[bool, str]:
        """返回(is_safe, reason)"""
        if len(content) > ContentSafetyFilter.MAX_INPUT_LENGTH:
            return False, "输入过长"
        for pattern in ContentSafetyFilter.SENSITIVE_PATTERNS:
            if re.search(pattern, content):
                return False, f"包含敏感内容"
        return True, ""
    
    @staticmethod
    def sanitize(content: str) -> str:
        """清理不可见字符和多余空白"""
        # 移除零宽字符、控制字符(U+0000-U+001F除\t\n\r)
        # 统一换行为\n
        # 合并多余空白
        return cleaned
```

### 5.3 幻觉检测器 HallucinationDetector

```python
class HallucinationDetector:
    UNCERTAINTY_PATTERNS = [
        r'据说', r'大概是', r'也许是', r'似乎',
        r'可能.*应该', r'不太确定', r'有待验证',
    ]
    
    FAKE_CITATION_PATTERNS = [
        r'《[^》]{2,30}》.*说',
        r'根据.{2,20}的研究',
    ]
    
    TRUSTED_DOMAINS = [
        '计算机科学', '数学', '物理', '数据结构',
        '算法', '操作系统', '网络', '数据库',
    ]
    
    @staticmethod
    def check_factuality(content: str, topic: str) -> Tuple[bool, List[str]]:
        """返回(is_factual, warnings)"""
        warnings = []
        
        for pattern in HallucinationDetector.UNCERTAINTY_PATTERNS:
            if re.search(pattern, content):
                warnings.append(f"检测到不确定性表达: {pattern}")
        
        for pattern in HallucinationDetector.FAKE_CITATION_PATTERNS:
            if re.search(pattern, content):
                warnings.append(f"检测到可能虚假的引用: {pattern}")
        
        return len(warnings) == 0, warnings
```

---

## 6. 数据模型设计

### 6.1 核心Agent数据模型

**文件**：`app/models/agent_models.py`

| 模型名 | 对应智能体 | 表名 | 关键JSON字段 |
|--------|----------|------|------------|
| `StudentProfileModel` | ProfileBuilder | `student_profiles_agent` | profile_data(10维JSON) |
| `LearningResourceModel` | ResourceGenerator | `learning_resources_agent` | content(完整Markdown/JSON) |
| `LearningPathModel` | LearningPlanner | `learning_paths_agent` | path_data(步骤列表JSON) |
| `AssessmentReportModel` | Evaluator | `assessment_reports_agent` | report_data(8维JSON) |
| `ChatHistoryModel` | Tutor/Profile | `chat_history_agent` | 对话历史 |
| `KnowledgeDocumentModel` | KnowledgeBase | `knowledge_documents_agent` | 文档元数据 |
| `KnowledgeChunkModel` | KnowledgeBase | `knowledge_chunks_agent` | keywords(JSON数组) |
| `DigitalHumanVideoTaskModel` | 扩展功能 | `digital_human_video_tasks` | 视频任务数据 |

### 6.2 JSON字段的设计哲学

多个Agent模型使用JSON字段存储结构化数据，而非拆分为多个关系表：

| 理由 | 说明 |
|------|------|
| **画像弹性** | 10维画像可能扩展为12维或15维，JSON字段无需迁移 |
| **查询简单** | 大多数查询以user_id为主键，不需要跨JSON字段JOIN |
| **读写效率** | 画像作为整体读写的概率远高于按维度部分读取 |
| **竞赛工程** | 减少表数量和迁移脚本，降低答辩出错风险 |

---

## 7. 前端技术栈与设计系统

### 7.1 技术组件清单

| 技术 | 版本 | 引入方式 | 用途 |
|------|:---:|---------|------|
| Bootstrap 5 | 5.3.x | CDN | 网格布局、导航栏、卡片、按钮、表单 |
| ECharts | 5.4.x | CDN | 雷达图、趋势折线图、仪表盘图表 |
| Mermaid.js | 10.x | CDN | 思维导图实时渲染 |
| Font Awesome | 6.4.x | CDN | 图标系统(资源卡片图标、导航图标) |
| 自定义CSS | - | 内联+独立文件 | 深墨蓝科技风主题、卡片动效 |

### 7.2 设计语言：深墨蓝科技风

| 设计元素 | 规范 |
|---------|------|
| 主色调 | #1a1a2e (深墨蓝背景) → #16213e (次级背景) |
| 强调色 | #0f3460 (深蓝) → #4364F7 (亮蓝CTA) |
| 成功色 | #00C9A7 (青绿) — 用于完成状态、里程碑解锁 |
| 警告色 | #F9A826 (琥珀) — 用于薄弱指标、待改进 |
| 危险色 | #E84545 (珊瑚红) — 用于错误、需改进 |
| 卡片样式 | 圆角8px、轻微阴影(0 2px 10px rgba(0,0,0,0.3))、悬停上浮动效 |
| 字体 | 系统默认中文字体栈: -apple-system, "Microsoft YaHei", sans-serif |
| 代码块 | 深色背景 #0d1117，等宽字体 Consolas/Monaco |

### 7.3 Mermaid思维导图渲染

```html
<!-- 模板中 -->
<div class="mermaid">
mindmap
  数据结构
    线性结构
      数组
      链表
        单链表
        双向链表
      栈
      队列
    树形结构
      二叉树
      二叉搜索树
      AVL树
    图形结构
      有向图
      无向图
</div>

<!-- Mermaid.js自动渲染为交互式思维导图 -->
```

---

## 8. 部署方案

### 8.1 本地开发启动

```bash
# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python set_db.py

# 启动服务
python run.py
# 访问: http://127.0.0.1:5000
```

### 8.2 Windows一键启动

`start.bat` 执行流程：
```
1. 检测Python环境 (.venv优先 → venv → 系统python)
2. 检测.env文件 (密钥配置)
3. 启动Flask开发服务器 (PYTHONUTF8=1)
4. 浏览器访问: http://127.0.0.1:5000
```

### 8.3 Docker部署

```bash
# 构建并启动
docker compose up -d --build

# 初始化数据库(首次)
docker compose exec web python set_db.py

# 访问: http://localhost:80

# 日志
docker compose logs -f web

# 停止
docker compose down
```

### 8.4 演示环境检查清单

| 检查项 | 命令/方法 | 预期结果 |
|--------|---------|---------|
| Python版本 | `python --version` | ≥ 3.8 |
| 依赖完整 | `pip check` | No broken requirements |
| 语法编译 | `python -m compileall app` | 无语法错误 |
| 测试通过 | `pytest tests -q` | 10 passed |
| 服务启动 | `python run.py` / `start.bat` | http://127.0.0.1:5000 可访问 |
| 页面冒烟 | 逐一访问核心URL | 全部返回200 |
| Docker可用 | `docker compose up -d` | 容器启动成功 |

---

## 9. 项目目录结构

```
damo-zhixue/
├── app/
│   ├── __init__.py                 # Flask应用工厂 create_app()
│   ├── multi_agent/                # 🔴 多智能体核心模块
│   │   ├── __init__.py             #   数据类(ResourceType/Session等)、安全过滤器
│   │   ├── coordinator.py          #   AgentCoordinator 协调器(会话/调度/日志)
│   │   ├── profile_agent.py        #   ProfileBuilderAgent (10维画像)
│   │   ├── resource_agent.py       #   ResourceGeneratorAgent (6种资源)
│   │   ├── planner_agent.py        #   LearningPlannerAgent (路径规划)
│   │   ├── tutor_agent.py          #   TutorAgent (智能辅导)
│   │   ├── evaluator_agent.py      #   LearningEvaluatorAgent (效果评估)
│   │   ├── knowledge_agent.py      #   KnowledgeBaseAgent (RAG全链路, 563行)
│   │   └── llm_client.py           #   LLM接口 (BaseLLM/OpenAI/Ollama)
│   ├── models/
│   │   ├── user.py                 #   用户模型 (User)
│   │   ├── agent_models.py         #   智能体数据模型 (8个ORM模型)
│   │   ├── quiz.py                 #   题库模型 (Question/QuizSubmission)
│   │   └── ...                     #   其他业务模型
│   ├── routes/
│   │   ├── agent_system.py         #   /agent/* 多智能体API (核心)
│   │   ├── main.py                 #   首页、赛题对照、成就中心等
│   │   ├── auth.py                 #   登录、注册、登出
│   │   ├── quiz.py                 #   题库管理、答题、提交
│   │   ├── analysis.py             #   数据分析、学习报告、画像展示
│   │   ├── student.py              #   学习计划、专项练习、详情
│   │   ├── intelligent_assistant.py #  智能问答主页面
│   │   ├── test.py                 #   能力测试中心
│   │   ├── nav.py                  #   导航辅助路由
│   │   ├── features.py             #   功能展示页
│   │   └── extra_features.py       #   扩展功能
│   ├── templates/                  #   49个Jinja2 HTML模板
│   │   ├── base.html / base_pro.html / base_unified.html  # 基础布局
│   │   ├── index.html              #   首页
│   │   ├── components/             #   可复用组件 (导航栏等)
│   │   ├── auth/                   #   认证相关页面
│   │   ├── analysis/               #   数据分析页面
│   │   ├── student/                #   学生端页面
│   │   ├── quiz/                   #   题库页面
│   │   ├── test/                   #   测试中心页面
│   │   ├── agent_system/           #   智能体系统页面
│   │   └── intelligent_assistant/  #   智能问答页面
│   ├── static/                     #   静态资源 (CSS/JS/图片)
│   └── utils/                      #   工具函数
├── data/
│   └── knowledge_base/
│       └── computer_organization_sample/  # 课程知识库样例包 (6文件)
├── docs/                           #   参赛文档 (8份MD + 1份DOCX + evidence/)
├── outputs/                        #   答辩PPT等输出
├── tests/                          #   自动化测试
├── instance/                       #   SQLite数据库 (运行时生成)
├── screenshots/                    #   系统截图
├── run.py                          #   开发环境启动入口
├── wsgi.py                         #   生产环境WSGI入口
├── set_db.py                       #   数据库初始化与测试数据
├── start.bat                       #   Windows一键启动
├── install.bat                     #   Windows一键安装
├── deploy_to_server.sh             #   Linux服务器部署脚本
├── Dockerfile                      #   Docker镜像
├── docker-compose.yml              #   Docker编排
├── nginx.conf                      #   Nginx反向代理
├── requirements.txt                #   完整Python依赖
├── requirements_light.txt          #   精简依赖
├── .env.example                    #   环境变量模板
├── .gitignore                      #   Git忽略规则
├── package.json                    #   项目元信息
└── README.md                       #   项目说明
```

---

## 10. 创新点与技术亮点总结

### 10.1 架构创新

1. **画像驱动全链路**：10维画像不是终点，而是贯穿资源生成、路径规划、辅导问答的输入依据——每个Agent的输出都因画像不同而不同
2. **多Agent专业分工**：7类智能体按教学角色划分(而非功能模块划分)，每类有独立System Prompt和降级策略，架构清晰可扩展
3. **协调器单例调度**：全局单例管理会话和Agent调用链，4线程并行资源生成，执行日志可追溯

### 10.2 工程创新

4. **RAG六层保障**：8格式解析→智能分块→双后端检索→LLM证据生成→引用追溯→多重兜底，构成完整的可信问答工程链路
5. **评测回流闭环**：测验→8维评估→雷达图→画像更新→路径动态调整，数据在系统内循环驱动优化
6. **零配置启动**：SQLite免安装数据库 + 自动编码检测 + 一键启动脚本 + 演示账号自动修正

### 10.3 场景创新

7. **教师深度参与**：教师不仅是数据查看者，更是知识来源——教师材料优先于LLM自由知识
8. **竞赛化表达**：甘特图/雷达图/思维导图/赛题对照页，为答辩演示量身定制的可视化方案
9. **双重保障设计**：每个Agent都有正常模式和降级模式，系统在任何条件下都有合理输出

---

## 11. 开发环境搭建指南

### 11.1 推荐开发环境

| 工具 | 推荐版本 | 用途 |
|------|---------|------|
| Python | 3.9 - 3.12 | 运行环境 |
| VS Code | latest | IDE(推荐Python扩展) |
| Git | latest | 版本控制 |
| Docker Desktop | latest | 容器化测试 |
| Ollama | latest | 本地LLM测试(可选) |

### 11.2 VS Code配置建议

```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "ms-python.black-formatter"
    }
}
```

### 11.3 调试配置

```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Flask Debug",
            "type": "python",
            "request": "launch",
            "module": "flask",
            "env": { "FLASK_APP": "run.py", "FLASK_DEBUG": "1" },
            "args": ["run", "--host=0.0.0.0", "--port=5000"],
            "jinja": true
        }
    ]
}
```

---

*本开发说明书基于大模智学 v3.0 完整源码编写，所有功能描述均可对应到 `app/multi_agent/` 中的具体代码实现。*
