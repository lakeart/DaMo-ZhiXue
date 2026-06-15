# A3 软件需求规格说明书 (SRS)

**项目名称**：大模智学  
**赛题名称**：A3-基于大模型的个性化资源生成与学习多智能体系统开发  
**版本**：v2.0  
**最后更新**：2026-06-15

---

## 1. 引言

### 1.1 编写目的

本文档用于明确"大模智学"项目在软件杯 A3 赛题下的完整功能边界、用户角色定义、核心业务流程、非功能约束与验收标准。作为开发、测试、答辩及后续迭代的统一依据，确保所有参与方对系统目标有一致理解。

### 1.2 适用范围

系统面向三类核心用户——**学生**、**教师**与**管理员**，覆盖六大业务模块：
1. 对话式学习画像构建
2. 多智能体协同资源生成（8种资源类型）
3. 个性化学习路径规划与资源推送
4. 智能辅导与RAG知识库问答
5. 学习效果评估与动态优化
6. 工程化部署与演示

### 1.3 术语与缩写

| 术语 | 说明 |
|------|------|
| 学习画像 (Profile) | 对学生目标、基础、偏好、薄弱点、节奏等维度的结构化描述，当前包含10个维度 |
| 多智能体 (Multi-Agent) | 由画像、资源生成、学习规划、辅导、评估、知识库、协调器等7类角色组成的协同系统 |
| RAG (Retrieval-Augmented Generation) | 检索增强生成：先检索课程资料，再基于证据由LLM生成带引用回答，降低幻觉风险 |
| 课程知识库样例包 | 用于上传验证的一组真实课程讲义、题库、术语表和复习提纲（计算机组成原理） |
| LLM | 大语言模型 (Large Language Model)，支持OpenAI兼容接口 |
| TF-IDF | 词频-逆文档频率，当前默认语义检索算法 |
| ChromaDB | 可选向量数据库后端，支持嵌入向量检索 |

---

## 2. 项目背景与目标

### 2.1 业务背景与痛点分析

高校学生在自主学习中面临系统性困难：
1. **资源分散**：课程讲义、题库、视频、教材散布多个平台，缺乏按个人需求整合的入口
2. **答疑不及时**：课下疑问无法即时获得基于课程材料的准确回答，搜索引回噪声大
3. **计划缺个性化**：统一教学计划难以兼顾不同基础、目标和学习偏好的个体差异
4. **测评与学习脱节**：测试结果停留在总分层面，缺乏针对性改进建议和后续学习路径指导
5. **知识幻觉风险**：通用AI聊天工具可能给出与课程教材不一致的回答，缺乏可追溯性

### 2.2 建设目标

1. **对话驱动**：用自然语言对话快速构建并动态更新学生学习画像（10维）
2. **多智能体协同**：7类智能体分工协作，按需生成8种个性化学习资源
3. **RAG可信问答**：知识库优先、证据引用、资料不足拦截，降低开放式问答的幻觉风险
4. **测评闭环**：能力测试→学习报告→画像更新→路径调整，形成持续优化循环
5. **工程化落地**：形成可运行、可部署、可演示的竞赛系统样机，配套完整文档与证据包

---

## 3. 用户角色与权限

### 3.1 学生

默认演示账号：`student / student123`

| 权限项 | 说明 |
|--------|------|
| 登录系统 | 查看个人学习入口面板 |
| 能力测试 | 参与普通高校/民航特色方向的专业化测评，查看逐题解析 |
| 学习报告 | 查看8维雷达图、趋势分析、个性化建议 |
| 学习计划 | 获取甘特图/日历/列表视图的个性化学习路径 |
| 知识库管理 | 上传课程资料（8种格式），管理已上传文档 |
| 知识库问答 | 基于已上传资料的RAG问答，获取带来源引用的回答 |
| 资源生成 | 基于学习画像生成课程讲义、思维导图、练习题等 |
| 智能问答 | 多模态辅导问答，支持追问纠错 |
| 学习画像 | 查看和更新个人10维学习画像 |

### 3.2 教师

默认演示账号：`teacher / teacher123`

| 权限项 | 说明 |
|--------|------|
| 登录系统 | 查看教师分析工作台 |
| 上传教学材料 | 上传课程讲义、实验文档、题库等作为知识库来源 |
| 查看学生表现 | 浏览学生学习数据与评估结果 |
| 教学资源管理 | 管理课程知识库内容 |

