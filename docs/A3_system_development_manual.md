# A3 系统开发说明书

**项目名称**：大模智学  
**赛题名称**：A3-基于大模型的个性化资源生成与学习多智能体系统开发  
**版本**：v2.0  
**最后更新**：2026-06-15

---

## 1. 项目概述

### 1.1 系统定位

"大模智学"是一个面向高校大学生的个性化学习多智能体系统，围绕软件杯A3赛题五大核心能力设计：
1. 对话式学习画像构建
2. 多智能体协同资源生成
3. 个性化学习路径规划与资源推送
4. 智能辅导与即时答疑
5. 学习效果评估与动态优化

系统以Web应用为载体，覆盖课程教学辅助、自主学习辅导、知识库RAG问答、多模态资源生成与学习效果追踪等高校核心场景。

### 1.2 核心理念

本系统不是"一个模型回答所有问题"的UI壳，而是将**学习画像**作为中心数据资产，让7类Agent分工协作，贯穿"对话了解学生→定制资源→规划路径→辅导答疑→评估反馈→动态调整"的完整学习闭环。

---

## 2. 需求分析

### 2.1 用户痛点

1. 高校课程内容多、节奏快，学生难以在海量资源中找到适合自己的学习材料
2. 统一化教学无法兼顾基础差异与学习偏好差异（视觉型/听觉型/动手型）
3. 传统学习计划静态、无反馈，不会随学习效果变化动态调整
4. 通用AI聊天工具缺乏课程资料支撑，回答不可追溯，存在知识幻觉风险
5. 测评结果常停留在总分层面，难以形成针对性改进方案

### 2.2 赛题对标

| 赛题要求 | 本系统实现 |
|---------|-----------|
| 对话式学习画像自主构建 | `ProfileBuilderAgent`：10维画像，LLM驱动对话，关键词+规则匹配 |
| 多智能体协同资源生成 | `ResourceGeneratorAgent`：6种SystemPrompt，并行生成，画像注入 |
| 个性化学习路径规划 | `LearningPlannerAgent`：优先级排序，渐进难度曲线，5级里程碑 |
| 智能辅导 | `TutorAgent`：6种答案类型，流式SSE，上下文保持 |
| 学习效果评估 | `LearningEvaluatorAgent`：8维加权指标，ECharts雷达图，趋势分析 |
| 知识库与防幻觉 | `KnowledgeBaseAgent`：8格式解析，TF-IDF/ChromaDB双后端，LLM生成+引用 |
| 课程知识库样例 | 计算机组成原理6文件完整样例包 |

---

## 3. 总体架构

### 3.1 技术架构（四层模型）

```
┌─────────────────────────────────────────────────────┐
│                    表现层 (Templates)                 │
│  Bootstrap 5 + ECharts + Mermaid.js + Font Awesome  │
│  49个HTML模板覆盖所有页面                             │
├─────────────────────────────────────────────────────┤
│                    路由层 (Routes)                    │
│  Flask Blueprint × 10: main/auth/quiz/analysis/     │
│  student/intelligent_assistant/test/nav/features/    │
│  extra_features/agent_system                        │
├─────────────────────────────────────────────────────┤
│                  智能体层 (Multi-Agent)               │
│  AgentCoordinator ← 单例协调器                        │
│  ├── ProfileBuilderAgent                            │
│  ├── ResourceGeneratorAgent                         │
│  ├── LearningPlannerAgent                           │
│  ├── TutorAgent                                     │
│  ├── LearningEvaluatorAgent                         │
│  ├── KnowledgeBaseAgent                             │
│  └── LLM Client (BaseLLM → OpenAI/Ollama)           │
├─────────────────────────────────────────────────────┤
│                    数据层 (Models)                    │
│  SQLAlchemy ORM + SQLite                            │
│  ├── StudentProfileModel                            │
│  ├── LearningResourceModel                          │
│  ├── LearningPathModel                              │
│  ├── AssessmentReportModel                          │
│  ├── KnowledgeDocumentModel                         │
│  ├── KnowledgeChunkModel                            │
│  ├── DigitalHumanVideoTaskModel                     │
│  └── ChatHistoryModel                               │
└─────────────────────────────────────────────────────┘
```

### 3.2 路由与蓝图体系

| 蓝图 | URL前缀 | 核心职责 |
|------|--------|---------|
| `main_bp` | `/` | 首页、赛题对照、成就中心、通知中心、笔记系统 |
| `auth_bp` | `/auth` | 登录、注册、注销 |
| `quiz_bp` | `/quiz` | 题库管理、答题、提交、错题本 |
| `analysis_bp` | `/analysis` | 数据分析、学习报告、画像展示、排名 |
| `student_bp` | `/student` | 学习计划、专项练习、学习详情 |
| `intelligent_bp` | `/intelligent-assistant` | 智能问答主页面 |
| `agent_bp` | `/agent` | 多智能体系统API端点 |
| `test_bp` | `/test` | 能力测试中心 |
| `features_bp` | `/features` | 功能展示页 |
| `extra_bp` | `/extra` | 扩展功能（PPT生成等） |

