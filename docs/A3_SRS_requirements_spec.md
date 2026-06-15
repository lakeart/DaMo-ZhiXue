# A3 软件需求规格说明书 (SRS)

**项目名称**：大模智学  
**赛题名称**：A3-基于大模型的个性化资源生成与学习多智能体系统开发  
**版本**：v3.0  
**最后更新**：2026-06-15

---

## 1. 引言

### 1.1 编写目的

本文档用于明确"大模智学"项目在软件杯A3赛题下的完整需求边界、技术架构、用户角色、核心业务流程、非功能约束、验收标准与商业/社会价值论述。作为开发、测试、答辩及后续迭代的统一依据，确保所有参与方对系统目标有一致理解。

**本文档的核心定位**：
- **对评委**：展示需求分析的完整性与系统性，证明项目覆盖A3赛题全部要求
- **对开发者**：提供可执行的功能规格与接口契约，指导编码实现
- **对测试者**：定义验收标准与测试边界，支撑质量保证
- **对用户**：阐明系统能力边界与使用场景，设定合理预期

### 1.2 适用范围

系统面向三类核心用户——**学生**、**教师**与**管理员**，覆盖六大数据驱动的业务模块：

| 编号 | 业务模块 | 核心价值 | 涉及智能体 |
|:----:|---------|---------|-----------|
| M1 | **对话式学习画像构建** | 免填表、自然语言驱动的10维画像采集与动态更新 | ProfileBuilderAgent |
| M2 | **知识库管理与RAG问答** | 8格式文档解析、分块索引、双后端检索、证据驱动的可信回答 | KnowledgeBaseAgent |
| M3 | **多智能体协同资源生成** | 6种类型×N个知识点的并行个性化资源生成 | ResourceGeneratorAgent + Coordinator |
| M4 | **个性化学习路径规划** | 画像驱动、渐进难度、动态调整的多视图学习路径 | LearningPlannerAgent |
| M5 | **智能辅导与答疑** | 6种回答类型自动检测、流式输出、上下文保持、追问纠错 | TutorAgent |
| M6 | **学习效果评估与闭环优化** | 8维加权指标、雷达图可视化、评估结果回流画像与路径 | LearningEvaluatorAgent |

### 1.3 术语与缩写

| 术语 | 英文 | 说明 |
|------|------|------|
| 学习画像 | Learning Profile | 对学生目标、基础、偏好、薄弱点、节奏等维度的结构化描述，当前包含10个维度 |
| 多智能体 | Multi-Agent System | 由画像、资源生成、学习规划、辅导、评估、知识库、协调器等7类角色组成的协同系统 |
| RAG | Retrieval-Augmented Generation | 检索增强生成：先检索课程资料，再基于证据由LLM生成带引用回答，降低幻觉风险 |
| 课程知识库样例包 | Course Knowledge Base Sample | 用于上传验证的一组真实课程讲义、题库、术语表和复习提纲（计算机组成原理） |
| LLM | Large Language Model | 大语言模型，支持OpenAI兼容接口与Ollama本地模型 |
| TF-IDF | Term Frequency-Inverse Document Frequency | 词频-逆文档频率，当前默认语义检索算法 |
| ChromaDB | - | 可选向量数据库后端，支持嵌入向量语义检索 |
| SSE | Server-Sent Events | 服务端推送事件，实现流式回答逐字展示 |
| Coordinator | AgentCoordinator | 多智能体协调器，单例模式管理全局Agent调度 |

### 1.4 参考资料

| 编号 | 资料名称 | 用途 |
|:----:|---------|------|
| REF-1 | 第十五届中国软件杯大赛A3赛题说明 | 赛题要求与评分标准基准 |
| REF-2 | OpenAI Chat Completions API文档 | LLM接口规范参考 |
| REF-3 | Ollama API文档 | 本地LLM接口规范参考 |
| REF-4 | Flask 3.x官方文档 | Web框架最佳实践 |
| REF-5 | scikit-learn TfidfVectorizer文档 | 检索引擎参数调优参考 |
| REF-6 | ChromaDB官方文档 | 向量数据库集成参考 |

---

## 2. 项目背景与战略定位

### 2.1 行业背景与宏观趋势

#### 2.1.1 教育数字化转型趋势

全球教育科技(EdTech)市场正处于高速增长期。根据HolonIQ数据，全球教育科技市场规模预计在2025年达到4040亿美元，其中AI+教育细分赛道年复合增长率超过35%。中国作为全球最大的高等教育市场，拥有超过4000万在校大学生，个性化学习支持的需求日益迫切。

#### 2.1.2 大模型技术对教育的重塑

2023年以来，以GPT-4、文心一言、通义千问等为代表的大语言模型(LLM)技术快速发展，其在教育领域的应用潜力得到广泛认可：
- **教学内容生成**：LLM可自动生成讲义、习题、思维导图等多样化教学资源
- **个性化辅导**：基于学生画像的差异化教学成为可能
- **知识管理**：RAG技术使LLM能够基于特定课程材料提供可信回答
- **学习分析**：多维度的学习效果量化评估得以实现

#### 2.1.3 高校教学的实际痛点

| 痛点 | 具体表现 | 根因分析 |
|------|---------|---------|
| **资源碎片化** | 课程讲义散落各平台、题库版本混乱、参考资料难以系统获取 | 缺乏统一的课程知识管理入口 |
| **答疑时延高** | 课下问题需等待下次课或办公时间才能解答 | 教师资源有限，无法提供7×24支持 |
| **教学一刀切** | 统一进度和难度无法适应200+学生的差异化需求 | 传统教学范式受限于教师精力与班级规模 |
| **测评浅层化** | 考试分数难以定位具体薄弱知识点 | 缺乏细粒度能力诊断与归因分析 |
| **知识幻觉风险** | 学生使用通用AI工具可能获得与教材矛盾的回答 | 通用AI缺乏课程特定材料支撑 |
| **学习动力衰减** | 缺乏阶段性成就反馈和个性化激励 | 传统教学缺乏游戏化/里程碑式激励设计 |

### 2.2 项目定位与建设目标

#### 2.2.1 系统定位

"大模智学" 定位为**面向高校课程的AI-native个性化学习支持系统**，核心理念是：
- **不是**"大模型聊天窗口 + UI壳"的简单缝合
- **而是**将学习画像作为中心数据资产、让7类专业智能体分工协作、贯穿"理解学生→定制资源→规划路径→辅导答疑→评估反馈→动态调整"完整闭环的教学系统

#### 2.2.2 六大建设目标

| 编号 | 目标 | 量化指标 | 实现路径 |
|:----:|------|---------|---------|
| G1 | **对话驱动画像** | 10维画像覆盖，置信度≥0.3(首轮对话)，≥0.7(3轮后) | ProfileBuilderAgent多轮对话+关键词匹配+LLM语义理解 |
| G2 | **多智能体协同** | 7类Agent，6种资源类型并行生成 | Coordinator单例调度+ThreadPoolExecutor(max_workers=4) |
| G3 | **RAG可信问答** | 8种格式支持，引用追溯，幻觉检测 | KnowledgeBaseAgent六层保障体系 |
| G4 | **个性化学习路径** | 甘特图/日历/列表三视图，5级里程碑 | LearningPlannerAgent算法驱动的路径生成与动态调整 |
| G5 | **测评闭环优化** | 8维加权评估，评估结果自动回流画像与路径 | EvaluatorAgent → Profile/Planner数据回流 |
| G6 | **工程化落地** | 一键启动(Windows/Docker)，49个页面，10项自动化测试 | Flask+Bootstrap+ECharts+SQLite全栈工程化 |

### 2.3 商业价值与社会价值

#### 2.3.1 商业价值

| 价值维度 | 具体描述 | 预期受益 |
|---------|---------|---------|
| **教学效率提升** | AI辅助备课与答疑，降低教师重复性工作60%+ | 高校教学管理部门 |
| **学习效果优化** | 个性化学习路径相比统一教学，预期提升学习效率30-50% | 学生群体 |
| **教育公平促进** | 低成本AI辅导使优质教育资源的获取不再受地域和师资限制 | 教育资源薄弱地区 |
| **数据资产沉淀** | 学习画像与教学数据的长期积累可支撑教育研究与政策决策 | 教育研究机构 |

#### 2.3.2 社会价值

1. **促进教育公平**：通过AI技术降低个性化教育的边际成本，使欠发达地区学生也能获得高质量的个性化学习支持
2. **推动教学范式转型**：从"以教为中心"向"以学为中心"转变，AI系统成为教师的教学助手而非替代者
3. **建立可信AI教育标准**：RAG反幻觉机制为教育领域的AI应用提供可信性保障的技术范式
4. **培养自主学习能力**：通过画像驱动和闭环优化，引导大学生建立自我认知和自主学习习惯