### 3.3 管理员

默认演示账号：`admin / admin123`

| 权限项 | 说明 |
|--------|------|
| 系统管理 | 维护演示账号，管理数据库 |
| 全局监控 | 查看系统运行状态，管理所有用户数据 |
| 部署保障 | 确保答辩演示环境稳定运行 |

---

## 4. 功能需求（详细规格）

### 4.1 模块一：对话式学习画像构建

#### 4.1.1 功能描述
系统通过自然语言对话自动采集学生信息，构建并持续更新10维学习画像，该画像作为后续所有智能体决策的输入依据。

#### 4.1.2 画像维度定义

| 编号 | 维度名称 | 数据类型 | 取值范围 | 采集方式 |
|:----:|---------|---------|---------|---------|
| D1 | 知识基础 | `Dict[str, float]` | 各知识点 0.0~1.0 | 答题数据推断 |
| D2 | 认知风格 | `str` | visual/verbal/auditory/kinesthetic | 对话关键词提取 |
| D3 | 易错点偏好 | `List[Dict]` | 错误类型列表 | 答题数据分析 |
| D4 | 学习速度 | `str` | slow/medium/fast | 对话关键词+答题速度 |
| D5 | 兴趣方向 | `List[str]` | 兴趣领域列表 | 对话采集 |
| D6 | 学习目标 | `List[str]` | 目标描述列表 | 对话采集 |
| D7 | 偏好知识点 | `List[str]` | 偏好主题列表 | 对话采集 |
| D8 | 薄弱知识点 | `List[str]` | 薄弱主题列表 | 答题+对话推断 |
| D9 | 学习习惯 | `Dict[str, Any]` | 时间/频率/方式 | 数据推断 |
| D10 | 可用时间 | `Dict[str, int]` | 周各时段小时数 | 对话采集 |

#### 4.1.3 功能流程

```
用户输入 → ContentSafetyFilter安全检查
         → profile_agent.process_message()
            ├── 更新 conversation_history
            ├── 构建上下文 prompt (含已知画像信息)
            ├── 调用 LLM (temperature=0.8) 生成响应
            ├── 正则提取响应中的JSON画像更新
            ├── 关键词匹配推断认知风格/学习速度
            └── 更新 profile.confidence = len(extracted_info)/10
         → 返回 {response, profile_update, suggested_questions, profile}
```

#### 4.1.4 交互规格

| 项目 | 规格 |
|------|------|
| 输入 | 自然语言字符串，无长度限制（内部>50000字符拦截） |
| 输出 | `{response: str, profile_update: Dict, suggested_questions: List[str], profile: Dict}` |
| LLM模型 | OpenAI兼容接口，temperature=0.8 |
| System Prompt | 专业教育顾问角色，苏格拉底式提问 |
| 安全意识 | ContentSafetyFilter敏感词过滤 |
| 降级策略 | 预定义模板响应 `_get_fallback_response()` |

---

### 4.2 模块二：知识库管理（RAG）

#### 4.2.1 功能描述
知识库管理智能体负责课程文档的上传、解析、分块、索引、语义检索和基于LLM的RAG问答生成，是整个系统"可信回答"的核心引擎。

#### 4.2.2 支持的文件格式

| 格式 | 扩展名 | 解析方式 | 稳定性 |
|------|--------|---------|:------:|
| 纯文本 | `.txt` | 编码自动检测(utf-8→gbk→gb18030) | ✅ 稳定 |
| Markdown | `.md` | 同纯文本 | ✅ 稳定 |
| CSV | `.csv` | 同纯文本 | ✅ 稳定 |
| JSON | `.json` | 同纯文本 | ✅ 稳定 |
| Word文档 | `.docx` | OpenXML ZIP解析 (word/document.xml) | ✅ 稳定 |
| PDF文档 | `.pdf` | PyPDF2/PyPDF 逐页提取 | ✅ 稳定 |
| PowerPoint新 | `.pptx` | OpenXML ZIP解析 (ppt/slides/slide*.xml) | ✅ 稳定 |
| PowerPoint旧 | `.ppt` | 二进制文本提取 (UTF-16LE+ASCII) | ⚠️ 兼容提取 |

#### 4.2.3 文档处理管线