### 3.3 核心页面清单

| 页面 | 模板路径 | URL路径 | 核心功能 |
|------|---------|---------|---------|
| 首页 | `index.html` | `/` | 系统入口与能力概览 |
| 登录 | `auth/login.html` | `/auth/login` | 用户认证 |
| 智能问答 | `intelligent_assistant/index.html` | `/intelligent-assistant` | 多智能体协同中枢 |
| 学习画像 | `agent_system/learning_agent.html` | `/agent-system/learning-agent` | 对话式画像构建 |
| 能力测试 | `test/assessment_pro.html` | `/test/assessment` | 专业化测评 |
| 学习报告 | `analysis/learning_report.html` | `/analysis/report` | 8维雷达图+趋势 |
| 学习计划 | `student/learning_plan.html` | `/student/learning-plan` | 甘特图+日历+列表 |
| 学生画像 | `analysis/student_portrait.html` | `/analysis/portrait` | 画像详情展示 |
| 赛题对照 | `competition_readiness.html` | `/competition-readiness` | 赛题完成度总览 |

---

## 4. 智能体详细设计（深度阐述）

### 4.1 协调器 AgentCoordinator

**文件**：`app/multi_agent/coordinator.py`

#### 4.1.1 设计模式与架构

协调器采用**单例模式**管理全局智能体实例：

```python
_coordinator_instance: Optional[AgentCoordinator] = None

def get_coordinator() -> AgentCoordinator:
    global _coordinator_instance
    if _coordinator_instance is None:
        _coordinator_instance = AgentCoordinator()
    return _coordinator_instance
```

#### 4.1.2 核心职责

1. **会话管理**：每个用户会话通过 `session_id` (UUID4) 唯一标识，维护画像/资源/路径/日志的状态生命周期
2. **工作流编排**：按"画像→资源→路径→问答→评估"的顺序编排Agent调用
3. **并行调度**：资源生成使用 `ThreadPoolExecutor(max_workers=4)` 并行调用
4. **执行追溯**：每次Agent调用记录时间戳、Agent名称、操作、参数到 `execution_log`

#### 4.1.3 数据流

```
用户请求 → coordinator.orchestrate()
           ├── 检查前置条件 (如: 画像是否存在)
           ├── 调用目标Agent
           ├── 记录 execution_log {timestamp, agent, action, params}
           ├── 更新协调器状态 (current_profile/resources/path)
           └── 返回统一响应格式 {结果, 状态, 错误}
```

#### 4.1.4 会话生命周期

```
initialize_session(user_id, username)
  → reset all agents
  → profile_agent.init_profile()
  → 返回 {session_id, profile, welcome_message, suggested_questions}

... 用户操作 ...

reset_session()
  → 重建所有Agent实例
  → 清空所有状态
  → 返回 {message, new_session_id}
```

---

### 4.2 画像构建智能体 ProfileBuilderAgent

**文件**：`app/multi_agent/profile_agent.py`

#### 4.2.1 设计目标

通过自然语言多轮对话自动构建学生的10维学习画像，无需表单填写。

#### 4.2.2 完整工作流

```
用户消息 → ContentSafetyFilter.filter()
          ├── 不安全 → 返回拒绝响应
          └── 安全 ↓
          → conversation_history.append({role:user, content})
          → _build_context(): 组装"当前学生+已知信息"上下文
          → 构建 messages = [SYSTEM_PROMPT] + [问候语] + [历史对话] + [上下文] + [用户消息]
          → LLM.chat(messages, temperature=0.8)
            ├── 成功 → 获取响应文本
            └── 失败 → _get_fallback_response()
          → _extract_profile_update(response):
            ├── re.search(r'\{[^{}]*\}', response) 提取JSON
            ├── 反射更新 self.profile 对应字段
            ├── 更新 extracted_info
            └── confidence = len(extracted_info) / 10
          → _extract_keywords(response):
            ├── 认知风格匹配:
            │   {visual: [看,图,画,视觉], verbal: [读,写,说],
            │    auditory: [听,声音,音频], kinesthetic: [做,动手,实践]}
            └── 学习速度匹配:
                {fast: [快,迅速], slow: [慢,需要时间,反复]}
          → _generate_suggested_questions(): 基于缺失维度生成追问
          → conversation_history.append({role:assistant, content:response})
          → 返回 {response, profile_update, suggested_questions, profile}
```

