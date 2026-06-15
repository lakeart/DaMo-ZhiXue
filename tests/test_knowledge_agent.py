import zipfile

from app.multi_agent.knowledge_agent import KnowledgeBaseAgent


class DummyLLM:
    def __init__(self, response):
        self.response = response

    def chat(self, messages, **kwargs):
        return self.response


def test_extract_pptx_text(monkeypatch, tmp_path):
    monkeypatch.setattr(
        'app.multi_agent.knowledge_agent.get_llm_client',
        lambda: DummyLLM('')
    )
    monkeypatch.setenv('KNOWLEDGE_RETRIEVAL_BACKEND', 'tfidf')

    pptx_path = tmp_path / 'sample_slides.pptx'
    slide_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<p:cSld><p:spTree><p:sp><p:txBody>'
        '<a:p><a:r><a:t>课程封面</a:t></a:r></a:p>'
        '<a:p><a:r><a:t>知识库问答</a:t></a:r></a:p>'
        '</p:txBody></p:sp></p:spTree></p:cSld></p:sld>'
    )
    with zipfile.ZipFile(pptx_path, 'w') as zf:
        zf.writestr('ppt/slides/slide1.xml', slide_xml)

    agent = KnowledgeBaseAgent()
    text = agent.extract_text(str(pptx_path), pptx_path.name)

    assert '课程封面' in text
    assert '知识库问答' in text


def test_generate_rag_answer_falls_back_when_llm_is_mock(monkeypatch):
    monkeypatch.setattr(
        'app.multi_agent.knowledge_agent.get_llm_client',
        lambda: DummyLLM('感谢您的提问！关于“测试问题”我来为您详细解答。')
    )
    monkeypatch.setenv('KNOWLEDGE_RETRIEVAL_BACKEND', 'tfidf')

    agent = KnowledgeBaseAgent()
    contexts = [
        {
            'document_title': '核心知识讲义',
            'filename': '02_核心知识讲义.md',
            'content': 'Cache 是位于 CPU 与主存之间的高速小容量存储器，用于降低平均访存时间。'
        },
        {
            'document_title': '章节题库',
            'filename': '04_章节题库.csv',
            'content': 'Cache 的主要作用是利用局部性原理提升系统性能。'
        }
    ]

    answer = agent._generate_rag_answer('Cache 的主要作用是什么？', contexts)

    assert '基于已上传知识库' in answer
    assert '[来源1]' in answer
    assert '[来源2]' in answer


def test_retrieval_backend_respects_tfidf_preference(monkeypatch):
    monkeypatch.setattr(
        'app.multi_agent.knowledge_agent.get_llm_client',
        lambda: DummyLLM('')
    )
    monkeypatch.setenv('KNOWLEDGE_RETRIEVAL_BACKEND', 'tfidf')

    agent = KnowledgeBaseAgent()

    assert agent.retrieval_backend == 'tfidf'
    assert agent._get_retrieval_engine_label() == 'TF-IDF semantic retrieval'
    assert '.pptx' in agent.SUPPORTED_EXTENSIONS
    assert '.ppt' in agent.SUPPORTED_EXTENSIONS