### 2.4 核心优势框架

| 优势维度 | 传统方案 | 大模智学方案 | 差异化要点 |
|---------|---------|-------------|-----------|
| **画像构建** | 手动填表/静态标签 | 自然对话+10维动态更新 | 免填表、多维度、持续演进 |
| **资源生成** | 固定题库/统一讲义 | 6种类型+N个知识点按需并行生成 | 类型多样、画像驱动、一键生成 |
| **知识问答** | 预设答案/通用AI | RAG证据驱动+引用追溯+幻觉检测 | 基于课程材料、可追溯、防幻觉 |
| **学习规划** | 固定课表 | 渐近难度+5级里程碑+动态调整 | 个性化、可视化、自适应 |
| **效果评估** | 单一分数 | 8维雷达图+趋势分析+闭环优化 | 细粒度、可视化、可回流 |
| **架构扩展性** | 单体耦合 | 7类Agent松耦合+协调器调度 | 可扩展、可维护、可解释 |

---

## 3. 用户角色与权限

### 3.1 学生角色

默认演示账号：`student / student123`

| 权限项 | 功能说明 | 涉及页面 | 数据权限 |
|--------|---------|---------|---------|
| 系统登录 | 身份认证，获取个人学习空间 | `/auth/login` | 仅本人数据 |
| 能力测试 | 参与双专业方向(普通高校/民航特色)测评，查看逐题解析与答题统计 | `/test/assessment` | 本人答题记录 |
| 学习画像 | 通过对话构建并持续更新10维学习画像，查看画像置信度 | `/agent-system/learning-agent` | 本人画像 |
| 学习报告 | 查看8维雷达图、趋势分析、个性化改进建议(最多5条) | `/analysis/report` | 本人评估数据 |
| 学习计划 | 获取甘特图/日历/列表三视图的个性化学习路径，含周计划分配表 | `/student/learning-plan` | 本人路径数据 |
| 知识库管理 | 上传课程资料(8种格式)，管理已上传文档，查看检索引擎状态 | 知识库面板 | 本人上传文档 |
| RAG问答 | 基于已上传课程资料的证据驱动问答，获取带来源引用的可信回答 | 智能问答页 | 本人知识库 |
| 资源生成 | 基于学习画像生成6种个性化学习资源(讲义/导图/习题/阅读/脚本/代码) | 多智能体面板 | 本人生成资源 |
| 智能辅导 | 多模态学习答疑(6种答案类型自动匹配)，支持流式输出和追问纠错 | 智能问答页 | 本人对话历史 |
| 错题本 | 汇总所有错题，支持按知识点筛选和重新练习 | 能力测试结果页 | 本人错题 |

### 3.2 教师角色

默认演示账号：`teacher / teacher123`

| 权限项 | 功能说明 | 涉及页面 | 数据权限 |
|--------|---------|---------|---------|
| 系统登录 | 身份认证，获取教师分析工作台 | `/auth/login` | 所有学生数据(脱敏可配置) |
| 数据分析仪表盘 | 查看学生参与度、正确率、用时等核心指标 | `/teacher_dashboard` | 课程级聚合数据 |
| 学生群像分析 | 可视化展示学生群体的能力分布与学习特征 | `/analysis/` | 课程级统计数据 |
| 知识点掌握分析 | 识别课程薄弱环节，按知识点维度查看班级掌握度热力图 | `/analysis/knowledge-point` | 课程级分析 |
| 高级分析 | KMeans学习风格聚类、能力雷达图、效率分析、预测预警 | `/analysis/advanced` | 课程级分析 |
| 知识库管理 | 上传课程讲义、实验文档、题库等作为RAG知识来源 | 知识库管理面板 | 课程知识库 |
| 学生详情查看 | 查看单个学生答题详情、学习轨迹 | `/student/details` | 指定学生数据 |
| 题库管理 | 添加、编辑、删除题目，支持批量导入 | `/quiz/manage` | 课程题库 |

**教师角色的核心价值**：教师不是系统的旁观者，而是通过上传课程材料间接参与学生的个性化学习——教师的讲义成为RAG回答的证据来源，教师的题库支撑能力测评，教师的术语表影响知识图谱构建。

### 3.3 管理员角色

默认演示账号：`admin / admin123`

| 权限项 | 功能说明 | 涉及页面 | 数据权限 |
|--------|---------|---------|---------|
| 系统管理 | 维护演示账号、管理数据库、清理过期数据 | 管理面板 | 全部数据 |
| 全局监控 | 查看系统运行状态、Agent可用性、LLM后端状态 | `/agent/status` | 系统级监控 |
| 部署保障 | 确保答辩演示环境稳定运行 | Docker/启动脚本 | 基础设施 |

### 3.4 权限模型

```
权限层级:
├── 管理员 (admin): 全部功能 + 系统管理
├── 教师 (teacher): 数据查看(课程级) + 知识库管理 + 题库管理
└── 学生 (student): 个人数据(仅本人) + 学习功能(全部)
```

权限控制通过 Flask-Login 的 `@login_required` 装饰器 + `current_user.role` 属性判断实现，在路由层进行拦截。

---

## 4. 功能需求（详细规格）

### 4.1 模块一：对话式学习画像构建

#### 4.1.1 功能定位

本模块是整个系统的数据入口与核心资产。学习画像是所有后续智能体决策的输入依据——资源生成会根据学习速度调整难度，学习规划会根据薄弱知识点排优先级，辅导答疑会根据认知风格调整表达方式。

#### 4.1.2 画像维度完整定义

| 编号 | 维度名称 | 数据类型 | 取值范围 | 采集方式 | 优先级 | 对下游的影响 |
|:----:|---------|---------|---------|---------|:----:|------------|
| D1 | **知识基础** | `Dict[str, float]` | 各知识点 0.0~1.0 | 答题数据推断 + 对话声明 | P0 | 资源难度、路径起点、评估基准 |
| D2 | **认知风格** | `str` | visual/verbal/auditory/kinesthetic | 对话关键词匹配 + LLM推断 | P1 | 资源表达方式(图/文/声/动手) |
| D3 | **易错点模式** | `List[Dict]` | 错误类型列表 | 答题数据分析 | P1 | 练习题偏向、辅导重点 |
| D4 | **学习速度** | `str` | slow/medium/fast | 对话关键词+答题速度+关键词匹配 | P1 | 路径步长因子({fast:0.7, medium:1.0, slow:1.3}) |
| D5 | **兴趣方向** | `List[str]` | 兴趣领域列表 | 对话采集 | P2 | 资源主题推荐、拓展阅读方向 |
| D6 | **学习目标** | `List[str]` | 目标描述列表 | 对话采集 | P0 | 路径终点锚定、资源优先级 |
| D7 | **偏好知识点** | `List[str]` | 偏好主题列表 | 对话采集 | P2 | 激励性学习内容插入 |
| D8 | **薄弱知识点** | `List[str]` | 薄弱主题列表 | 答题+对话推断 | P0 | 路径优先级排序(priority=1) |
| D9 | **学习习惯** | `Dict[str, Any]` | 时间段/频率/单次时长/偏好方式 | 对话采集+行为数据推断 | P2 | 周计划时段分配 |
| D10 | **可用时间** | `Dict[str, int]` | 周各时段小时数 | 对话采集 | P1 | 周计划任务量计算 |

#### 4.1.3 完整交互流程