#### 4.2.3 System Prompt设计（核心）

```
角色: 专业教育顾问智能体
原则: 苏格拉底式提问 → 画像动态更新 → 自然流畅对话
维度: 10个 (知识基础/认知风格/易错点/学习速度/兴趣/目标/偏好/薄弱/习惯/时间)
输出: 1.理解和建议 2.更新画像(JSON) 3.建议下一轮问题
```

#### 4.2.4 核心算法

**关键词匹配推断**：使用中文关键词集合进行认知风格和学习速度的枚举匹配

**置信度计算**：
```python
self.profile.confidence = min(1.0, len(self.extracted_info) / 10)
```
每成功提取一个维度，置信度增加0.1，上限1.0

**建议问题生成**：遍历所有维度，对缺失维度生成对应追问，最多3个

#### 4.2.5 输入输出规范

**输入**：`user_message: str` — 任意长度的自然语言文本

**输出**：
```json
{
  "response": "AI回复文本",
  "profile_update": {"认知风格": "visual", "学习速度": "medium", ...},
  "suggested_questions": ["追问1", "追问2", "追问3"],
  "profile": { /* 完整10维画像 */ }
}
```

---

### 4.3 资源生成智能体 ResourceGeneratorAgent

**文件**：`app/multi_agent/resource_agent.py`

#### 4.3.1 设计目标

根据学生画像和指定知识点，利用LLM生成6种类型的个性化学习资源。本Agent是系统"资源多样性"的核心体现。

#### 4.3.2 6种资源的System Prompt设计

每种资源类型拥有独立的System Prompt，定义了角色的专业知识、输出格式和质量标准：

| 资源类型 | 角色定位 | 输出格式 | 特殊要求 |
|---------|---------|---------|---------|
| COURSE_DOCUMENT | 资深教育专家 | Markdown 6段式 | 800-1500字，代码块支持 |
| MIND_MAP | 知识可视化专家 | Mermaid mindmap | 3-4层，每节点1-5词 |
| EXERCISES | 出题专家 | JSON exercises数组 | 5种题型×3级难度 |
| EXTENDED_READING | 学术导师 | Markdown列表 | 3-5个资源，含获取链接 |
| VIDEO_SCRIPT | 视频内容策划 | Markdown分镜 | 4镜头结构，3-5分钟 |
| CODE_PRACTICE | 程序员教育者 | Markdown+代码块 | 完整注释+逐行解析 |

#### 4.3.3 完整生成管线

```
generate_resource(resource_type, topic, profile, additional_context=None)
  ├── _build_prompt(): 构建个性化提示
  │   ├── 注入学生画像信息:
  │   │   ├── 用户名 / 认知风格 / 学习速度
  │   │   ├── 兴趣方向 / 学习目标
  │   │   └── 薄弱知识点 (top3) / 附加信息
  │   └── 注入资源信息:
  │       ├── 资源类型 / 主题
  │       └── additional_context (如编程语言)
  ├── messages = [SYSTEM_PROMPT[type]] + [user_prompt]
  ├── LLM.chat(messages, temperature=0.7)
  │   ├── 成功 → content
  │   └── 失败 → _get_fallback_content(type, topic)
  ├── 内容安全: ContentSafetyFilter.filter(content)
  │   └── 不安全 → content = "[内容已过滤]"
  ├── 幻觉检测: HallucinationDetector.check_factuality(content, topic)
  │   └── 有警告 → content += "> ⚠️ 注意：{warnings[0]}"
  ├── 内容清理: ContentSafetyFilter.sanitize(content)
  └── 创建 LearningResource 对象
      ├── resource_id = uuid4()
      ├── title = "{topic} - {resource_type.value}"
      ├── difficulty = _estimate_difficulty(profile):
      │   └── fast→hard, slow→easy, else→medium
      └── estimated_time = _estimate_time(resource_type):
          {COURSE:15, MIND_MAP:10, EXERCISES:20,
           READING:30, VIDEO:5, CODE:45} 分钟
```

#### 4.3.4 并行生成机制

```python
# Coordinator 中的并行调度
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {}
    for topic in topics:
        for res_type in resource_types:
            future = executor.submit(
                self.resource_agent.generate_resource,
                res_type, topic, profile
            )
            futures[future] = {'topic': topic, 'type': res_type}
    
    for future in as_completed(futures):
        # 每个任务独立收集，失败不影响其他任务
```

#### 4.3.5 降级策略 `_get_fallback_content()`

每个资源类型都有预定义的Markdown/JSON/Mermaid模板作为LLM不可用时的降级内容，确保系统在任何情况下都有基础输出。

#### 4.3.6 输入输出规范

**输入**：`resource_type: ResourceType`, `topic: str`, `profile: StudentProfile`, `additional_context: Dict`

