from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models.user import User
from app.models.quiz import Question, QuizSubmission
from sqlalchemy import func, case, desc
from app import db
import json
import random
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)


def _quiz_max_score_case():
    return case(
        (QuizSubmission.question_style == '\u5224\u65ad\u9898', 2),
        (QuizSubmission.question_style == '\u89e3\u7b54\u9898', 10),
        (QuizSubmission.question_style == '\u7f16\u7a0b\u9898', 15),
        else_=5
    )


def _teacher_dashboard_data():
    max_score_case = _quiz_max_score_case()
    normalized_score = (QuizSubmission.score * 100.0) / max_score_case

    total_students = User.query.filter_by(role='student').count()
    total_questions = Question.query.count()
    total_submissions = QuizSubmission.query.count()
    active_students = db.session.query(func.count(func.distinct(QuizSubmission.student_id))).scalar() or 0
    average_accuracy = db.session.query(func.avg(normalized_score)).scalar() or 0
    average_time = db.session.query(func.avg(QuizSubmission.time_consumed)).scalar() or 0

    recent_rows = db.session.query(
        QuizSubmission.student_name,
        QuizSubmission.student_id,
        QuizSubmission.question_topic,
        QuizSubmission.question_style,
        QuizSubmission.score,
        QuizSubmission.submit_time,
        QuizSubmission.time_region
    ).order_by(desc(QuizSubmission.submit_time)).limit(8).all()

    recent_submissions = []
    for row in recent_rows:
        max_score = 5
        if row.question_style == '\u5224\u65ad\u9898':
            max_score = 2
        elif row.question_style == '\u89e3\u7b54\u9898':
            max_score = 10
        elif row.question_style == '\u7f16\u7a0b\u9898':
            max_score = 15

        recent_submissions.append({
            'student_name': row.student_name or row.student_id or 'Demo Student',
            'student_id': row.student_id,
            'topic': row.question_topic or 'Uncategorized',
            'question_style': row.question_style or 'Unknown',
            'score': row.score or 0,
            'max_score': max_score,
            'accuracy': round(((row.score or 0) / max_score) * 100, 1) if max_score else 0,
            'submit_time': row.submit_time,
            'time_region': row.time_region or 'N/A'
        })

    weak_topic_rows = db.session.query(
        QuizSubmission.question_topic.label('topic'),
        func.count(QuizSubmission.id).label('submission_count'),
        func.avg(normalized_score).label('avg_accuracy')
    ).filter(
        QuizSubmission.question_topic.isnot(None)
    ).group_by(
        QuizSubmission.question_topic
    ).order_by(
        func.avg(normalized_score).asc(),
        func.count(QuizSubmission.id).desc()
    ).limit(6).all()

    weak_topics = [{
        'topic': row.topic,
        'submission_count': row.submission_count,
        'avg_accuracy': round(float(row.avg_accuracy or 0), 1)
    } for row in weak_topic_rows]

    student_rows = db.session.query(
        QuizSubmission.student_name.label('student_name'),
        QuizSubmission.student_id.label('student_id'),
        func.count(QuizSubmission.id).label('submission_count'),
        func.avg(normalized_score).label('avg_accuracy'),
        func.max(QuizSubmission.submit_time).label('last_submit')
    ).group_by(
        QuizSubmission.student_name,
        QuizSubmission.student_id
    ).order_by(
        desc(func.count(QuizSubmission.id)),
        desc(func.max(QuizSubmission.submit_time))
    ).limit(6).all()

    student_snapshots = [{
        'student_name': row.student_name or row.student_id or 'Demo Student',
        'student_id': row.student_id,
        'submission_count': row.submission_count,
        'avg_accuracy': round(float(row.avg_accuracy or 0), 1),
        'last_submit': row.last_submit
    } for row in student_rows]

    topic_count = db.session.query(func.count(func.distinct(Question.topic))).scalar() or 0

    return {
        'stats': {
            'total_students': total_students,
            'total_questions': total_questions,
            'total_submissions': total_submissions,
            'active_students': active_students,
            'topic_count': topic_count,
            'average_accuracy': round(float(average_accuracy or 0), 1),
            'average_time': round(float(average_time or 0), 1)
        },
        'recent_submissions': recent_submissions,
        'weak_topics': weak_topics,
        'student_snapshots': student_snapshots
    }