```
用户输入(M) → ContentSafetyFilter.filter(M) —安全检查层
              │  ├── 敏感词检测: SENSITIVE_PATTERNS正则匹配
              │  ├── 长度限制: len(M) > 50000 → 拒绝
              │  └── 不安全 → 返回拒绝响应 {response: "抱歉，无法处理该内容"}
              │
              └── 安全通过 ↓
              
ProfileBuilderAgent.process_message(M)
  ├── Step 1: 上下文构建
  │   └── _build_context():
  │       ├── 提取当前日期时间
  │       ├── 收集已知画像数据: {k: v for k, v in profile.items() if v}
  │       └── 格式化为自然语言上下文块
  │
  ├── Step 2: 消息组装
  │   └── messages = [
  │       {"role": "system", "content": PROFILE_SYSTEM_PROMPT},
  │       {"role": "assistant", "content": INITIAL_GREETING},
  │       *conversation_history[-6:],      # 最近6轮对话(上下文窗口)
  │       {"role": "user", "content": f"{context}\n\n用户消息：{M}"}
  │   ]
  │
  ├── Step 3: LLM对话生成
  │   └── try: response = LLM.chat(messages, temperature=0.8, max_tokens=4096)
  │       except: response = _get_fallback_response()  # 降级到模板
  │
  ├── Step 4: 画像信息提取
  │   └── _extract_profile_update(response):
  │       ├── JSON提取: re.search(r'\{[^{}]*\}', response)
  │       │   └── 尝试 json.loads() 解析
  │       ├── 反射更新: setattr(profile, key, value) for key, value in parsed.items()
  │       ├── 更新 extracted_info 集合
  │       └── 置信度计算: confidence = len(extracted_info) / 10
  │
  ├── Step 5: 关键词匹配推断
  │   └── _extract_keywords(response):
  │       ├── 认知风格匹配:
  │       │   visual:    ["看","图","画","视觉","眼睛","图表"]
  │       │   verbal:    ["读","写","说","文字","书籍","阅读"]
  │       │   auditory:  ["听","声音","音频","讲","口头"]
  │       │   kinesthetic: ["做","动手","实践","试","操作","试验"]
  │       └── 学习速度匹配:
  │           fast: ["快","迅速","很快","一下子"]
  │           slow: ["慢","需要时间","反复","仔细","花时间"]
  │
  ├── Step 6: 追问生成
  │   └── _generate_suggested_questions():
  │       └── 遍历10维 → 对缺失维度生成追问 → 取前3个
  │           ├── "你的薄弱科目是哪些课程？"
  │           ├── "你平时习惯什么时间学习？"
  │           └── "你有没有特别感兴趣的计算机领域？"
  │
  └── Step 7: 返回结果
      └── return {
          "response": str,            # AI的自然语言回复
          "profile_update": Dict,     # 本轮更新的维度
          "suggested_questions": [str, str, str],  # 建议追问(最多3个)
          "profile": {                # 完整10维画像当前状态
              "knowledge_base": {...},
              "cognitive_style": "visual",
              ...
              "confidence": 0.4
          }
      }
```

#### 4.1.4 System Prompt 设计（完整版）

```
你是一个专业的教育顾问智能体，名为"大模智学助手"。
你的职责是通过自然对话帮助学生建立全面的学习画像。

## 对话原则
1. 苏格拉底式提问：通过引导性问题而非直接问询获取信息
2. 自然流畅：不要像问卷一样逐一询问，而要在对话中自然引出信息
3. 画像驱动：每当你识别到新的学生特征，更新画像并告知学生
4. 鼓励为主：肯定学生的自我认知，同时给出建设性建议

## 你需要收集的10个维度
1. 知识基础：各知识点的当前掌握度(0-1)
2. 认知风格：视觉型/文字型/听觉型/动手型
3. 易错点：常犯的错误类型和知识点
4. 学习速度：慢速/中速/快速
5. 兴趣方向：感兴趣的计算机领域
6. 学习目标：短期和长期目标(如考研、就业、考证)
7. 偏好知识点：喜欢学习的主题
8. 薄弱知识点：感觉困难的主题
9. 学习习惯：时间段、频率、单次时长
10. 可用时间：每周可用于学习的小时数

## 输出格式
每次回复包括三部分：
1. 对学生输入的理解和共情回应
2. 如果提取到新的画像信息，以JSON格式输出更新：
   {"认知风格": "visual", "学习速度": "medium", ...}
3. 1-3个自然的跟进问题
```

#### 4.1.5 输入输出规范

**输入**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| user_message | str | ✅ | 任意长度的自然语言文本，无长度下限，>50000字符被安全层拦截 |

**输出**：
| 字段 | 类型 | 说明 |
|------|------|------|
| response | str | AI的自然语言对话回复(含共情、确认、建议) |
| profile_update | Dict | 本轮对话中新提取到的画像维度更新 |
| suggested_questions | List[str] | 基于当前缺失维度的追问建议(最多3个) |
| profile | Dict | 完整10维画像的当前状态，含confidence字段 |

**LLM参数**：temperature=0.8 (需要一定创造性使对话自然), max_tokens=4096

**降级策略**：LLM不可用时返回预定义的苏格拉底式模板响应，含结构化追问引导

---

### 4.2 模块二：知识库管理与RAG可信问答

#### 4.2.1 功能定位

知识库管理智能体是系统"可信回答"的核心引擎。在A3赛题对"反幻觉"要求的背景下，本模块通过六层工程保障实现了从文档上传到证据驱动回答的完整RAG管线，确保回答可追溯、有依据、不编造。

#### 4.2.2 支持的文件格式与解析深度

| 格式 | 扩展名 | 解析技术 | 解析深度 | 稳定性 | 适用场景 |
|------|--------|---------|---------|:------:|---------|
| 纯文本 | `.txt` | 编码自动检测(utf-8→gbk→gb18030→ignore) | 全文 | ✅ 稳定 | 课程讲义、实验文档 |
| Markdown | `.md` | 同纯文本 + 保留Markdown标记 | 全文 | ✅ 稳定 | 复习提纲、README |
| CSV | `.csv` | 同纯文本 | 全文 | ✅ 稳定 | 术语表、题库 |
| JSON | `.json` | 同纯文本 | 全文 | ✅ 稳定 | 结构化题库、习题集 |
| Word文档 | `.docx` | OpenXML ZIP → xml.etree遍历w:t节点 | 全文+格式保留 | ✅ 稳定 | 课程讲义、实验指导 |
| PDF文档 | `.pdf` | PyPDF2/PyPDF PdfReader逐页extract_text() | 文本层(不含扫描版) | ✅ 稳定 | 论文、教材 |
| PowerPoint新 | `.pptx` | OpenXML ZIP → ppt/slides/slide*.xml → 遍历a:t节点 | 逐slide提取文本 | ✅ 稳定 | 课件、答辩PPT |
| PowerPoint旧 | `.ppt` | 二进制正则: UTF-16LE `([\x20-\x7e\x80-\xff]\x00){4,}` + ASCII `[\x20-\x7e]{6,}` | 最佳努力提取 | ⚠️ 兼容 | 旧版课件 |

#### 4.2.3 完整文档处理管线

```
文件上传(F) → Step 0: 格式校验
              │  └── ext = os.path.splitext(F.filename)[1].lower()
              │      └── ext not in SUPPORTED_EXTENSIONS → 拒绝: "不支持的格式"
              │
              ├── Step 1: 文本提取 (按扩展名路由)
              │   ├── .docx: zipfile.ZipFile(F) → read('word/document.xml')
              │   │   └── 遍历 XML: for p in root.iter('{...}p'): text += p.text
              │   ├── .pdf:  PyPDF2.PdfReader(F) → for page: text += page.extract_text()
              │   ├── .pptx: zipfile.ZipFile(F) → for slide in slides: 遍历a:t节点
              │   ├── .ppt:  二进制正则提取UTF-16LE+ASCII → 控制字符清理
              │   └── 文本类: 编码检测(utf-8→gbk→gb18030→ignore)
              │
              ├── Step 2: 文本质量校验
              │   └── stripped_text = extract(F).strip()
              │       ├── len(stripped_text) < 20 → 拒绝: "文件内容过少"
              │       └── len(stripped_text) > 0 → 通过
              │
              ├── Step 3: SHA256去重检测
              │   └── content_hash = sha256(text.encode()).hexdigest()
              │       ├── DB查询: KnowledgeDocumentModel.query.filter_by(content_hash=hash)
              │       ├── 已存在 → 返回 {deduplicated: true, existing_doc_id: ...}
              │       └── 新文档 → 继续
              │
              ├── Step 4: 智能文本分块
              │   └── _chunk_text(text, chunk_size=800, overlap=120):
              │       ├── 清理多余换行: re.sub(r'\n{3,}', '\n\n', text).strip()
              │       ├── 滑动窗口: start=0; while start < len:
              │       │   ├── window = text[start: min(end, start+chunk_size)]
              │       │   ├── 查找切割点: max(rfind('\n'), rfind('。'), rfind('；'), rfind('.'))
              │       │   │   └── if cut > chunk_size*0.45: end = start+cut+1
              │       │   ├── chunk = window.strip()
              │       │   └── start = max(0, end-overlap)  # 重叠120字符
              │       └── return [chunk1, chunk2, ...]
              │
              ├── Step 5: 关键词提取
              │   └── _extract_keywords(text, limit=12):
              │       ├── 分词: 中文[\u4e00-\u9fa5]{2,} + 英文[A-Za-z][A-Za-z0-9_+-]{1,}
              │       ├── 词频统计: {token: count}
              │       └── 返回: sorted(freq.items(), key=lambda x: x[1], reverse=True)[:limit]
              │
              ├── Step 6: 数据库持久化
              │   ├── KnowledgeDocumentModel: id, user_id, title, file_type, content_hash, status
              │   └── KnowledgeChunkModel × N: document_id, chunk_index, content, keywords(JSON)
              │
              ├── Step 7: 向量存储同步
              │   └── if chroma_available:
              │       └── collection.add(ids=[f"chunk_{i}"], documents=[chunk.content], metadatas=[{...}])
              │
              └── 返回: {document, chunks_count, deduplicated: false}
```