```
文件上传 → 校验扩展名 ∈ SUPPORTED_EXTENSIONS
        → 按扩展名路由解析器:
           ├── .docx → _extract_docx_text() [ZIP+XML]
           ├── .pdf  → _extract_pdf_text() [PyPDF2/PyPDF]
           ├── .pptx → _extract_pptx_text() [ZIP+XML/slide]
           ├── .ppt  → _extract_ppt_text() [二进制正则]
           └── 其他  → 编码检测文本读取
        → 文本校验: len(strip) ≥ 20
        → SHA256去重检查 (content_hash)
        → 文本分块 _chunk_text(chunk_size=800, overlap=120)
           └── 优先在换行/句号处切割
        → 关键词提取 _extract_keywords(limit=12)
        → 创建 KnowledgeDocumentModel + KnowledgeChunkModel
        → 同步到向量存储 (ChromaDB可用时)
        → 返回 {document, chunks, deduplicated}
```

#### 4.2.4 检索架构（双后端设计）

**后端一：TF-IDF 语义检索（默认）**
- 使用 scikit-learn `TfidfVectorizer(analyzer='char_wb', ngram_range=(2,4), max_features=6000)`
- 计算所有分块与查询的余弦相似度
- 回退方案：基于Jaccard词重叠的字符级匹配

**后端二：ChromaDB 向量检索（可选启用）**
- 配置环境变量 `KNOWLEDGE_RETRIEVAL_BACKEND=chroma`
- 使用 ChromaDB 内置嵌入模型，自动构建向量索引
- 通过 `collection.query()` 进行语义检索
- 不可用时自动降级到 TF-IDF

#### 4.2.5 RAG问答生成流程

```
用户提问 → knowledge_agent.answer(user_id, question, top_k=4)
          ├── search() 检索 top_k 相关分块
          ├── 无结果 → 返回"资料不足"提示 (confidence=0)
          ├── 有结果 → _generate_rag_answer():
          │   ├── 构建系统提示: "仅根据材料回答，禁止编造"
          │   ├── 拼装检索上下文: [来源1] 文档 + 片段
          │   ├── 调用 LLM (temperature=0.2, max_tokens=900)
          │   ├── 检查是否mock回答 → 回退模板拼接
          │   ├── 补全"参考来源"引用列表
          │   └── 幻觉检测 HallucinationDetector.check_factuality()
          └── 返回 {answer, citations, confidence, warnings, retrieval}
```

#### 4.2.6 反幻觉与安全机制

| 机制 | 实现方式 | 触发条件 |
|------|---------|---------|
| 知识库优先 | RAG回答仅基于检索材料，prompt禁止编造 | 知识库模式下始终生效 |
| 资料不足拦截 | 无检索结果时返回提示而非强结论 | `search_results`为空 |
| 引用回答 | 答案末尾附加 `[来源N]` 标记 | 有检索结果时自动附加 |
| LLM调用失败回退 | 模板拼接降级回答 | LLM异常/mock回答检测 |
| 双重幻觉检测 | `HallucinationDetector.check_factuality()` | 回答生成后 |
| Mock回答过滤 | `_looks_like_mock_answer()` | 检测"感谢您的提问"等模式 |

---

### 4.3 模块三：多智能体资源生成中心

#### 4.3.1 功能描述
资源生成智能体基于学生画像和指定知识点，利用LLM协同生成8种类型的个性化学习资源，是多智能体系统功能的集中体现。

#### 4.3.2 资源类型详细规格

**资源1：课程讲义 (COURSE_DOCUMENT)**

| 项目 | 规格 |
|------|------|
| System Prompt | 资深教育专家角色 |
| 内容结构 | 概述 → 核心概念 → 详细讲解 → 实例解析 → 应用场景 → 拓展阅读 |
| 输出格式 | Markdown，支持代码块/表格/列表 |
| 长度控制 | 800-1500字 |
| 画像适配 | 结合认知风格调整表达方式 |
| 预估时长 | 15分钟 |
| 难度估算 | fast→hard, slow→easy, default→medium |
| 降级内容 | 预定义Markdown模板 |

**资源2：思维导图 (MIND_MAP)**

| 项目 | 规格 |
|------|------|
| System Prompt | 知识可视化专家角色 |
| 输出格式 | Mermaid `mindmap` 语法 |
| 层级结构 | 根节点+主分支+子分支，一般3-4层 |
| 节点规范 | 每节点1-5个关键词 |
| 覆盖范围 | 知识点核心要素和关联关系 |
| 预估时长 | 10分钟 |
| 降级内容 | 预定义Mermaid模板 |
| 前端渲染 | Mermaid.js实时渲染为交互式思维导图 |