**输出**：`LearningResource` 对象，通过 `to_card()` 转为前端卡片格式：
```json
{
  "id": "uuid",
  "type": "course_document|mind_map|exercises|...",
  "title": "主题 - 资源类型",
  "preview": "前200字预览",
  "full_content": "完整Markdown/Mermaid/JSON内容",
  "topics": ["目标知识点"],
  "difficulty": "easy|medium|hard",
  "duration": 15,
  "icon": "fa-file-alt|fa-project-diagram|...",
  "color": "#4364F7|#00C9A7|..."
}
```

---

### 4.4 知识库智能体 KnowledgeBaseAgent

**文件**：`app/multi_agent/knowledge_agent.py` (563行)

#### 4.4.1 设计目标

构建完整的RAG知识库管线：文档上传→解析→分块→索引→语义检索→LLM生成回答，是系统"可信回答"的核心工程实现。

#### 4.4.2 文档解析架构

```
extract_text(file_path, filename)
  ├── 扩展名检测 (SUPPORTED_EXTENSIONS = {.txt, .md, .csv, .json, .docx, .pdf, .pptx, .ppt})
  └── 按类型路由:
      ├── .docx → _extract_docx_text()
      │   └── ZIP打开 → word/document.xml → XML遍历 w:p → 提取w:t文本
      ├── .pdf  → _extract_pdf_text()
      │   └── PyPDF2/PyPDF PdfReader → 逐页 extract_text()
      ├── .pptx → _extract_pptx_text()
      │   └── ZIP → ppt/slides/slide*.xml → 遍历a:t节点 → 逐slide提取
      ├── .ppt  → _extract_ppt_text()
      │   └── 二进制正则提取 UTF-16LE ([\x20-\x7e\x80-\xff]\x00){4,}
      │   └── ASCII补充提取 [\x20-\x7e]{6,}
      │   └── _normalize_binary_text() 清理控制字符
      └── 文本类 → 编码检测读取 (utf-8→gbk→gb18030→ignore)
```

#### 4.4.3 文本分块算法 `_chunk_text()`

```python
def _chunk_text(text, chunk_size=800, overlap=120):
    # 第一步：清理多余换行
    cleaned = re.sub(r'\n{3,}', '\n\n', text).strip()
    
    # 第二步：滑动窗口分块
    chunks = []
    start = 0
    while start < len(cleaned):
        end = min(len(cleaned), start + chunk_size)
        window = cleaned[start:end]
        
        # 第三步：智能切割点查找（优先级: \n > 。> ；> .）
        cut = max(window.rfind('\n'), window.rfind('。'),
                  window.rfind('；'), window.rfind('.'))
        
        # 第四步：仅当切割点足够靠后时才使用
        if cut > chunk_size * 0.45:
            end = start + cut + 1
        
        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # 第五步：带重叠的滑动窗口
        start = max(0, end - overlap)
    
    return chunks
```

#### 4.4.4 双后端检索引擎

**后端一：TF-IDF（默认，零依赖）**

```python
def _rank_chunks(query, chunks):
    corpus = [chunk.content for chunk in chunks]
    try:
        # 字符级char_wb n-gram，中英文混合友好
        vectorizer = TfidfVectorizer(
            analyzer='char_wb',      # 字符边界感知
            ngram_range=(2, 4),      # 2-4 gram
            max_features=6000         # 特征上限
        )
        matrix = vectorizer.fit_transform(corpus + [query])
        similarities = cosine_similarity(matrix[-1], matrix[:-1]).flatten()
    except Exception:
        # 回退：Jaccard词重叠
        query_terms = set(tokenize(query))
        scored = [(chunk, |query_terms ∩ tokenize(chunk.content)| / |query_terms|)]
```

**后端二：ChromaDB 向量检索（可选启用）**

```python
# 环境变量: KNOWLEDGE_RETRIEVAL_BACKEND=chroma
def _search_with_chroma(user_id, query, top_k):
    collection = _get_chroma_collection(user_id)  # knowledge_user_{user_id}
    raw = collection.query(query_texts=[query], n_results=top_k)
    # 将 ChromaDB distance 转为 similarity
    similarity = 1 / (1 + distance)
```

**自动切换逻辑**：
```python
_init_retrieval_backend():
    if preference == 'chroma':
        try: import chromadb; 初始化PersistentClient
        except: 回退到 tfidf
    else:
        默认 tfidf
```

#### 4.4.5 RAG回答生成 `_generate_rag_answer()`