#### 4.2.4 双后端检索引擎（完整设计）

##### 后端一：TF-IDF 语义检索（默认，零额外依赖）

| 参数 | 值 | 说明 |
|------|-----|------|
| analyzer | `'char_wb'` | 字符级+词边界感知，中英文混合友好 |
| ngram_range | `(2, 4)` | bi-gram到quad-gram，平衡精度与召回 |
| max_features | `6000` | 特征维度上限，控制计算复杂度 |
| 相似度计算 | `cosine_similarity` | 余弦相似度，值域[-1, 1] |
| 回退策略 | Jaccard词重叠 | 当TfidfVectorizer初始化失败时 |

##### 后端二：ChromaDB 向量检索（可选启用）

| 参数 | 说明 |
|------|------|
| 启用方式 | 环境变量 `KNOWLEDGE_RETRIEVAL_BACKEND=chroma` |
| 持久化路径 | `instance/chroma/knowledge` |
| Collection命名 | `knowledge_user_{user_id}` |
| 嵌入模型 | ChromaDB内置默认模型 |
| 相似度转换 | `similarity = 1 / (1 + distance)` |
| 自动降级 | ChromaDB不可用时自动回退到TF-IDF |

##### 后端自动选择逻辑

```
_init_retrieval_backend():
  1. 读取环境变量 KNOWLEDGE_RETRIEVAL_BACKEND (默认 "auto")
  2. if "chroma":
      try: import chromadb; client = PersistentClient(path); 返回 "chroma"
      except ImportError: log.warning; 回退 tfidf
  3. else: 默认 "tfidf"
```

#### 4.2.5 RAG问答生成完整链路

```
用户提问(Q) → knowledge_agent.answer(user_id, Q, top_k=4)
             │
             ├── Step 1: 语义检索
             │   └── contexts = search(user_id, Q, top_k)
             │       ├── TF-IDF模式: _rank_chunks(Q, all_chunks) → 取top_k
             │       └── Chroma模式: collection.query(query_texts=[Q], n_results=top_k)
             │
             ├── Step 2: 资料不足判断
             │   └── if len(contexts) == 0 or max(context.score) < threshold:
             │       └── return {
             │           "answer": "抱歉，当前知识库中没有与您问题相关的资料。\n建议：1.上传相关课程讲义 2.换个问法试试 3.从课程样例包开始",
             │           "confidence": 0,
             │           "citations": []
             │       }
             │
             ├── Step 3: LLM证据生成
             │   └── _generate_rag_answer(Q, contexts):
             │       ├── 构建系统提示:
             │       │   "你是高校课程知识库问答助手。"
             │       │   "仅根据提供的材料回答问题，禁止编造。"
             │       │   "材料不足时明确说明资料不足。"
             │       │   "引用时使用 [来源1] 格式注明出处。"
             │       │
             │       ├── 拼装检索上下文:
             │       │   for i, ctx in enumerate(contexts, 1):
             │       │       材料块 += f"[来源{i}] 文档：{ctx.document_title}（{ctx.filename}）\n"
             │       │       材料块 += f"片段：{ctx.content[:900]}\n\n"
             │       │
             │       ├── LLM调用: chat(messages, temperature=0.2, max_tokens=900)
             │       │   └── low temperature确保忠实于材料，不自由发挥
             │       │
             │       ├── Mock回答检测: _looks_like_mock_answer(answer)
             │       │   └── 检测模式: "感谢您的提问" / "这是很好的问题" 等模板化表述
             │       │   └── 触发时 → answer = '' (触发降级拼接)
             │       │
             │       └── 后处理:
             │           ├── 引用补全: if "参考来源" not in answer: 追加引用列表
             │           ├── 幻觉检测: HallucinationDetector.check_factuality(answer, Q)
             │           └── 返回: {answer, citations, confidence, warnings}
             │
             └── 返回完整结果
```

#### 4.2.6 反幻觉与安全机制的六层工程保障

| 层级 | 机制名称 | 实现方式 | 触发条件 | 保障效果 |
|:---:|---------|---------|---------|---------|
| L1 | **8格式文档解析** | 编码检测+OpenXML+PyPDF2+二进制正则 | 文件上传时 | 确保知识库覆盖多种课程材料格式 |
| L2 | **智能分块** | chunk_size=800, overlap=120, 句号/换行切割 | 文档索引时 | 保持语义完整性的细粒度检索单元 |
| L3 | **双后端检索** | TF-IDF(char_wb ngram) + ChromaDB向量 | 每次问答 | 多策略检索确保召回率 |
| L4 | **LLM证据生成** | System Prompt "仅根据材料"，temperature=0.2 | RAG问答模式 | 限制LLM自由发挥空间，降低编造概率 |
| L5 | **引用追溯+幻觉检测** | 回答自动附加[来源N]，HallucinationDetector | 回答生成后 | 可验证、可追溯、可质疑 |
| L6 | **多重兜底** | Mock检测→模板拼接→检索片段直展→"资料不足" | LLM失败/异常检测 | 确保系统在任何情况下都有合理输出 |

**创新亮点**："资料不足"不是缺陷，是Feature——未命中相关材料时明确告知而非强行回答，这在教学场景中比给出不确定的答案更有价值。

---

### 4.3 模块三：多智能体资源生成中心

#### 4.3.1 功能定位

资源生成智能体是多智能体系统"资源多样性"的集中体现。基于学生10维画像和指定知识点，利用LLM协同生成6种类型的个性化学习资源，并通过协调器的并行调度实现高效产出。

#### 4.3.2 六种资源类型完整规格

##### 资源1：课程讲义 (COURSE_DOCUMENT)