**资源3：练习题 (EXERCISES)**

| 项目 | 规格 |
|------|------|
| 题型 | 选择题、填空题、判断题、简答题、编程题 |
| 难度分层 | 基础题/中等题/进阶题 |
| 数量 | 每种类型2-3道，合计10-15道 |
| 输出格式 | JSON，含question/options/answer/explanation |
| 解析要求 | 每题附带详细解析 |
| 画像适配 | 基于认知风格和学习水平调整题型比例 |
| 预估时长 | 20分钟 |

**资源4：拓展阅读 (EXTENDED_READING)**

| 项目 | 规格 |
|------|------|
| 资源类型 | 书籍、论文、文章、视频、在线课程 |
| 数量 | 3-5个高质量资源 |
| 信息维度 | 类型/标题/推荐理由/适合程度/获取链接 |
| 质量标准 | 权威性、实用性、时效性 |
| 预估时长 | 30分钟 |

**资源5：视频脚本 (VIDEO_SCRIPT)**

| 项目 | 规格 |
|------|------|
| 时长控制 | 3-5分钟 |
| 脚本结构 | 开场引入 → 核心讲解 → 案例演示 → 总结回顾 |
| 分镜格式 | 镜头编号 + 画面描述 + 旁白文本 |
| 表达风格 | 口语化，善用比喻和类比 |
| 预估时长 | 5分钟（阅读） |
| 备注 | 当前生成文字脚本，非渲染视频文件 |

**资源6：代码实操 (CODE_PRACTICE)**

| 项目 | 规格 |
|------|------|
| 代码语言 | 默认Python，可通过`programming_language`参数指定 |
| 内容结构 | 案例目标 → 预备知识 → 代码实现 → 代码解析 → 运行结果 → 进阶挑战 |
| 注释要求 | 完整注释，逐行解析 |
| 代码规范 | PEP8规范，易读性优先 |
| 预估时长 | 45分钟 |
| 专用接口 | `generate_code_practice(topic, profile, language)` |

#### 4.3.3 资源生成完整工作流

```
Coordinator.generate_learning_resources(topics, resource_types)
  ├── 校验: current_profile 是否存在
  ├── 并行生成: ThreadPoolExecutor(max_workers=4)
  │   └── for topic × resource_type:
  │       ResourceGeneratorAgent.generate_resource(type, topic, profile)
  │         ├── _build_prompt(): 注入学生画像信息
  │         ├── LLM.chat(messages, temperature=0.7)
  │         ├── ContentSafetyFilter.filter(content) 安全检查
  │         ├── HallucinationDetector.check_factuality(content, topic) 幻觉检测
  │         ├── ContentSafetyFilter.sanitize(content) 内容清理
  │         ├── 创建 LearningResource 对象
  │         │   ├── resource_id = UUID4
  │         │   ├── difficulty = _estimate_difficulty(profile)
  │         │   └── estimated_time = _estimate_time(resource_type)
  │         └── 追加到 generated_resources 列表
  ├── 收集所有成功/失败结果
  └── 返回 {resources: [to_card()], count, errors, types_generated}
```

#### 4.3.4 资源卡片 (to_card) 输出规范

每个资源调用 `to_card()` 后输出：
```json
{
  "id": "uuid",
  "type": "course_document|mind_map|exercises|extended_reading|video_script|code_practice",
  "title": "知识点 - 资源类型名称",
  "preview": "前200字预览",
  "full_content": "完整内容",
  "topics": ["目标知识点列表"],
  "difficulty": "easy|medium|hard",
  "duration": "预估学习分钟",
  "icon": "Font Awesome类名",
  "color": "卡片主题色"
}
```

---

### 4.4 模块四：个性化学习路径规划

#### 4.4.1 功能描述
学习规划智能体基于学生画像、已生成资源和学习目标，自动生成多阶段、带里程碑的个性化学习路径，并支持基于评估结果的动态调整。

#### 4.4.2 路径规划算法