```python
def _generate_rag_answer(question, contexts):
    # 第一步：构建检索上下文
    prompt_blocks = []
    for i, ctx in enumerate(contexts, 1):
        prompt_blocks.append(
            f"[来源{i}] 文档：{ctx['document_title']}（{ctx['filename']}）\n"
            f"片段：{ctx['content'][:900]}"
        )
    
    # 第二步：构建LLM消息
    messages = [
        {"role": "system", "content": (
            "你是高校课程知识库问答助手。"
            "仅根据提供的材料回答问题，禁止编造。"
            "材料不足时明确说资料不足。"
            "引用时使用 [来源1] 格式。"
        )},
        {"role": "user", "content": (
            f"问题：{question}\n\n"
            f"可用材料：\n{'\n'.join(prompt_blocks)}\n\n"
            "要求：1.先给直接答案 2.关键结论带来源标记 "
            "3.多材料互相补充可合并 4.补学习建议"
        )}
    ]
    
    # 第三步：LLM生成 (低temperature确保忠实于材料)
    answer = LLM.chat(messages, temperature=0.2, max_tokens=900)
    
    # 第四步：Mock回答检测
    if _looks_like_mock_answer(answer):
        answer = ''  # 触发降级
    
    # 第五步：构建最终回答
    if answer:
        if '参考来源：' not in answer:
            answer += '\n' + '参考来源：\n' + 引用列表
        return answer
    
    # 第六步：降级方案 - 检索片段直接拼接
    return '\n'.join([
        f"基于已上传知识库，检索到 {len(contexts)} 条相关材料：",
        *[f"{i}. {best_sentence(ctx['content'], question)} [来源{i}]"
          for i, ctx in enumerate(contexts, 1)],
        "建议学习路径：先阅读最高相关来源，提炼概念定义，再用练习题验证..."
    ])
```

#### 4.4.6 关键词提取算法

```python
def _extract_keywords(text, limit=12):
    tokens = _tokenize(text)  # 中文: [\u4e00-\u9fa5]{2,} 英文: [A-Za-z][A-Za-z0-9_+-]{1,}
    freq = {}
    for token in tokens:
        if len(token) >= 2:
            freq[token] = freq.get(token, 0) + 1
    return sorted(freq.items(), key=lambda x: x[1], reverse=True)[:limit]
```

#### 4.4.7 输入输出规范

**文件上传** `index_file(user_id, file_path, original_filename, title)`

输出：
```json
{
  "document": { /* KnowledgeDocumentModel.to_dict() */ },
  "chunks": 7,
  "deduplicated": false  // SHA256去重标志
}
```

**检索** `search(user_id, query, top_k=5)`

输出：
```json
{
  "results": [{
    "chunk_id": 1,
    "document_id": "uuid",
    "document_title": "文档标题",
    "filename": "original.pdf",
    "chunk_index": 0,
    "score": 0.8523,
    "content": "分块文本内容",
    "preview": "高亮预览片段"
  }],
  "count": 3
}
```

**问答** `answer(user_id, question, top_k=4)`

输出：
```json
{
  "answer": "LLM生成的带引用回答或材料拼接",
  "citations": [{
    "ref": "来源1",
    "document_title": "...",
    "filename": "...",
    "chunk_index": 0,
    "score": 0.85,
    "content": "来源片段前360字"
  }],
  "confidence": 0.92,
  "warnings": [],
  "retrieval": { /* search结果 */ }
}
```

**状态** `status(user_id)`

输出：
```json
{
  "documents": [/* 文档列表 */],
  "document_count": 6,
  "chunk_count": 7,
  "retrieval_engine": "TF-IDF semantic retrieval",
  "retrieval_backend": "tfidf",
  "chroma_available": false,
  "supported_extensions": [".csv", ".docx", ".json", ".md", ".pdf", ".ppt", ".pptx", ".txt"]
}
```

---

### 4.5 学习规划智能体 LearningPlannerAgent

**文件**：`app/multi_agent/planner_agent.py`

#### 4.5.1 设计目标

基于学生画像、知识掌握度和学习目标，生成个性化、动态可调的多阶段学习路径。

#### 4.5.2 目标知识点分析算法

```
_analyze_target_topics(profile):
  收集三类知识点:
  ├── 薄弱知识点 (profile.weak_topics)     → priority=1, type=weak
  ├── 未掌握知识点 (mastery < 0.8)         → priority=2, type=need_work
  └── 偏好知识点 (profile.preferred_topics) → priority=3, type=interest
  
  排序规则: (priority ASC, mastery ASC) → 最多10个
  语义: 薄弱优先学 → 没掌握的接着学 → 感兴趣的激励学
```

#### 4.5.3 学习步骤规划算法

