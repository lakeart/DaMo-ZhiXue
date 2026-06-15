import json
import random
from datetime import datetime, timedelta

from app import db
from app.models.quiz import Question, QuizSubmission
from app.models.user import User


TOPICS = [
    '数据结构', '算法设计', '计算机网络', '操作系统', '数据库原理', '软件工程',
    '计算机组成原理', '离散数学', '编译原理', '人工智能', 'Python基础', '机器学习导论'
]

QUESTION_STYLES = ['选择题', '填空题', '判断题', '解答题']
DIFFICULTIES = ['简单', '中等', '困难']
STUDENT_NAMES = [
    '李明', '张悦', '王晨', '刘洋', '陈璐', '周航', '孙瑞', '赵宁',
    '黄琪', '吴楠', '徐帆', '郭倩', '何森', '林凡', '高颖', '罗欣',
    '杨博', '胡静', '马超', '朱琳', '唐悦', '郑航', '曹阳', '谢宁'
]


def ensure_demo_learning_data(min_students=24, min_questions=80, min_submissions=600):
    """在现有数据库基础上幂等补齐演示数据，不重置用户已有数据。"""
    rng = random.Random(20260613)

    students = User.query.filter_by(role='student').order_by(User.id.asc()).all()
    teacher = User.query.filter_by(role='teacher').first() or User.query.filter_by(role='admin').first()
    if teacher is None:
        return {'students': len(students), 'questions': 0, 'submissions': 0, 'created': False}

    created_students = 0
    created_questions = 0
    created_submissions = 0

    existing_usernames = {user.username for user in students}
    while len(students) < min_students:
        seq = len(students) + 1
        username = f"2026{seq:04d}"
        while username in existing_usernames:
            seq += 1
            username = f"2026{seq:04d}"
        existing_usernames.add(username)
        user = User(
            username=username,
            email=f"{username}@student.demo",
            password=username,
            role='student'
        )
        db.session.add(user)
        students.append(user)
        created_students += 1

    if created_students:
        db.session.commit()
        students = User.query.filter_by(role='student').order_by(User.id.asc()).all()

    existing_questions = Question.query.count()
    next_question_no = _next_question_number()
    teacher_id = teacher.id
    while existing_questions + created_questions < min_questions:
        topic = TOPICS[(existing_questions + created_questions) % len(TOPICS)]
        style = QUESTION_STYLES[(existing_questions + created_questions) % len(QUESTION_STYLES)]
        difficulty = DIFFICULTIES[(existing_questions + created_questions) % len(DIFFICULTIES)]
        question = _build_question(next_question_no, topic, style, difficulty)
        question.created_by = teacher_id
        db.session.add(question)
        created_questions += 1
        next_question_no += 1

    if created_questions:
        db.session.commit()

    total_submissions = QuizSubmission.query.count()
    if total_submissions < min_submissions:
        questions = Question.query.order_by(Question.id.asc()).all()
        if questions and students:
            for i in range(total_submissions, min_submissions):
                student = students[i % len(students)]
                question = questions[(i * 3) % len(questions)]
                score, error_style = _score_for_question(question, rng)
                start_time = datetime.now() - timedelta(days=rng.randint(1, 90), hours=rng.randint(0, 12), minutes=rng.randint(0, 59))
                time_consumed = rng.randint(45, 420 if question.style in ('解答题', '编程题') else 180)
                submit_time = start_time + timedelta(seconds=time_consumed)
                submission = QuizSubmission(
                    student_id=student.username,
                    student_name=STUDENT_NAMES[i % len(STUDENT_NAMES)],
                    question_id=question.id,
                    source_question_id=question.question_id,
                    question_topic=question.topic,
                    question_style=question.style,
                    error_style=error_style,
                    start_time=start_time,
                    submit_time=submit_time,
                    difficulty=question.difficulty,
                    score=score,
                    time_consumed=time_consumed,
                    memory=rng.randint(128, 1024),
                    time_region=_time_region(start_time)
                )
                db.session.add(submission)
                created_submissions += 1

            db.session.commit()

    return {
        'students': User.query.filter_by(role='student').count(),
        'questions': Question.query.count(),
        'submissions': QuizSubmission.query.count(),
        'created': any([created_students, created_questions, created_submissions]),
        'created_students': created_students,
        'created_questions': created_questions,
        'created_submissions': created_submissions
    }


def _next_question_number():
    max_number = 0
    for row in Question.query.with_entities(Question.question_id).all():
        qid = row[0] or ''
        digits = ''.join(ch for ch in qid if ch.isdigit())
        if digits:
            max_number = max(max_number, int(digits))
    return max_number + 1


def _build_question(number, topic, style, difficulty):
    question_id = f"Q{number:04d}"
    if style == '选择题':
        options = [
            f"{topic} 的核心目标是什么？",
            f"{topic} 的主要优势是什么？",
            f"{topic} 最适合解决哪类问题？",
            f"{topic} 在课程学习中的关键作用是什么？"
        ]
        answer = 'A'
        content = f"{topic} - {difficulty} 选择题：下列关于{topic}的描述，哪一项更准确？"
        return Question(
            question_id=question_id,
            topic=topic,
            style=style,
            content=content,
            options=json.dumps(options, ensure_ascii=False),
            answer=answer,
            difficulty=difficulty
        )
    if style == '判断题':
        content = f"{topic} 判断题：掌握核心概念和典型场景分析，是学好{topic}的重要前提。"
        return Question(
            question_id=question_id,
            topic=topic,
            style=style,
            content=content,
            options=json.dumps(['正确', '错误'], ensure_ascii=False),
            answer='正确',
            difficulty=difficulty
        )
    if style == '填空题':
        content = f"{topic} 填空题：请补全 {topic} 学习中最关键的一个概念或步骤。"
        return Question(
            question_id=question_id,
            topic=topic,
            style=style,
            content=content,
            options='',
            answer=f'{topic}核心概念',
            difficulty=difficulty
        )
    content = f"{topic} 解答题：请结合课程内容，简述 {topic} 的基本原理、典型应用场景与常见易错点。"
    return Question(
        question_id=question_id,
        topic=topic,
        style=style,
        content=content,
        options='',
        answer=f'{topic} 的基本原理、应用场景和易错点分析',
        difficulty=difficulty
    )


def _score_for_question(question, rng):
    full_score = 5
    if question.style == '判断题':
        full_score = 2
    elif question.style == '解答题':
        full_score = 10
    elif question.style == '编程题':
        full_score = 15

    difficulty_bias = {'简单': 0.78, '中等': 0.63, '困难': 0.48}.get(question.difficulty, 0.6)
    roll = rng.random()
    if roll <= difficulty_bias:
        return full_score, '答案正确'
    if question.style in ('解答题', '编程题') and roll <= difficulty_bias + 0.18:
        return max(1, int(full_score * rng.uniform(0.4, 0.8))), '部分正确'
    return 0, rng.choice(['概念错误', '审题错误', '知识点缺失', '理解偏差'])


def _time_region(start_time):
    hour = start_time.hour
    if 6 <= hour < 11:
        return '早上'
    if 11 <= hour < 14:
        return '中午'
    if 14 <= hour < 18:
        return '下午'
    if 18 <= hour < 24:
        return '晚上'
    return '凌晨'