```
LearningPlannerAgent.create_learning_path(profile, resources, goal)
  ├── _analyze_target_topics(profile)
  │   ├── 提取薄弱知识点 (priority=1, 优先学习)
  │   ├── 提取未掌握知识点 (mastery<0.8, priority=2)
  │   ├── 提取偏好知识点 (priority=3, 增强兴趣)
  │   └── 按优先级排序，取前10个知识点
  ├── _plan_steps(profile, resources, target_topics)
  │   ├── speed_factor = {fast:0.7, medium:1.0, slow:1.3}
  │   └── for each topic:
  │       ├── 学习步骤 (45×speed_factor min)
  │       │   ├── difficulty = mastery<0.3→easy, 0.3~0.6→medium, >0.6→hard
  │       │   └── activities = ["观看讲解","做笔记","理解概念"] + 类型特化
  │       ├── 练习步骤 (30×speed_factor min)
  │       │   ├── difficulty = 练习难度略高于学习
  │       │   └── activities = ["做题","错题分析","总结反思"]
  │       └── 每3个知识点插入阶段复习 (40×speed_factor min)
  ├── 末尾添加学习总结步骤 (30 min)
  ├── _generate_difficulty_curve(steps): 渐进式难度曲线
  └── _set_milestones(steps): 5级里程碑
      └── 入门成功→基础掌握→能力提升→深入理解→融会贯通
```

#### 4.4.3 路径动态调整算法

```
LearningPlannerAgent.adjust_path(path, progress)
  ├── 标记 completed_steps 为已完成
  └── for each 未完成步骤:
      ├── if topic.assessment_score < 0.6:
      │   ├── difficulty → 'easy'
      │   ├── duration × 1.2 (延长时间)
      │   └── activities += "额外练习"
      └── elif topic.assessment_score > 0.9:
          ├── duration × 0.8 (加快进度)
          └── activities += "进阶挑战"
```

#### 4.4.4 周计划生成

```python
get_weekly_plan(path, weekly_hours=10)
  # 将学习步骤分配到7天
  # 每天分配 weekly_hours/7 小时
  # 按 morning/afternoon/evening 时段
  # 输出: {weekly_plan: [{day, tasks, total_hours}], summary}
```

#### 4.4.5 可视化视图

| 视图类型 | 展示方式 | 所在页面 |
|---------|---------|---------|
| 甘特图 (Gantt) | 时间线+阶段里程碑可视化 | `/student/learning-plan` |
| 日历视图 | 每日任务卡片布局 | `/student/learning-plan` |
| 列表视图 | 步骤顺序列表 | `/student/learning-plan` |
| 周计划 | 7天日程表 | 学习计划页面周视图 |

---

### 4.5 模块五：智能辅导

#### 4.5.1 功能描述
辅导智能体提供多模态学习答疑服务，支持普通问答和RAG知识库增强问答两种模式，具备上下文保持、追问纠错和个性化建议能力。

#### 4.5.2 问答类型自动检测

| 类型 | 触发关键词 | 回答格式 |
|------|-----------|---------|
| `code` | 代码/编程/python | 问题分析→解决方案→代码解析→注意事项→练习 |
| `comparison` | 比较/区别/vs | 对比分析格式 |
| `explanation` | 为什么/原理/原因 | 问题理解→解答→知识延伸→思考题 |
| `guide` | 如何/怎样/怎么 | 步骤式指南 |
| `calculation` | 计算/求解/证明/推导 | 推导过程格式 |
| `general` | 其他 | 通用问答格式 |

#### 4.5.3 流式回答

```python
tutor_agent.stream_answer(question, profile, context)
  ├── ContentSafetyFilter.filter(question)
  ├── _build_prompt(): 注入画像+上下文
  ├── LLM.stream_chat(messages, temperature=0.7)
  │   └── yield content chunks (SSE/逐字)
  └── 异常回退: yield 预定义降级文本
```

#### 4.5.4 高级辅导功能

- **概念详解** `explain_with_examples()`：配2-3个由浅入深的例子，附加常见误区
- **针对性练习** `create_practice_for_doubt()`：基于错题生成3道分层巩固练习
- **多模态提示** `_get_multimodal_hints()`：检测是否需要生成流程图/代码/视频脚本

---

### 4.6 模块六：学习效果评估

#### 4.6.1 功能描述
评估智能体基于8维指标体系对学生学习效果进行多维度定量评估，生成结构化评估报告，并与画像和路径形成数据回流闭环。

#### 4.6.2 8维指标定义与计算