```python
_plan_steps(profile, resources, target_topics):
    speed_factor = {fast:0.7, medium:1.0, slow:1.3}[profile.learning_speed]
    
    for each topic:
        # 学习步骤
        学习步骤: {
            title: '学习：{topic}',
            duration: 45 × speed_factor,     # 快学生可缩短到31.5分钟
            difficulty: mastery<0.3→easy, 0.3~0.6→medium, >0.6→hard,
            activities: base + type_specific  # weak→增加示例, interest→拓展探索
        }
        
        # 练习步骤
        练习步骤: {
            title: '练习：{topic}',
            duration: 30 × speed_factor,
            difficulty: 比学习难度高一级,
            activities: [做题, 错题分析, 总结反思]
        }
        
        # 每3个知识点插入一次阶段复习
        if (i+1) % 3 == 0:
            复习步骤: {duration: 40 × speed_factor}
    
    # 末尾添加学习总结
    总结步骤: {title: '学习总结', duration: 30}
```

#### 4.5.4 难度曲线生成 `_generate_difficulty_curve()`

```
按学习进度位置 (position = i / (n-1)) 控制难度:
├── position < 0.2: easy (入门期)
├── position 0.2~0.4: easy/medium交替 (过渡期)
├── position 0.4~0.7: medium (核心学习期)
├── position 0.7~0.9: medium/hard交替 (深化期)
└── position > 0.9: hard (冲刺期)
```

#### 4.5.5 里程碑设定

5级递进式里程碑：
```
入门成功 → 基础掌握 → 能力提升 → 深入理解 → 融会贯通
```
每级对应一个成就奖励（如"解锁成就：初窥门径"），激励持续学习。

#### 4.5.6 动态路径调整

```python
adjust_path(path, progress):
    # 标记已完成
    for step in path.steps:
        if step.step_number in completed_steps:
            step.completed = True
    
    # 基于评估结果调整未完成步骤
    for step in path.steps where not completed:
        for topic in step.topics where topic in assessments:
            if score < 0.6:
                difficulty → 'easy'        # 降低难度
                duration × 1.2             # 延长时间
                activities += "额外练习"    # 增加练习
            elif score > 0.9:
                duration × 0.8             # 加快进度
                activities += "进阶挑战"    # 增加挑战
```

#### 4.5.7 前端可视化实现

三个视图均由同一个后端数据结构驱动：

- **甘特图视图**：使用CSS构建时间线，每个步骤为横条，里程碑为标记点
- **日历视图**：按7天网格布局，每天显示分配到的学习任务卡片
- **列表视图**：步骤编号顺序列表，每项显示标题、时长、难度标签

---

### 4.6 智能辅导智能体 TutorAgent

**文件**：`app/multi_agent/tutor_agent.py`

#### 4.6.1 设计目标

提供多模态、上下文化的学习答疑服务，支持6种回答类型自动检测、流式输出、追问纠错和个性化建议。

#### 4.6.2 回答类型自动检测

```python
_detect_answer_type(question):
    if '代码' in q or '编程' in q or 'python' in q.lower(): → 'code'
    elif '比较' in q or '区别' in q or 'vs' in q.lower():   → 'comparison'
    elif '为什么' in q or '原理' in q or '原因' in q:        → 'explanation'
    elif '如何' in q or '怎样' in q or '怎么' in q:          → 'guide'
    elif '计算' in q or '求解' in q or '证明' in q:          → 'calculation'
    else:                                                    → 'general'
```

每种类型对应不同的System Prompt回答格式模板。

#### 4.6.3 流式回答实现

```python
stream_answer(question, profile, context):
    # 安全检查
    is_safe, reason = ContentSafetyFilter.filter(question)
    if not is_safe: yield 拒绝消息; return
    
    # 构建消息
    prompt = _build_prompt(question, profile, context)
    messages = [SYSTEM_PROMPT, *conversation_context, user_prompt]
    
    # 流式调用
    try:
        for chunk in LLM.stream_chat(messages, temperature=0.7):
            yield chunk  # 逐字返回给前端(SSE)
    except:
        yield from _get_fallback_stream_answer(question)
```

#### 4.6.4 多模态提示 `_get_multimodal_hints()`