| 维度 | 规格 |
|------|------|
| **System Prompt角色** | 资深计算机教育专家，擅长将复杂概念转化为通俗易懂的讲解 |
| **内容结构** | ① 学习目标概述 → ② 核心概念定义 → ③ 详细知识讲解 → ④ 典型实例解析(2-3个) → ⑤ 实际应用场景 → ⑥ 拓展阅读指引 |
| **输出格式** | Markdown，支持代码块(` ``` `)、表格、有序/无序列表 |
| **长度控制** | 正文800-1500字（不含代码块和表格） |
| **画像适配** | 认知风格visual→增加图表建议；kinesthetic→增加动手实验；learning_speed=slow→更多基础铺垫 |
| **预估学习时长** | 15分钟 |
| **难度估算** | fast→hard, slow→easy, default→medium |
| **降级内容** | 预定义Markdown模板：概述+概念定义+示例+应用+阅读(各段固定模板) |
| **前端展示** | 卡片形式：标题+类型图标(fa-file-alt)+难度标签+时长+预览(前200字) |

##### 资源2：思维导图 (MIND_MAP)

| 维度 | 规格 |
|------|------|
| **System Prompt角色** | 知识可视化专家，擅长将知识体系转化为层次化思维导图 |
| **输出格式** | Mermaid `mindmap` 语法 |
| **层级结构** | 根节点(知识点名称) → 一级分支(核心主题，4-6个) → 二级分支(细节展开) → 三级分支(具体内容) |
| **节点规范** | 每节点1-5个关键词，避免完整句子；中文为主，术语保留英文 |
| **覆盖范围** | 知识点核心要素、关联关系、前置依赖、应用方向 |
| **画像适配** | visual认知风格→增加视觉化分支；verbal→增加文字说明节点 |
| **预估学习时长** | 10分钟(浏览理解) |
| **降级内容** | 预定义3-4层Mermaid模板，含固定节点结构 |
| **前端渲染** | Mermaid.js实时渲染为交互式思维导图，支持节点展开/收缩、缩放 |

##### 资源3：练习题集 (EXERCISES)

| 维度 | 规格 |
|------|------|
| **题型覆盖** | 选择题(4选1)、填空题、判断题、简答题、编程题 |
| **难度分层** | 基础题(40%) → 中等题(35%) → 进阶题(25%) |
| **数量规范** | 每种题型2-3道，合计10-15道 |
| **输出格式** | JSON数组，每道题含: `{type, question, options(选择题), answer, explanation, difficulty, knowledge_point}` |
| **解析要求** | 每题必须附带详细解析(不少于30字)，说明正确选项/答案的原因和常见错误 |
| **画像适配** | 学习速度slow→增加基础题比例至50%；薄弱知识点→优先出相关题 |
| **预估学习时长** | 20分钟 |
| **降级内容** | 预定义JSON题库模板(含3道选择题+2道填空题+1道简答题) |

##### 资源4：拓展阅读 (EXTENDED_READING)

| 维度 | 规格 |
|------|------|
| **资源类型** | 经典教材/学术论文/技术博客/视频课程/官方文档 |
| **数量** | 3-5个高质量资源 |
| **信息维度** | 资源类型→标题→作者/来源→推荐理由(50-80字)→适合程度(入门/进阶/研究)→获取链接 |
| **质量标准** | 权威性(经典教材/顶会论文)、实用性(与知识点直接相关)、时效性(优先3年内) |
| **画像适配** | 兴趣方向→优先推荐相关领域资源 |
| **预估学习时长** | 30分钟(快速浏览)至数小时(深度阅读) |

##### 资源5：视频脚本 (VIDEO_SCRIPT)

| 维度 | 规格 |
|------|------|
| **时长控制** | 脚本对应视频时长3-5分钟 |
| **脚本结构** | 开场引入(15秒)→核心讲解(2-3分钟)→案例演示(1分钟)→总结回顾(30秒) |
| **分镜格式** | 镜头编号 → 画面描述(视觉内容/动画/文字) → 旁白文本 → 时长(秒) |
| **表达风格** | 口语化，善用比喻和类比，适合教学讲解 |
| **预估学习时长** | 5分钟(阅读脚本) |
| **当前限制** | 生成文字脚本，非渲染视频文件；可辅助教师制作教学视频 |

##### 资源6：代码实操 (CODE_PRACTICE)

| 维度 | 规格 |
|------|------|
| **默认语言** | Python（可通过`programming_language`参数指定） |
| **内容结构** | 案例目标 → 预备知识 → 完整代码 → 逐行解析 → 运行结果展示 → 进阶挑战(2-3个) |
| **注释要求** | 完整中文注释，关键行需逐行解析说明 |
| **代码规范** | PEP8规范，函数名/变量名语义化，单函数不超过30行 |
| **画像适配** | knowledge_base中该知识点mastery低→更详细的基础注释 |
| **预估学习时长** | 45分钟 |
| **专用接口** | `generate_code_practice(topic, profile, language="Python")` |

#### 4.3.3 并行生成调度机制

```python
# Coordinator.generate_learning_resources() 中的并行调度
def generate_learning_resources(topics: List[str], resource_types: List[ResourceType]):
    # 前置条件检查
    if not current_profile or current_profile.confidence < 0.1:
        return {"error": "请先构建学习画像"}
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {}
        
        # 提交所有生成任务
        for topic in topics:
            for res_type in resource_types:
                future = executor.submit(
                    resource_agent.generate_resource,
                    res_type,       # ResourceType枚举
                    topic,          # 知识点名称
                    current_profile # 学生画像
                )
                futures[future] = {'topic': topic, 'type': res_type}
        
        # 收集结果(独立失败不影响其他任务)
        generated = []
        errors = []
        for future in as_completed(futures):
            info = futures[future]
            try:
                resource = future.result()
                generated.append(resource.to_card())
            except Exception as e:
                errors.append({
                    'topic': info['topic'],
                    'type': info['type'].value,
                    'error': str(e)
                })
    
    return {
        "resources": generated,
        "count": len(generated),
        "errors": errors,
        "types_generated": [r['type'] for r in generated]
    }
```

#### 4.3.4 资源生成完整工作流

```
Coordinator.generate_learning_resources(topics, resource_types)
  ├── 前置校验: current_profile 是否存在，confidence ≥ 0.1
  ├── 并行调度: ThreadPoolExecutor(max_workers=4)
  │   └── for each (topic × resource_type):
  │       ResourceGeneratorAgent.generate_resource(type, topic, profile)
  │         ├── _build_prompt():
  │         │   ├── 注入学生画像(用户名/认知风格/学习速度/兴趣/目标/薄弱点)
  │         │   └── 注入资源信息(类型/主题/额外上下文)
  │         ├── 选择System Prompt: SYSTEM_PROMPTS[resource_type]
  │         ├── LLM.chat(messages, temperature=0.7, max_tokens=4096)
  │         │   ├── 成功 → raw_content
  │         │   └── 失败 → _get_fallback_content(type, topic) [预定义模板]
  │         ├── ContentSafetyFilter.filter(raw_content) → 安全检测
  │         ├── HallucinationDetector.check_factuality(raw_content, topic) → 幻觉检测
  │         ├── ContentSafetyFilter.sanitize(raw_content) → 内容清理
  │         └── 创建 LearningResource{
  │               resource_id = uuid4(),
  │               resource_type, title = f"{topic} - {type.value}",
  │               content, target_topics=[topic],
  │               difficulty = _estimate(profile),
  │               estimated_time = TIME_MAP[type]
  │             }
  │         └── resource.to_card() → 前端友好格式
  │
  ├── 结果汇总: generated_resources[] + errors[]
  └── 返回: {resources: [card], count, errors, types_generated}
```

#### 4.3.5 资源卡片 (to_card) 输出规范

```json
{
  "id": "a1b2c3d4-...",
  "type": "course_document",
  "title": "链表 - 课程讲义",
  "preview": "链表是一种常见的数据结构，它由一系列节点组成...",
  "full_content": "# 链表\n\n## 学习目标\n...",
  "topics": ["链表", "数据结构"],
  "difficulty": "medium",
  "duration": 15,
  "icon": "fa-file-alt",
  "color": "#4364F7"
}
```

---

### 4.4 模块四：个性化学习路径规划

#### 4.4.1 功能定位

学习规划智能体将画像和资源转化为可执行的学习方案。核心价值在于"不是给所有学生同一个计划，而是根据每个人的基础、目标、速度和偏好生成差异化的路径"。

#### 4.4.2 路径规划算法（完整版）

```
LearningPlannerAgent.create_learning_path(profile, resources, goal)
  │
  ├── Phase 1: 目标知识点分析 _analyze_target_topics(profile)
  │   ├── 收集三类知识点:
  │   │   ├── 薄弱知识点 (profile.weak_topics)              → priority=1, type='weak'
  │   │   │   └── 语义: 最需要补习的，必须最优先
  │   │   ├── 未掌握知识点 (profile.knowledge_base中mastery<0.8) → priority=2, type='need_work'
  │   │   │   └── 语义: 需要加强的
  │   │   └── 偏好知识点 (profile.preferred_topics)          → priority=3, type='interest'
  │   │       └── 语义: 用来保持学习兴趣的
  │   └── 排序: ORDER BY priority ASC, mastery ASC(薄弱中的最弱→偏好中的最弱)
  │       └── LIMIT 10 个知识点
  │
  ├── Phase 2: 学习步骤规划 _plan_steps(profile, resources, target_topics)
  │   ├── speed_factor = {fast: 0.7, medium: 1.0, slow: 1.3}[profile.learning_speed]
  │   │
  │   └── for i, topic in enumerate(target_topics):
  │       ├── 当前知识点掌握度 mastery = profile.knowledge_base.get(topic, 0.5)
  │       │
  │       ├── [学习步骤]
  │       │   ├── title: f'学习：{topic}'
  │       │   ├── duration: 45 × speed_factor 分钟
  │       │   ├── difficulty: mastery<0.3→easy, 0.3≤mastery<0.7→medium, ≥0.7→hard
  │       │   ├── activities: base_activities = ['观看讲解','做笔记','理解核心概念']
  │       │   ├── type_specific:
  │       │   │   ├── type='weak' → activities += ['额外基础练习','绘制知识结构图']
  │       │   │   └── type='interest' → activities += ['拓展探索','关联知识挖掘']
  │       │   └── cognitive_style_adaptation:
  │       │       ├── visual → '绘制知识图谱'
  │       │       ├── verbal → '撰写学习笔记'
  │       │       ├── auditory → '录制讲解音频'
  │       │       └── kinesthetic → '动手编程实践'
  │       │
  │       ├── [练习步骤]
  │       │   ├── title: f'练习：{topic}'
  │       │   ├── duration: 30 × speed_factor 分钟
  │       │   ├── difficulty: 学习难度+1级(min(学习难度+1, hard))
  │       │   ├── activities: ['完成练习题','错题分析','总结反思']
  │       │   └── 配对资源: 从generated_resources中匹配EXERCISES类型资源
  │       │
  │       └── [阶段复习] (每3个知识点)
  │           └── if (i+1) % 3 == 0:
  │               ├── title: f'阶段复习：{topics[:3]}'
  │               ├── duration: 40 × speed_factor 分钟
  │               └── activities: ['回顾前阶段内容','综合练习','查漏补缺']
  │
  ├── Phase 3: 难度曲线生成 _generate_difficulty_curve(steps)
  │   └── 渐进式难度设计:
  │       ├── position 0.0~0.2: easy (入门期，建立信心)
  │       ├── position 0.2~0.4: easy/medium 交替 (过渡期，逐步加码)
  │       ├── position 0.4~0.7: medium (核心学习期，稳步推进)
  │       ├── position 0.7~0.9: medium/hard 交替 (深化期，挑战升级)
  │       └── position 0.9~1.0: hard (冲刺期，最后检验)
  │
  ├── Phase 4: 里程碑设定 _set_milestones(steps)
  │   └── 5级递进式里程碑:
  │       ├── M1: 入门成功 (完成前20%步骤)     → 解锁成就："初窥门径"
  │       ├── M2: 基础掌握 (完成前40%步骤)     → 解锁成就："渐入佳境"
  │       ├── M3: 能力提升 (完成前60%步骤)     → 解锁成就："驾轻就熟"
  │       ├── M4: 深入理解 (完成前80%步骤)     → 解锁成就："融会贯通"
  │       └── M5: 融会贯通 (完成100%步骤)      → 解锁成就："登峰造极"
  │
  └── Phase 5: 周计划分配 _get_weekly_plan(path, weekly_hours=10)
      ├── 总步骤时间 sum(durations)
      ├── 总周数 = ceil(总时间 / (weekly_hours × 60))
      ├── 按天分配: 每天 = weekly_hours / 7 小时
      │   └── 按morning/afternoon/evening时段分布
      └── 输出: [{day, tasks[{step, topic, duration}], total_hours}], summary
```

#### 4.4.3 路径动态调整算法

```
LearningPlannerAgent.adjust_path(path, progress):
  └── for each step in path.steps:
      ├── if step.step_number in progress.completed_steps:
      │   └── step.completed = True
      │
      └── if not step.completed:
          └── for each topic in step.topics:
              └── if topic in progress.assessment_results:
                  ├── if score < 0.6:
                  │   ├── step.difficulty = 'easy'      # 降低难度
                  │   ├── step.duration ×= 1.2           # 延长20%时间
                  │   └── step.activities.append('额外基础练习')
                  │
                  └── elif score > 0.9:
                      ├── step.duration ×= 0.8           # 缩短20%时间
                      └── step.activities.append('进阶挑战题')

  # 调整前后对比
  return {
    "original_path": path_snapshot,
    "adjusted_path": path,
    "changes": [
      {"step": 3, "difficulty": "medium→easy", "reason": "评估得分0.45<0.6"},
      {"step": 5, "duration": "45→36分钟", "reason": "评估得分0.95>0.9"}
    ]
  }
```

#### 4.4.4 前端三视图

| 视图 | 展示形式 | 核心元素 | 适用场景 |
|------|---------|---------|---------|
| **甘特图** | 横向时间线+彩色横条 | 步骤横条(颜色=难度)、里程碑标记点(⭐)、阶段分隔线 | 答辩展示：一目了然的视觉冲击 |
| **日历视图** | 7天网格布局+任务卡片 | 日期Header、每日任务卡片(标题+知识点+时长)、空状态占位 | 学生日常：每天做什么清清楚楚 |
| **列表视图** | 垂直步骤编号列表 | 步骤编号、标题、描述、知识点标签、活动列表、难度徽章、时长 | 详细查看：完整信息不遗漏 |

---

### 4.5 模块五：智能辅导与答疑

#### 4.5.1 回答类型自动检测逻辑

```
TutorAgent._detect_answer_type(question):
  关键词检测顺序(优先级从高到低):
  ├── 'code'         ← 含: 代码/编程/python/java/c++/写一个/实现/def/function
  ├── 'comparison'   ← 含: 比较/区别/vs/对比/差异/异同
  ├── 'explanation'  ← 含: 为什么/原理/原因/机制/解释/底层
  ├── 'guide'        ← 含: 如何/怎样/怎么/步骤/教程/指南
  ├── 'calculation'  ← 含: 计算/求解/证明/推导/公式/复杂度
  └── 'general'      ← default
```

#### 4.5.2 各回答类型格式规范

| 类型 | 回答结构模板 |
|------|------------|
| **code** | ① 问题分析(理解题意)→② 解决方案思路→③ 完整代码(带注释)→④ 逐段/逐行解析→⑤ 复杂度分析→⑥ 注意事项与变体 |
| **comparison** | ① 对比对象概述→② 对比维度表格(≥3维度)→③ 逐一详细解析→④ 适用场景建议→⑤ 选择指南 |
| **explanation** | ① 问题理解确认→② 核心原理讲解(由浅入深)→③ 类比/示例辅助理解→④ 知识延伸→⑤ 思考题引导 |
| **guide** | ① 目标确认→② 前置条件检查→③ 分步指南(3-7步)→④ 每步操作+预期结果→⑤ 常见问题预警 |
| **calculation** | ① 已知条件整理→② 公式/定理回顾→③ 推导过程(逐步)→④ 计算结果→⑤ 验证与讨论 |
| **general** | ① 问题理解→② 核心解答→③ 补充说明→④ 学习建议→⑤ 延伸问题 |

#### 4.5.3 流式回答技术实现

```python
def stream_answer(question, profile, context):
    # SSE格式输出 (text/event-stream)
    # 前端EventSource接收，逐字渲染
    
    ContentSafetyFilter.filter(question)  # 安全检查
    
    yield "data: " + json.dumps({"type": "start"}) + "\n\n"
    
    try:
        for chunk in LLM.stream_chat(messages, temperature=0.7):
            yield "data: " + json.dumps({"type": "chunk", "content": chunk}) + "\n\n"
    except:
        # 降级：直接返回完整降级文本
        yield "data: " + json.dumps({"type": "full", "content": fallback_answer}) + "\n\n"
    
    yield "data: " + json.dumps({"type": "end"}) + "\n\n"
```

---

### 4.6 模块六：学习效果评估与闭环

#### 4.6.1 8维加权指标体系

| 指标 | 权重 | 计算方式 | 数据来源 | 评分范围 |
|------|:---:|---------|---------|:------:|
| 知识掌握度 | 25% | `avg(profile.knowledge_base.values()) × 100` | 画像知识基础 | 0-100 |
| 练习准确率 | 20% | `correct_count / total_count × 100` | 答题记录 | 0-100 |
| 概念理解度 | 15% | 概念类题目正确率 × 100 | 答题记录(概念题型) | 0-100 |
| 问题解决能力 | 15% | difficulty=hard题目正确率 × 100 | 答题记录(高难度) | 0-100 |
| 学习效率 | 10% | `(expected_time/actual_time × 100 + knowledge_mastery) / 2` | 答题耗时+知识掌握 | 0-100 |
| 时间管理 | 5% | `(punctuality_score + planning_score) × 50` | 学习行为数据 | 0-100 |
| 学习持续性 | 5% | `min(100, current_streak × 10)` | 连续学习天数 | 0-100 |
| 学习投入度 | 5% | `(consistency + focus_ratio×100 + resource_usage×100) / 3` | 综合行为指标 | 0-100 |

#### 4.6.2 数据回流闭环（完整链路）

```
能力测试完成 → quiz_results 写入
              │
              ├──→ EvaluatorAgent.evaluate(profile, learning_data)
              │      ├── 8维指标计算 → overall_score
              │      ├── 等级评定: >=90优秀, 75-89良好, 60-74一般, <60需改进
              │      ├── 趋势分析: improving_topics vs declining_topics
              │      ├── 改进建议生成(最多5条，基于薄弱指标)
              │      └── 输出: AssessmentReport {overall_score, dimensions, trends, recommendations}
              │
              ├──→ 数据持久化: AssessmentReportModel(report_data=JSON)
              │
              ├──→ 画像回流:
              │      └── Coordinator.update_profile_from_assessment(report)
              │          ├── profile.knowledge_base[topic] += score * 0.2  (加权更新)
              │          ├── profile.weak_topics ← 从declining_topics补充
              │          └── profile.strong_topics ← 从improving_topics补充
              │
              ├──→ 路径回流:
              │      └── Coordinator.adjust_path_from_assessment(report)
              │          └── LearningPlannerAgent.adjust_path(path, report.progress)
              │
              └──→ 前端展示:
                     ├── 8维雷达图: ECharts radar chart
                     ├── 趋势对比: previous vs current
                     └── 建议卡片: 可操作的具体建议
```

---

### 4.7 多智能体协同架构（全貌）

#### 4.7.1 7类Agent角色矩阵

| 编号 | Agent类名 | 文件 | 角色定位 | 核心能力 | 依赖 |
|:----:|----------|------|---------|---------|------|
| A1 | `ProfileBuilderAgent` | `profile_agent.py` | 画像采集维护 | 10维画像+LLM对话+关键词匹配 | 无(独立) |
| A2 | `ResourceGeneratorAgent` | `resource_agent.py` | 多类型资源生成 | 6种SystemPrompt+并行生成+安全过滤 | A1(画像) |
| A3 | `LearningPlannerAgent` | `planner_agent.py` | 路径规划调度 | 目标分析+步骤规划+动态调整+三视图 | A1(画像)+A2(资源) |
| A4 | `TutorAgent` | `tutor_agent.py` | 智能答疑辅导 | 6种答案+流式SSE+追问纠错 | A1(画像) |
| A5 | `LearningEvaluatorAgent` | `evaluator_agent.py` | 效果量化评估 | 8维加权+雷达图+趋势+回流 | A1(画像)+数据 |
| A6 | `KnowledgeBaseAgent` | `knowledge_agent.py` | RAG知识管理 | 8格式解析+双后端检索+LLM生成 | 无(独立) |
| A7 | `AgentCoordinator` | `coordinator.py` | 协同调度 | 会话管理+并行调度+日志追溯 | A1~A6 |

#### 4.7.2 协调器完整API

| 方法 | HTTP路径 | 方法 | 前置条件 | 输出 |
|------|---------|:---:|---------|------|
| `initialize_session` | `/agent/init` | POST | user_id, username | session_id, profile, welcome_message |
| `build_profile` | `/agent/profile` | POST | 已初始化会话 | response, profile_update, suggested_questions |
| `generate_learning_resources` | `/agent/resources` | POST | profile.confidence ≥ 0.1 | resources[], count, errors |
| `create_personalized_plan` | `/agent/plan` | POST | 有资源和画像 | path_data, weekly_plan, milestones |
| `ask_question` | `/agent/ask` | POST | 无 | answer, citations, answer_type |
| `stream_ask_question` | `/agent/stream` | GET(SSE) | 无 | SSE流式回答 |
| `evaluate_and_adjust` | `/agent/evaluate` | POST | 有测评数据 | report, path_changes |
| `get_system_status` | `/agent/status` | GET | 无 | 7个Agent状态+会话信息 |
| `reset_session` | `/agent/reset` | POST | 无 | new_session_id |
| `export_session_data` | `/agent/export` | GET | 有会话 | 完整会话数据JSON导出 |

#### 4.7.3 典型场景协同工作流

```
学生学习完整闭环 (6步循环):

Step 1: initialize_session → 创建画像 (confidence=0)
Step 2: build_profile × N轮 → 对话完善画像 (confidence→0.3→0.6→0.8)
Step 3: 完成能力测试 → quiz_results入库
Step 4: generate_learning_resources → 并行生成6种资源
Step 5: create_personalized_plan → 生成学习路径+周计划
Step 6: evaluate_and_adjust → 基于测评调整路径难度和时长
         ↓ (循环回Step 2或Step 4，画像和路径持续优化)
```

---

### 4.8 工程化与部署功能

| 功能 | 实现 | 价值 |
|------|------|------|
| Windows一键启动 | `start.bat`: 自动检测Python→加载.env→启动Flask | 评委/演示者零门槛启动 |
| Docker部署 | `Dockerfile` + `docker-compose.yml` + `nginx.conf` | 生产级容器化部署 |
| 数据库零配置 | SQLite (`instance/quiz_system.db`) | 无需安装数据库服务 |
| 前端渲染 | Flask Jinja2 + Bootstrap 5 + ECharts + Mermaid.js | 专业视觉体验 |
| 演示账号 | admin/teacher/student 自动修正密码 | 登录即用 |
| 单例模式 | `get_coordinator()` 全局单例 | 避免多实例状态不一致 |
| 流式输出 | SSE (Server-Sent Events) | 逐字实时展示AI回答 |

---

## 5. 非功能需求

### 5.1 性能指标

| 指标 | 目标值 | 测量方式 | 当前状态 |
|------|:-----:|---------|:------:|
| 基础页面TTFB | < 500ms | Flask内置日志 | ✅ 达标 |
| 完整页面加载(LCP) | < 3s | 浏览器DevTools | ✅ 达标 |
| 文档上传处理(100KB) | < 30s | 上传至索引完成计时 | ✅ 达标 |
| RAG问答端到端延迟 | < 15s | 提问到回答显示计时 | ✅ 达标 |
| 资源并行生成(6种) | < 60s | 开始生成到全部返回 | ✅ 达标 |
| LLM调用超时 | 60s(同步)/120s(流式) | requests timeout | ✅ 已配置 |
| 并发资源生成数 | 4 | ThreadPoolExecutor max_workers | ✅ 已配置 |
| 知识库检索延迟 | < 1s | TF-IDF cosine计算 | ✅ 达标 |

### 5.2 安全可信要求

| 编号 | 安全要求 | 实现机制 | 保障层级 |
|:----:|---------|---------|:---:|
| S1 | 知识库回答必须基于已上传资料 | System Prompt "仅根据材料回答，禁止编造" + temperature=0.2 | L4 |
| S2 | 材料不足时明确提示 | 检索结果为空或score低于阈值 → 返回"资料不足" | L6 |
| S3 | 回答必须附带来源引用 | 自动追加 [来源N] 引用列表 | L5 |
| S4 | 输入内容安全过滤 | ContentSafetyFilter敏感词检测+长度限制 | L1 |
| S5 | 输出内容安全清理 | ContentSafetyFilter.sanitize() | L1 |
| S6 | 幻觉检测 | HallucinationDetector检查不确定性表达+虚假引用 | L5 |
| S7 | Mock回答过滤 | _looks_like_mock_answer() 检测模板化通用回复 | L6 |
| S8 | 教师材料优先 | 当多来源存在差异时，优先以教师上传材料为准 | L4 |

### 5.3 可维护性要求

| 编号 | 维护性要求 | 实现方式 |
|:----:|----------|---------|
| M1 | 模块高内聚低耦合 | 7个Agent各自独立文件，通过Coordinator统一调度 |
| M2 | 检索后端可替换 | TF-IDF → ChromaDB 通过环境变量切换，无需改代码 |
| M3 | LLM可替换 | OpenAI兼容接口 → Ollama本地模型自动检测切换 |
| M4 | 配置集中管理 | `.env` 环境变量文件统一管理所有密钥和配置 |
| M5 | 日志完善 | logging模块记录关键操作、异常、Agent调用链 |
| M6 | 代码风格一致 | 统一使用Type Hints + Docstrings | 

### 5.4 可扩展性要求

| 编号 | 扩展性要求 | 当前设计 | 扩展方向 |
|:----:|----------|---------|---------|
| E1 | 新增Agent | 在`multi_agent/`下新增类，Coordinator注册 | PPT生成Agent、视频渲染Agent |
| E2 | 新增资源类型 | ResourceType枚举扩展 + System Prompt字典扩展 | Flash卡片、知识图谱、音频讲解 |
| E3 | 新增文件格式 | `_extract_xxx_text()` + SUPPORTED_EXTENSIONS扩展 | EPUB、LaTeX |
| E4 | 新增评估维度 | `_compute_new_dimension()` 加入加权公式 | 协作能力、创新能力 |
| E5 | 多语言支持 | 画像维度+System Prompt翻译 | 英文版、中英双语版 |

---

## 6. 典型业务流程

### 6.1 学生首次使用完整闭环（12步40分钟）

```
Step 1  [1min]   登录 → student/student123 → 进入学习仪表盘
Step 2  [5min]   学习画像 → 对话: "我是大二计科学生，数据结构学得不好，准备考研408"
Step 3  [实时]   右侧面板10维画像逐项更新 (confidence: 0→0.3→0.5)
Step 4  [10min]  能力测试 → 选择"普通高校专业方向" → 完成10题
Step 5  [即时]   查看测试结果: 总分78/难度分布/逐题解析
Step 6  [2min]   学习报告 → 查看8维雷达图(知识掌握60/练习准确75/概念理解70/...)
Step 7  [即时]   查看个性化改进建议: "建议重点加强数据结构-树/图部分"
Step 8  [1min]   点击"调整学习计划" → 路径自动更新(链表步骤难度medium→easy)
Step 9  [2min]   学习计划 → 切换甘特图/日历/列表三视图
Step 10 [3min]   知识库 → 上传3个课程文件(讲义+复习提纲+术语表)
Step 11 [1min]   RAG问答: "什么是冯诺依曼架构？" → 获取带[来源1][来源2]的引用回答
Step 12 [5min]   资源生成 → 选择"数据结构-链表"+思维导图+练习题 → 查看生成卡片

总演示时长: 约30-40分钟 (全链路完整演示)
答辩精简版: 约6-7分钟 (跳过快进展示关键节点)
```

### 6.2 教师材料投喂闭环

```
Step 1  教师登录 (teacher/teacher123)
Step 2  准备课程资料包: 讲义/实验文档/题库/术语表/PPT课件
Step 3  上传到知识库 → 系统自动解析+分块+索引
Step 4  学生在问答中自动引用教师材料([来源: 教师讲义.pdf])
Step 5  学生测评结果反馈到教师分析工作台
Step 6  教师识别班级薄弱知识点 → 针对性补充教学材料
Step 7  (循环) 学生使用更新后的知识库 → 测评结果改善 → 教师调整教学策略
```

---

## 7. 数据字典

### 7.1 StudentProfile (学生画像)

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|:---:|--------|------|
| user_id | int | ✅ | - | 关联User表外键 |
| username | str | ✅ | - | 用户名 |
| knowledge_base | Dict[str, float] | - | {} | 知识点→掌握度(0.0~1.0) |
| cognitive_style | str | - | "visual" | visual/verbal/auditory/kinesthetic |
| error_patterns | List[Dict] | - | [] | 易错点: [{type, topic, frequency}] |
| learning_speed | str | - | "medium" | slow/medium/fast |
| interests | List[str] | - | [] | 兴趣方向 |
| goals | List[str] | - | [] | 学习目标 |
| preferred_topics | List[str] | - | [] | 偏好知识点 |
| weak_topics | List[str] | - | [] | 薄弱知识点 |
| strong_topics | List[str] | - | [] | 强项知识点 |
| study_habits | Dict[str, Any] | - | {} | {时段, 频率, 单次时长, 偏好方式} |
| available_time | Dict[str, int] | - | {} | {周一~周日: 小时数} |
| confidence | float | - | 0.0 | 画像置信度: len(extracted_info)/10 |

### 7.2 LearningResource (学习资源)

| 字段 | 类型 | 说明 |
|------|------|------|
| resource_id | UUID4 | 资源唯一标识 |
| resource_type | ResourceType | 枚举: COURSE_DOCUMENT/MIND_MAP/EXERCISES/EXTENDED_READING/VIDEO_SCRIPT/CODE_PRACTICE |
| title | str | "知识点 - 资源类型" |
| content | str | 完整Markdown/JSON/Mermaid内容 |
| target_topics | List[str] | 目标知识点列表 |
| difficulty | str | easy/medium/hard |
| estimated_time | int | 预估学习分钟 |
| source_agent | str | "ResourceGeneratorAgent" |

### 7.3 LearningPath (学习路径)

| 字段 | 类型 | 说明 |
|------|------|------|
| path_id | UUID4 | 路径唯一标识 |
| user_id | int | 关联用户 |
| steps | List[Step] | 步骤列表(每步含: step_number, title, duration, difficulty, activities, topics, completed) |
| total_duration | int | 总预估分钟 |
| difficulty_curve | List[str] | 渐进难度曲线序列 |
| milestones | List[Milestone] | 5级里程碑(每级含: name, target_step, achievement, unlocked) |
| weekly_plan | List[DayPlan] | 7天日程分配 |

---

## 8. 验收标准

| 编号 | 验收项 | 验收方法 | 通过标准 |
|:----:|-------|---------|---------|
| AC-1 | 系统可启动 | 双击`start.bat` | `http://127.0.0.1:5000` 可访问，返回200 |
| AC-2 | 三套账号可用 | admin/teacher/student分别登录 | 均登录成功，跳转正确页面 |
| AC-3 | 能力测试完整体验 | student登录→选择方向→完成10题→提交 | 显示总分+难度分布+逐题解析 |
| AC-4 | 学习画像对话构建 | 输入≥3轮自然语言对话 | 10维画像≥6个有值，confidence≥0.3 |
| AC-5 | 6种格式上传 | 上传TXT/MD/CSV/JSON/DOCX/PDF/PPTX | 每种格式解析成功，创建分块 |
| AC-6 | RAG可信问答 | 上传知识库→提问"冯诺依曼架构" | 回答含[来源N]引用，confidence>0 |
| AC-7 | 资料不足拦截 | 无相关资料时提问 | 返回"资料不足"提示，非编造回答 |
| AC-8 | 学习路径三视图 | 生成路径→切换视图 | 甘特图/日历/列表均可正常渲染 |
| AC-9 | 6种资源生成 | 选择全部资源类型→生成 | 每种类型均有有效输出(含降级) |
| AC-10 | 8维雷达图渲染 | 完成测试→进入学习报告 | ECharts雷达图8轴正常显示、有数据 |
| AC-11 | 评估回流路径调整 | 评估后查看学习路径变化 | 部分步骤难度/时长/活动发生变化 |
| AC-12 | Docker部署 | `docker-compose up -d` | 服务启动，端口映射正常 |
| AC-13 | 文档完整性 | 逐一核对8类文档 | 所有文档内容充实、无空章节 |
| AC-14 | 课程样例包验证 | 上传6个样例文件→提问 | 全链路：解析/索引/检索/问答/引用 均正常 |

---

## 9. 附录：LLM集成规范

### 9.1 LLM客户端架构

```
BaseLLM (抽象基类: app/multi_agent/llm_client.py)
├── __init__(base_url, api_key, model)
├── chat(messages, temperature, max_tokens) → str
├── stream_chat(messages, **kwargs) → Iterator[str]
└── generate_with_retry(messages, max_retries=3, **kwargs) → str

├── OpenAIClient(BaseLLM)
│   ├── chat(): POST {base_url}/v1/chat/completions
│   │   └── 请求体: {model, messages, temperature, max_tokens}
│   └── stream_chat(): POST + stream=true → SSE解析逐行yield
│
└── LocalLLM(BaseLLM)
    ├── chat(): POST {base_url}/api/chat
    │   └── 请求体: {model, messages, options: {temperature}}
    └── stream_chat(): POST + stream=true → JSON行解析yield
```

### 9.2 各Agent LLM调用参数

| Agent | Temperature | Max Tokens | 选择理由 |
|-------|:----------:|:----------:|---------|
| ProfileBuilder | 0.8 | 4096 | 需要自然对话的创造性，温度偏高使对话不机械 |
| ResourceGenerator | 0.7 | 4096 | 需要专业内容输出但保持一定创造力 |
| Tutor | 0.7 | 4096 | 平衡准确性与表达自然度 |
| KnowledgeBase(RAG) | 0.2 | 900 | 极低温度确保忠实于检索材料，token限制因材料已提供 |
| Evaluator | - | - | 纯规则计算，不调用LLM |

### 9.3 LLM自动后端选择逻辑

```
get_llm_client() → BaseLLM:
  1. 检查 Ollama: GET {OLLAMA_BASE_URL}/api/tags (timeout=2s)
     └── 成功 → return LocalLLM(ollama_url, ollama_model)
  2. 检查环境变量: OPENAI_API_KEY and OPENAI_BASE_URL
     └── 存在 → return OpenAIClient(openai_url, openai_key, openai_model)
  3. 默认回退: LocalLLM(默认localhost:11434)
     └── 需用户自行启动Ollama服务
```

### 9.4 全局降级策略矩阵

| Agent | 正常行为 | LLM不可用降级 | Mock回答降级 |
|-------|---------|-------------|-------------|
| ProfileBuilder | LLM苏格拉底式对话 | 预定义问候模板+结构化追问列表 | 画像从预定义模板提取 |
| ResourceGenerator | LLM生成6种类型内容 | 6种预定义Markdown/Mermaid/JSON模板 | 模板内容直接使用 |
| Tutor | LLM生成6种类型回答 | 通用学习指导模板回答 | RAG模式触发检索拼接 |
| KnowledgeBase | LLM+RAG生成引用回答 | 检索片段直接拼接+学习建议引导 | 同LLM不可用降级 |

---

*本SRS文档基于大模智学v3.0实际代码编写，所有功能描述均可从 `app/multi_agent/` 源码中对应验证。文档结构遵循IEEE 830-1998标准建议，并根据赛题要求进行了教育场景特化。*