| 指标 | 字段名 | 权重 | 数据来源 |
|------|--------|:---:|---------|
| 知识掌握度 | `knowledge_mastery` | 25% | profile.knowledge_base 平均分 × 100 |
| 练习准确率 | `practice_accuracy` | 20% | quiz_results 正确率 |
| 概念理解度 | `concept_understanding` | 15% | 概念类题目正确率 |
| 问题解决能力 | `problem_solving` | 15% | 难题 (difficulty=hard) 正确率 |
| 学习效率 | `learning_efficiency` | 10% | 时间/成果比 + 知识掌握度平均 |
| 时间管理 | `time_management` | 5% | study_patterns.punctuality + planning |
| 学习持续性 | `consistency` | 5% | streak.current × 10 |
| 学习投入度 | `engagement` | 5% | 持续性/专注度/资源使用率的加权平均 |

#### 4.6.3 等级评定

| 等级 | 分数区间 | 英文标识 |
|------|:------:|---------|
| 优秀 | 90-100 | `excellent` |
| 良好 | 75-89 | `good` |
| 一般 | 60-74 | `fair` |
| 需改进 | <60 | `poor` |

#### 4.6.4 评估报告生成（Markdown格式）

```
# 学习效果评估报告
## 总体评估（日期/得分/等级）
## 各项指标得分（8维表格）
## 优势领域（前3最高分，≥75分）
## 需要加强（后3最低分，<70分）
## 学习趋势（improving_topics / declining_topics / stability）
## 改进建议（最多5条，含个性化画像建议）
```

#### 4.6.5 数据回流闭环

```
能力测试 → quiz_results
         → EvaluatorAgent.evaluate(profile, learning_data)
            └── 8维指标计算 → AssessmentReport
               ├── 存储到 AssessmentReportModel (持久化)
               ├── radar_chart 数据 → 前端 ECharts 渲染
               └── recommendations → 回流到 Coordinator
                                     → adjust_path() → 更新 LearningPath
                                     → profile更新 (知识基础/薄弱点)
```

---

### 4.7 多智能体协同架构

#### 4.7.1 Agent角色清单

| 编号 | Agent | 类名 | 角色定位 | 核心能力 |
|:----:|-------|------|---------|---------|
| A1 | 画像构建 | `ProfileBuilderAgent` | 学习画像采集与维护 | 10维画像、LLM对话、关键词匹配 |
| A2 | 资源生成 | `ResourceGeneratorAgent` | 多类型资源协同生成 | 6种SystemPrompt、并行生成、安全过滤 |
| A3 | 学习规划 | `LearningPlannerAgent` | 个性化路径规划 | 目标分析、步骤规划、动态调整 |
| A4 | 智能辅导 | `TutorAgent` | 多模态学习答疑 | 6种答案类型、流式输出、追问纠错 |
| A5 | 效果评估 | `LearningEvaluatorAgent` | 学习效果量化评估 | 8维指标、等级评定、趋势分析 |
| A6 | 知识库 | `KnowledgeBaseAgent` | RAG知识管理 | 8格式解析、双后端检索、LLM生成回答 |
| A7 | 协调器 | `AgentCoordinator` | 多智能体工作流调度 | 会话管理、并行调度、日志记录 |

#### 4.7.2 协调器完整API

| 方法 | 路径 | 描述 |
|------|------|------|
| `initialize_session(user_id, username)` | /agent/init | 初始化会话，创建画像，返回欢迎消息 |
| `build_profile(user_message)` | /agent/profile | 对话构建/更新画像 |
| `generate_learning_resources(topics, types)` | /agent/resources | 并行生成多种资源 |
| `create_personalized_plan(goals, time)` | /agent/plan | 创建个性化学习路径+周计划 |
| `ask_question(question)` | /agent/ask | 智能问答（含RAG上下文） |
| `stream_ask_question(question)` | /agent/stream | 流式智能问答 |
| `evaluate_and_adjust(steps, results)` | /agent/evaluate | 评估并调整学习路径 |
| `get_system_status()` | /agent/status | 获取系统运行状态 |
| `reset_session()` | /agent/reset | 重置所有Agent和会话 |
| `export_session_data()` | /agent/export | 导出完整会话数据 |

#### 4.7.3 协同工作流（典型场景）