```python
# 检测回答内容是否需要额外媒体支持
{
    'has_diagram': '流程/结构/关系/对比/组成' in answer,    → 建议生成流程图
    'has_code': '```' in answer or 'def' in answer,         → 有代码块
    'has_video_script': len(answer) > 500,                  → 建议生成视频
    'video_outline': {时长: '3-5分钟', 结构: ['开场','讲解','演示','总结']}
}
```

#### 4.6.5 高级辅导功能

- **`explain_with_examples(concept, profile)`**：概念深度讲解，配2-3个递增例子+常见误区
- **`create_practice_for_doubt(question, wrong_answer, profile)`**：基于错题的3道分层练习题（基础巩固→变式应用→综合提升）

---

### 4.7 学习评估智能体 LearningEvaluatorAgent

**文件**：`app/multi_agent/evaluator_agent.py`

#### 4.7.1 设计目标

对学生学习效果进行8维多维度定量评估，生成结构化学习报告，支持前后对比和趋势分析。

#### 4.7.2 8维加权计算

```python
overall_score = (
    knowledge_mastery    × 0.25 +   # 知识掌握度
    practice_accuracy    × 0.20 +   # 练习准确率
    concept_understanding × 0.15 +  # 概念理解度
    problem_solving      × 0.15 +   # 问题解决能力
    learning_efficiency  × 0.10 +   # 学习效率
    time_management      × 0.05 +   # 时间管理
    consistency          × 0.05 +   # 学习持续性
    engagement           × 0.05     # 学习投入度
)
```

#### 4.7.3 各指标计算逻辑

| 指标 | 计算逻辑 |
|------|---------|
| knowledge_mastery | profile.knowledge_base所有值的平均×100，无数据默认50 |
| practice_accuracy | quiz_results中is_correct比例×100，无数据用knowledge_mastery |
| concept_understanding | 概念类题目is_correct比例×100，无数据用practice_accuracy×0.9 |
| problem_solving | difficulty=hard题目is_correct比例×100，无数据用practice_accuracy×0.8 |
| learning_efficiency | (expected_time / actual_time × 100 + knowledge_mastery) / 2 |
| time_management | (punctuality + planning) × 50 |
| consistency | min(100, current_streak × 10) |
| engagement | (consistency + focus_ratio×100 + resource_usage_rate×100) / 3 |

#### 4.7.4 前后对比 `compare_with_previous()`

```python
# 对比当前报告与上一次报告的差异
{
    'overall_change': +5.2,           # 总分变化
    'metric_changes': {
        'knowledge_mastery': +3.1,
        'practice_accuracy': +7.3,
        ...
    }
}
```

---

## 5. LLM集成与安全管理

### 5.1 LLM客户端架构

**文件**：`app/multi_agent/llm_client.py`

```
BaseLLM (抽象基类)
├── chat(messages, **kwargs) → str            # 同步对话
├── stream_chat(messages, **kwargs) → Iterator # 流式对话
└── generate_with_retry(messages, max_retries, **kwargs)  # 带重试

实现类:
├── OpenAIClient: POST /v1/chat/completions + SSE流式
└── LocalLLM: POST /api/chat (Ollama兼容)
```

### 5.2 自动后端检测 `get_llm_client()`

```python
1. 尝试 Ollama GET /api/tags (timeout=2s) → 成功则用 LocalLLM
2. 检查环境变量 OPENAI_API_KEY + OPENAI_BASE_URL → 有则用 OpenAIClient
3. 默认回退 LocalLLM (需自行启动Ollama)
```

### 5.3 降级策略总览

| Agent | 正常时 | 降级时 |
|-------|--------|--------|
| ProfileBuilder | LLM生成个性化对话 | 预定义问候模板+结构化追问 |
| ResourceGenerator | LLM生成6种资源内容 | 6种预定义Markdown/Mermaid/JSON模板 |
| Tutor | LLM生成6类型回答 | 通用学习指导模板 |
| KnowledgeBase | LLM+检索生成引用回答 | 检索片段直接拼接+学习建议 |

### 5.4 内容安全与 幻觉检测

**ContentSafetyFilter (__init__.py)**
- 敏感词模式匹配 (SENSITIVE_PATTERNS)
- 长度限制 (>50000字符拦截)
- 内容清理 (移除特殊字符/多余空白)

**HallucinationDetector (__init__.py)**
- 不确定性表达检测: `据说`、`大概是`、`也许`、`似乎`
- 虚假引用检测: `《...》...说` 正则匹配
- 可信领域验证: 计算机科学/数学/物理关键词匹配
- 接口: `check_factuality(content, topic) → (is_factual, warnings)`

---

## 6. 数据模型设计

### 6.1 SQLAlchemy ORM模型

| 模型名 | 表名 | 主键 | 核心字段 | 用途 |
|--------|------|------|---------|------|
| StudentProfileModel | `student_profiles_agent` | id | user_id, profile_data(JSON), cognitive_style, learning_speed, confidence | 画像持久化 |
| LearningResourceModel | `learning_resources_agent` | id | resource_id(UUID), user_id, resource_type, title, content, difficulty | 资源存储 |
| LearningPathModel | `learning_paths_agent` | id | path_id(UUID), user_id, path_data(JSON), current_step, completion_rate | 路径持久化 |
| AssessmentReportModel | `assessment_reports_agent` | id | user_id, report_data(JSON), overall_score, level | 评估报告存储 |
| ChatHistoryModel | `chat_history_agent` | id | user_id, session_id, role, content, agent_type | 对话历史 |
| KnowledgeDocumentModel | `knowledge_documents_agent` | id | document_id(UUID), user_id, title, file_type, content_hash, status | 知识库文档 |
| KnowledgeChunkModel | `knowledge_chunks_agent` | id | document_id, user_id, chunk_index, content, keywords(JSON) | 知识库分块 |
| DigitalHumanVideoTaskModel | `digital_human_video_tasks` | id | user_id, task_id, topic, task_status, payload | 数字人视频任务 |

### 6.2 数据库选择

使用 **SQLite** 作为数据库（`instance/quiz_system.db`），原因：
1. 零配置：无需安装MySQL/PostgreSQL
2. 便携性：单文件数据库，适合竞赛演示
3. Flask-SQLAlchemy ORM抽象：后续可平滑迁移到生产数据库

---

## 7. 前端技术栈

| 技术 | 用途 | 版本 |
|------|------|------|
| Bootstrap 5 | UI框架 | 5.x CDN |
| ECharts | 雷达图、趋势图等数据可视化 | 5.x |
| Mermaid.js | 思维导图实时渲染 | CDN latest |
| Font Awesome | 图标系统 | 6.x CDN |
| Jinja2 | 服务端模板引擎 | Flask内置 |
| 自定义CSS | 深墨蓝科技风主题 | 内联+独立文件 |

---

## 8. 部署方案

### 8.1 本地运行

```bash
# 方式一：手动启动
pip install -r requirements.txt
python run.py