def _competition_readiness_data():
    """A3 赛题/国奖要求完成度矩阵，用于答辩演示与研发自查。"""
    modules = [
        {
            'name': '对话式学习画像构建',
            'score': 92,
            'level': '领先',
            'icon': 'fa-user-graduate',
            'requirements': ['自然语言收集画像', '10维画像抽取', '画像持久化', '前后变化可视化', '群体画像分析'],
            'evidence': [
                'ProfileBuilderAgent 支持对话式画像构建',
                'StudentProfile 包含知识基础、认知风格、学习速度、兴趣、目标等 10 维',
                '智能学习中心展示画像前后变化'
            ],
            'next_steps': ['继续增强画像历史版本留存与班级画像对比']
        },
        {
            'name': '知识库 RAG 与反幻觉',
            'score': 86,
            'level': '核心突破',
            'icon': 'fa-database',
            'requirements': ['文件上传', '文档解析', '分块索引', '语义检索', '带来源回答', '反幻觉提示'],
            'evidence': [
                'KnowledgeBaseAgent 支持 TXT/Markdown/CSV/JSON/DOCX/PDF',
                '完成上传、解析、分块、TF-IDF 语义检索、RAG 引用回答闭环',
                '/agent/knowledge/ask 默认优先使用知识库证据'
            ],
            'next_steps': ['可扩展 ChromaDB/Milvus 向量库与星火真实生成接口']
        },
        {
            'name': '学习路径规划 Agent',
            'score': 90,
            'level': '完整可演示',
            'icon': 'fa-route',
            'requirements': ['自动生成路径', '阶段/里程碑', '周计划', '甘特图', '日历视图', '动态调整'],
            'evidence': [
                'LearningPlannerAgent 生成步骤、难度曲线、里程碑和周计划',
                '前端提供时间线、甘特图、周日历三视图',
                '评估结果可反向调整后续步骤'
            ],
            'next_steps': ['补充学习进度拖拽更新与计划版本对比']
        },
        {
            'name': '多模态资源生成中心',
            'score': 88,
            'level': '优势突出',
            'icon': 'fa-wand-magic-sparkles',
            'requirements': ['课程讲义', '思维导图', '练习题', '拓展阅读', '代码实操', 'PPT', '视频脚本', '知识卡片'],
            'evidence': [
                'ResourceGeneratorAgent 覆盖 6 类学习资源',
                '已接入讯飞智文 PPT 与数字人视频任务接口',
                '资源生成后自动渲染移动端知识卡片'
            ],
            'next_steps': ['继续完善视频渲染成功率与资源质量评分']
        },
        {
            'name': '智能辅导与学习评估',
            'score': 88,
            'level': '闭环形成',
            'icon': 'fa-comments',
            'requirements': ['多轮问答', '流式输出', '追问纠错', '多维评估', '学习报告', '路径动态调整'],
            'evidence': [
                'TutorAgent 支持个性化问答和解释',
                'EvaluatorAgent 输出 8 维学习评估指标',
                '学习报告、雷达图、预警分析与学习路径形成闭环',
                '能力测试中心新增高校专业分类、民航特色题组、逐题解析与难度分析'
            ],
            'next_steps': ['增加定时自动评估、教师提醒工作流与测评结果持久化']
        },
        {
            'name': '部署测试与工程化',
            'score': 82,
            'level': '可交付',
            'icon': 'fa-server',
            'requirements': ['Windows 一键启动', 'Docker 部署', '生产 WSGI', '测试用例', '文档索引', '演示入口'],
            'evidence': [
                '提供 start.bat、Dockerfile、docker-compose.yml、wsgi.py',
                'README 与多智能体页面突出赛题亮点',
                'start.bat 调整为更稳的英文启动提示，降低 Windows 双击演示乱码风险',
                '新增赛题契合度中心用于答辩演示'
            ],
            'next_steps': ['安装 pytest 后补齐自动化测试报告与覆盖率截图']
        },
        {
            'name': '配套文档与答辩材料',
            'score': 80,
            'level': '持续完善',
            'icon': 'fa-file-lines',
            'requirements': ['开发说明书', '测试说明书', '开源组件声明', 'PPT 大纲', '演示视频脚本', '完成计划清单'],
            'evidence': [
                '已补充 A3 配套文档清单与完成计划',
                '已新增系统开发说明书、测试说明书与开源组件说明文档草稿',
                '可与赛题对照页、README、演示视频进一步联动'
            ],
            'next_steps': ['继续补齐最终版 PPT、演示视频脚本与更细的测试截图证据']
        }
    ]
    total_score = round(sum(item['score'] for item in modules) / len(modules), 1)
    strengths = [
        '多智能体协同覆盖画像、知识库、资源、规划、辅导、评估完整链路',
        'RAG 问答带来源引用，直接回应赛题反幻觉与知识库要求',
        '学习路径具备时间线、甘特图、日历三种演示视图',
        '画像动态演进与移动端知识卡片增强个性化体验',
        '能力测试中心已支持高校专业分类与民航特色题组，可直接回流学习画像与资源推送',
        '已开始沉淀配套文档与答辩材料，方便初赛提交时统一收口',
        '教师端已有群像聚类、雷达图、预警分析，支撑教育大数据价值'
    ]
    return {
        'title': 'A3 赛题契合度中心',
        'subtitle': '大模智学：基于大模型的个性化资源生成与学习多智能体系统',
        'total_score': total_score,
        'modules': modules,
        'strengths': strengths,
        'summary': {
            'agent_count': '7 类',
            'profile_dimensions': '10 维',
            'resource_types': '8 类',
            'rag_pipeline': '上传-解析-索引-检索-引用',
            'deployment': 'Windows / Docker / WSGI',
            'documentation': '清单 / 开发 / 测试 / 开源'
        }
    }

@main_bp.route('/')
def index():
    """首页 - 优化版"""
    return render_template('index.html')

@main_bp.route('/home')
def home():
    """首页 - 优化版"""
    return render_template('index.html')


@main_bp.route('/competition-readiness')
def competition_readiness():
    """赛题契合度与完成度展示页"""
    return render_template('competition_readiness.html', readiness=_competition_readiness_data())


@main_bp.route('/api/competition-readiness')
def api_competition_readiness():
    """赛题契合度 JSON 数据"""
    return jsonify(_competition_readiness_data())

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """用户仪表盘 - 根据角色跳转"""
    if current_user.is_teacher():
        return render_template('teacher_dashboard.html', dashboard=_teacher_dashboard_data())
    else:
        return render_template('student_dashboard.html')