```
学生学习完整闭环:
┌─────────────────────────────────────────────────────┐
│ 1. initialize_session → 创建画像                     │
│ 2. build_profile → 多轮对话完善画像 (10维)           │
│ 3. generate_learning_resources → 并行生成6种资源      │
│ 4. create_personalized_plan → 生成学习路径+周计划     │
│ 5. ask_question → 日常辅导问答                        │
│ 6. evaluate_and_adjust → 基于测评调整路径             │
│ 7. (循环至步骤3或5, 画像和路径持续优化)               │
└─────────────────────────────────────────────────────┘
```

---

### 4.8 工程化与部署功能

1. **Windows一键启动**：`start.bat` 双击启动，自动创建虚拟环境、安装依赖、启动服务
2. **Docker部署**：`Dockerfile` + `docker-compose.yml` + `wsgi.py`
3. **数据库**：SQLite (instance/quiz_system.db)，零配置启动
4. **前端**：Flask服务端模板渲染 + Bootstrap 5 + ECharts 可视化
5. **演示账号**：admin/teacher/student 三套账号自动补齐
6. **单例模式**：`get_coordinator()` 全局单例协调器

---

## 5. 非功能需求

### 5.1 性能要求

| 指标 | 目标值 | 说明 |
|------|:-----:|------|
| 页面加载时间 | < 3秒 | 基础页面响应 |
| 文档上传处理时间 | < 30秒 | 100KB以内文档解析+索引 |
| RAG问答响应时间 | < 15秒 | 含LLM生成时间 |
| 资源生成并行数 | 4 | ThreadPoolExecutor(max_workers=4) |
| LLM调用超时 | 60秒(同步)/120秒(流式) | 自动重试3次 |

### 5.2 安全与可信要求

1. **知识库回答**必须基于已上传资料，材料不足时明确提示而非猜测回答
2. **内容安全**：`ContentSafetyFilter` 在画像、辅导、资源生成的输入输出两端均做过滤
3. **幻觉检测**：`HallucinationDetector` 对生成内容进行不确定性表达和虚假引用检测
4. **教师材料优先**：当多来源存在差异时，优先以教师上传讲义/课程资料为准

### 5.3 可维护性要求

1. 模块按Agent角色拆分，每个Agent独立负责一类功能
2. 检索引擎支持从TF-IDF平滑替换到ChromaDB（环境变量切换）
3. LLM接口支持OpenAI兼容接口/Ollama本地模型灵活切换
4. 配置通过环境变量管理（`.env` 文件）

---

## 6. 典型业务流程（详细版）

### 6.1 学生首次使用完整闭环

```
Step 1: 登录 (student/student123)
Step 2: 首页 → 点击"学习画像"
Step 3: 对话输入:
   "我是大二计科学生，数据结构学得不好，准备考研408"
Step 4: 系统实时更新10维画像（右侧面板逐项显示）
Step 5: 进入能力测试中心 → 选择"普通高校专业方向"
Step 6: 完成答题 → 查看总分+难度分布+逐题解析
Step 7: 进入学习报告 → 查看8维雷达图+学习建议
Step 8: 基于评估结果自动调整学习计划
Step 9: 查看学习路径甘特图/日历/列表视图
Step 10: 进入智能问答 → 上传课程资料
Step 11: 知识库问答:"什么是冯诺依曼架构？"→ 获取引用回答
Step 12: 触发资源生成 → 生成课程讲义/思维导图/练习题
```

### 6.2 教师材料投喂闭环

```
Step 1: 教师登录 (teacher/teacher123)
Step 2: 准备课程资料（讲义/实验文档/题库/术语表）
Step 3: 上传到知识库 → 系统解析+分块+索引
Step 4: 学生在问答中自动引用教师材料
Step 5: 学生测评结果反馈给教师分析工作台
```

---

## 7. 数据字典

### 7.1 StudentProfile (学生画像)

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|:---:|--------|------|
| user_id | int | ✅ | - | 用户ID |
| username | str | ✅ | - | 用户名 |
| knowledge_base | Dict[str, float] | - | {} | 知识点→掌握度 |
| cognitive_style | str | - | "visual" | visual/verbal/auditory/kinesthetic |
| error_patterns | List[Dict] | - | [] | 易错点列表 |
| learning_speed | str | - | "medium" | slow/medium/fast |
| interests | List[str] | - | [] | 兴趣方向 |
| goals | List[str] | - | [] | 学习目标 |
| preferred_topics | List[str] | - | [] | 偏好知识点 |
| weak_topics | List[str] | - | [] | 薄弱知识点 |
| strong_topics | List[str] | - | [] | 强项知识点 |
| study_habits | Dict[str, Any] | - | {} | 学习习惯 |
| available_time | Dict[str, int] | - | {} | 可用时间 |
| confidence | float | - | 0.0 | 画像置信度 (0~1) |