# 方式二：一键启动
双击 start.bat

# 访问
http://127.0.0.1:5000
```

### 8.2 Docker部署

```yaml
# docker-compose.yml
services:
  web:
    build: .
    ports: ["5000:5000"]
    volumes: ["./instance:/app/instance"]
```

### 8.3 演示账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 教师 | teacher | teacher123 |
| 学生 | student | student123 |

启动时自动补齐/修正演示账号密码。

---

## 9. 项目目录结构

```
1/
├── app/
│   ├── __init__.py            # Flask应用工厂 create_app()
│   ├── multi_agent/           # 多智能体核心
│   │   ├── __init__.py        # 数据类/枚举/安全过滤器
│   │   ├── coordinator.py     # AgentCoordinator 协调器
│   │   ├── profile_agent.py   # ProfileBuilderAgent
│   │   ├── resource_agent.py  # ResourceGeneratorAgent
│   │   ├── planner_agent.py   # LearningPlannerAgent
│   │   ├── tutor_agent.py     # TutorAgent
│   │   ├── evaluator_agent.py # LearningEvaluatorAgent
│   │   ├── knowledge_agent.py # KnowledgeBaseAgent
│   │   └── llm_client.py      # LLM接口(BaseLLM/OpenAI/Local)
│   ├── models/
│   │   ├── user.py            # 用户模型
│   │   ├── agent_models.py    # 智能体数据模型(8个)
│   │   └── ...                # 其他模型
│   ├── routes/
│   │   ├── agent_system.py    # /agent/* 多智能体API
│   │   ├── main.py            # 首页、赛题对照等
│   │   ├── auth.py            # 登录注册
│   │   ├── quiz.py            # 题库与答题
│   │   ├── analysis.py        # 数据分析与报告
│   │   ├── student.py         # 学习计划与详情
│   │   ├── intelligent_assistant.py  # 智能问答页面
│   │   └── test.py            # 能力测试中心
│   └── templates/             # 49个HTML模板
├── data/
│   └── knowledge_base/
│       └── computer_organization_sample/  # 课程知识库样例包(6文件)
├── docs/                      # 参赛文档
├── outputs/                   # 答辩PPT等输出
├── instance/                  # SQLite数据库目录
├── run.py                     # 启动入口
├── start.bat                  # Windows一键启动
├── Dockerfile
├── docker-compose.yml
├── wsgi.py
├── requirements.txt
└── README.md
```

---

## 10. 创新点总结

1. **画像驱动全链路**：10维画像不是终点，而是贯穿资源生成、路径规划、辅导问答的输入依据
2. **多Agent专业分工**：7类智能体各司其职，协调器统一调度并行执行，架构可扩展
3. **RAG可信引擎**：8格式解析+双后端检索+LLM生成+引用标记+Mock过滤+降级兜底，六层保障
4. **评测回流闭环**：测评→报告→画像更新→路径调整，形成数据驱动的持续优化
5. **教学场景落地**：真实课程样例包+教师材料优先+资料不足拦截，针对教学场景深度定制
6. **工程化证据完善**：Docker+一键启动+证据包+截图+接口JSON，竞赛展示链条完整

---

*本开发说明书基于大模智学 v2.0 完整源码编写，所有功能描述均可对应到 `app/multi_agent/` 中的具体代码实现。*