### 7.2 LearningResource (学习资源)

| 字段 | 类型 | 说明 |
|------|------|------|
| resource_id | str (UUID4) | 资源唯一标识 |
| resource_type | ResourceType | 资源类型枚举 |
| title | str | 资源标题 |
| content | str | 资源正文内容 |
| target_topics | List[str] | 目标知识点 |
| difficulty | str | easy/medium/hard |
| estimated_time | int | 预估学习分钟 |
| source_agent | str | 生成来源Agent |

### 7.3 LearningPath (学习路径)

| 字段 | 类型 | 说明 |
|------|------|------|
| path_id | str (UUID4) | 路径唯一标识 |
| steps | List[Dict] | 学习步骤列表 |
| total_duration | int | 总预估分钟 |
| difficulty_curve | List[str] | 难度曲线序列 |
| milestones | List[Dict] | 里程碑列表 |

---

## 8. 验收标准

| 编号 | 验收项 | 验收标准 |
|:----:|-------|---------|
| AC-1 | 系统启动 | `start.bat` / `python run.py` 可成功启动，`http://127.0.0.1:5000` 可访问 |
| AC-2 | 演示账号 | admin/teacher/student 三套账号均可正常登录 |
| AC-3 | 能力测试 | 至少两个专业方向可切换，完整答题流程可用 |
| AC-4 | 学习画像 | 对话后右侧面板显示10维画像动态更新 |
| AC-5 | 知识库上传 | 至少6种格式文件可成功上传并建立索引 |
| AC-6 | RAG问答 | 知识库问答返回带来源引用的回答 |
| AC-7 | 资料不足拦截 | 无关问题返回"资料不足"提示 |
| AC-8 | 学习路径 | 生成甘特图/日历/列表视图的个性化学习路径 |
| AC-9 | 资源生成 | 6种资源类型均可成功生成并展示 |
| AC-10 | 学习报告 | 8维雷达图可正常渲染，含趋势和改进建议 |
| AC-11 | 路径调整 | 评估结果可回流到学习路径并产生差异 |
| AC-12 | Docker部署 | Dockerfile + docker-compose 完整可用 |
| AC-13 | 配套文档 | 7类文档齐全，证据包完整 |
| AC-14 | 课程样例包 | 计算机组成原理6个文件可完成全链路验证 |

---

## 9. 附录：LLM集成规范

### 9.1 LLM客户端架构

```
BaseLLM (抽象基类)
├── OpenAIClient: OpenAI兼容API
│   ├── chat(): POST /v1/chat/completions
│   └── stream_chat(): SSE流式
└── LocalLLM: Ollama本地模型
    ├── chat(): POST /api/chat
    └── stream_chat(): 流式JSON行
```

### 9.2 各Agent的LLM调用参数

| Agent | Temperature | Max Tokens | System Prompt 特征 |
|-------|:----------:|:----------:|-------------------|
| ProfileBuilder | 0.8 | 4096 | 苏格拉底式教育顾问 |
| ResourceGenerator | 0.7 | 4096 | 按资源类型切换6种专家角色 |
| Tutor | 0.7 | 4096 | 耐心专业学习导师 |
| KnowledgeBase (RAG) | 0.2 | 900 | 课程知识库问答助手 |
| Evaluator | - | - | 规则计算为主 |

### 9.3 LLM降级策略

所有Agent在LLM调用失败时均有降级响应：
- `ProfileBuilder`: 预定义问候模板 + 结构化追问
- `ResourceGenerator`: 6种资源的预定义模板内容 `_get_fallback_content()`
- `Tutor`: 通用学习指导模板 `_get_fallback_answer()`
- `KnowledgeBase`: 检索片段直接拼接 + 建议语
- Mock回答检测: `_looks_like_mock_answer()` 过滤模板化通用回复

---

*本SRS文档基于大模智学v2.0实际代码编写，所有功能描述均可从 `app/multi_agent/` 源码中对应验证。*
