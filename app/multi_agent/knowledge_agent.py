# -*- coding: utf-8 -*-
"""
知识库管理智能体
提供文档解析、分块索引、语义检索和带引用的 RAG 问答能力。
"""

import hashlib
import json
import os
import re
import uuid
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple

from app import db
from app.models.agent_models import KnowledgeChunkModel, KnowledgeDocumentModel
from app.multi_agent import HallucinationDetector
from app.multi_agent.llm_client import get_llm_client


class KnowledgeBaseAgent:
    """轻量级知识库 Agent。

    现阶段使用 TF-IDF 向量空间完成可演示的语义检索闭环，后续可平滑替换为
    ChromaDB/Milvus 等向量库。
    """

    SUPPORTED_EXTENSIONS = {'.txt', '.md', '.csv', '.json', '.docx', '.pdf', '.pptx', '.ppt'}

    def __init__(self):
        self.llm = get_llm_client()
        self.retrieval_backend_preference = (os.environ.get('KNOWLEDGE_RETRIEVAL_BACKEND', 'auto') or 'auto').lower()
        self.chroma_db_path = os.environ.get(
            'CHROMA_DB_PATH',
            os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                os.pardir,
                os.pardir,
                'instance',
                'chroma',
                'knowledge'
            ))
        )
        self.chroma_client = None
        self.chroma_available = False
        self.retrieval_backend = 'tfidf'
        self._init_retrieval_backend()

    def index_file(self, user_id: int, file_path: str, original_filename: str, title: str = "") -> Dict:
        text = self.extract_text(file_path, original_filename)
        if len(text.strip()) < 20:
            raise ValueError("文档内容过少，无法建立知识库索引")

        content_hash = self._hash_text(text)
        existing = KnowledgeDocumentModel.query.filter_by(
            user_id=user_id,
            content_hash=content_hash
        ).first()
        if existing:
            return {
                'document': existing.to_dict(),
                'chunks': existing.chunk_count,
                'deduplicated': True
            }

        document_id = str(uuid.uuid4())
        ext = os.path.splitext(original_filename)[1].lower().lstrip('.')
        chunks = self._chunk_text(text)

        document = KnowledgeDocumentModel(
            document_id=document_id,
            user_id=user_id,
            title=title or os.path.splitext(original_filename)[0],
            original_filename=original_filename,
            stored_filename=os.path.basename(file_path),
            file_type=ext,
            file_size=os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            content_hash=content_hash,
            status='indexed',
            chunk_count=len(chunks),
            summary=self._summarize(text)
        )
        db.session.add(document)

        chunk_rows = []
        for index, chunk in enumerate(chunks):
            keywords = self._extract_keywords(chunk)
            chunk_row = KnowledgeChunkModel(
                document_id=document_id,
                user_id=user_id,
                chunk_index=index,
                content=chunk,
                keywords=json.dumps(keywords, ensure_ascii=False),
                vector_meta=json.dumps({
                    'method': 'tfidf',
                    'chunk_hash': self._hash_text(chunk),
                    'token_count_estimate': max(1, len(chunk) // 2)
                }, ensure_ascii=False),
                char_count=len(chunk)
            )
            db.session.add(chunk_row)
            chunk_rows.append(chunk_row)

        db.session.commit()
        self._sync_document_to_vector_store(user_id, document, chunk_rows)
        return {
            'document': document.to_dict(),
            'chunks': len(chunks),
            'deduplicated': False
        }

    def extract_text(self, file_path: str, filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError("暂不支持该文件类型，请上传 TXT/Markdown/CSV/JSON/DOCX/PDF/PPT/PPTX")

        if ext == '.docx':
            return self._extract_docx_text(file_path)
        if ext == '.pdf':
            return self._extract_pdf_text(file_path)
        if ext == '.pptx':
            return self._extract_pptx_text(file_path)
        if ext == '.ppt':
            return self._extract_ppt_text(file_path)

        with open(file_path, 'rb') as f:
            raw = f.read()
        for encoding in ('utf-8-sig', 'utf-8', 'gbk', 'gb18030'):
            try:
                return raw.decode(encoding)
            except UnicodeDecodeError:
                continue
        return raw.decode('utf-8', errors='ignore')

    def search(self, user_id: int, query: str, top_k: int = 5) -> Dict:
        query = (query or '').strip()
        if not query:
            return {'results': [], 'count': 0}
        try:
            top_k = max(1, min(10, int(top_k)))
        except Exception:
            top_k = 5

        chunks = KnowledgeChunkModel.query.filter_by(user_id=user_id).all()
        if not chunks:
            return {'results': [], 'count': 0}

        if self.retrieval_backend == 'chroma':
            chroma_result = self._search_with_chroma(user_id, query, top_k)
            if chroma_result is not None:
                return chroma_result

        scores = self._rank_chunks(query, chunks)
        document_ids = {chunk.document_id for chunk, _ in scores}
        docs = KnowledgeDocumentModel.query.filter(
            KnowledgeDocumentModel.document_id.in_(document_ids)
        ).all() if document_ids else []
        doc_map = {doc.document_id: doc for doc in docs}

        results = []
        for chunk, score in scores[:top_k]:
            doc = doc_map.get(chunk.document_id)
            results.append({
                'chunk_id': chunk.id,
                'document_id': chunk.document_id,
                'document_title': doc.title if doc else '未知文档',
                'filename': doc.original_filename if doc else '',
                'chunk_index': chunk.chunk_index,
                'score': round(float(score), 4),
                'content': chunk.content,
                'preview': self._highlight_preview(chunk.content, query)
            })

        return {'results': results, 'count': len(results)}

    def answer(self, user_id: int, question: str, top_k: int = 4) -> Dict:
        search_result = self.search(user_id, question, top_k=top_k)
        contexts = search_result.get('results', [])
        if not contexts:
            return {
                'answer': '知识库中暂未检索到足够相关的材料。建议先上传课程讲义、课件或题库文档，再进行基于资料的问答。',
                'citations': [],
                'confidence': 0.0,
                'warnings': ['未命中知识库材料，回答已被拦截以降低幻觉风险。'],
                'retrieval': search_result
            }

        combined = self._generate_rag_answer(question, contexts)
        _, warnings = HallucinationDetector.check_factuality(combined, question)
        max_score = max((ctx['score'] for ctx in contexts), default=0)

        return {
            'answer': combined,
            'citations': [
                {
                    'ref': f"来源{i}",
                    'document_title': ctx['document_title'],
                    'filename': ctx['filename'],
                    'chunk_index': ctx['chunk_index'],
                    'score': ctx['score'],
                    'content': ctx['content'][:360]
                }
                for i, ctx in enumerate(contexts, 1)
            ],
            'confidence': round(min(0.96, max_score + 0.18), 2),
            'warnings': warnings,
            'retrieval': search_result
        }

    def status(self, user_id: int) -> Dict:
        documents = KnowledgeDocumentModel.query.filter_by(user_id=user_id).order_by(
            KnowledgeDocumentModel.created_at.desc()
        ).all()
        chunk_count = KnowledgeChunkModel.query.filter_by(user_id=user_id).count()
        return {
            'documents': [doc.to_dict() for doc in documents],
            'document_count': len(documents),
            'chunk_count': chunk_count,
            'retrieval_engine': self._get_retrieval_engine_label(),
            'retrieval_backend': self.retrieval_backend,
            'backend_preference': self.retrieval_backend_preference,
            'chroma_available': self.chroma_available,
            'supported_extensions': sorted(self.SUPPORTED_EXTENSIONS)
        }

    def _rank_chunks(self, query: str, chunks: List[KnowledgeChunkModel]) -> List[Tuple[KnowledgeChunkModel, float]]:
        corpus = [chunk.content for chunk in chunks]
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4), max_features=6000)
            matrix = vectorizer.fit_transform(corpus + [query])
            similarities = cosine_similarity(matrix[-1], matrix[:-1]).flatten()
            scored = list(zip(chunks, similarities))
        except Exception:
            query_terms = set(self._tokenize(query))
            scored = []
            for chunk in chunks:
                terms = set(self._tokenize(chunk.content))
                overlap = len(query_terms & terms)
                scored.append((chunk, overlap / max(1, len(query_terms))))

        scored.sort(key=lambda item: item[1], reverse=True)
        return [(chunk, score) for chunk, score in scored if score > 0]

    def _extract_docx_text(self, file_path: str) -> str:
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        with zipfile.ZipFile(file_path) as z:
            xml = z.read('word/document.xml')
        root = ET.fromstring(xml)
        paragraphs = []
        for p in root.findall('.//w:p', ns):
            text = ''.join((t.text or '') for t in p.findall('.//w:t', ns)).strip()
            if text:
                paragraphs.append(text)
        return '\n'.join(paragraphs)

    def _extract_pdf_text(self, file_path: str) -> str:
        try:
            try:
                from pypdf import PdfReader
            except Exception:
                from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            return '\n'.join(page.extract_text() or '' for page in reader.pages)
        except Exception as exc:
            raise ValueError(f"PDF 解析依赖不可用或文件无法解析：{exc}")

    def _init_retrieval_backend(self) -> None:
        preferred = self.retrieval_backend_preference
        if preferred not in {'auto', 'tfidf', 'chroma'}:
            preferred = 'auto'
            self.retrieval_backend_preference = 'auto'

        if preferred == 'tfidf':
            self.retrieval_backend = 'tfidf'
            return

        try:
            import chromadb
            from chromadb.config import Settings

            os.makedirs(self.chroma_db_path, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(
                path=self.chroma_db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            self.chroma_available = True
            self.retrieval_backend = 'chroma'
        except Exception:
            self.chroma_client = None
            self.chroma_available = False
            self.retrieval_backend = 'tfidf'

    def _sync_document_to_vector_store(
        self,
        user_id: int,
        document: KnowledgeDocumentModel,
        chunk_rows: List[KnowledgeChunkModel]
    ) -> None:
        if self.retrieval_backend != 'chroma' or not self.chroma_client or not chunk_rows:
            return

        try:
            collection = self._get_chroma_collection(user_id)
            ids = [self._build_chunk_vector_id(chunk.id, chunk.document_id, chunk.chunk_index) for chunk in chunk_rows]
            documents = [chunk.content for chunk in chunk_rows]
            metadatas = [
                {
                    'chunk_id': int(chunk.id),
                    'document_id': chunk.document_id,
                    'chunk_index': int(chunk.chunk_index),
                    'user_id': int(user_id),
                    'document_title': document.title,
                    'filename': document.original_filename,
                }
                for chunk in chunk_rows
            ]
            collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        except Exception:
            self.retrieval_backend = 'tfidf'

    def _search_with_chroma(self, user_id: int, query: str, top_k: int) -> Optional[Dict]:
        if not self.chroma_client:
            return None

        try:
            collection = self._get_chroma_collection(user_id)
            if collection.count() == 0:
                return {'results': [], 'count': 0}

            raw = collection.query(query_texts=[query], n_results=top_k)
            documents = (raw.get('documents') or [[]])[0]
            metadatas = (raw.get('metadatas') or [[]])[0]
            distances = (raw.get('distances') or [[]])[0]

            results = []
            for content, meta, distance in zip(documents, metadatas, distances):
                content = content or ''
                meta = meta or {}
                similarity = round(1 / (1 + max(float(distance), 0.0)), 4)
                results.append({
                    'chunk_id': meta.get('chunk_id'),
                    'document_id': meta.get('document_id'),
                    'document_title': meta.get('document_title', '未知文档'),
                    'filename': meta.get('filename', ''),
                    'chunk_index': meta.get('chunk_index', 0),
                    'score': similarity,
                    'content': content,
                    'preview': self._highlight_preview(content, query)
                })
            return {'results': results, 'count': len(results)}
        except Exception:
            self.retrieval_backend = 'tfidf'
            return None

    def _get_chroma_collection(self, user_id: int):
        return self.chroma_client.get_or_create_collection(
            name=self._build_collection_name(user_id),
            metadata={'user_id': int(user_id), 'domain': 'knowledge_base'}
        )

    def _build_collection_name(self, user_id: int) -> str:
        return f"knowledge_user_{int(user_id)}"

    def _build_chunk_vector_id(self, chunk_id: int, document_id: str, chunk_index: int) -> str:
        return f"{document_id}:{chunk_index}:{chunk_id}"

    def _extract_pptx_text(self, file_path: str) -> str:
        text_runs = []
        a_ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
        with zipfile.ZipFile(file_path) as z:
            slide_names = sorted(
                [name for name in z.namelist() if name.startswith('ppt/slides/slide') and name.endswith('.xml')]
            )
            for slide_name in slide_names:
                root = ET.fromstring(z.read(slide_name))
                slide_lines = [
                    (node.text or '').strip()
                    for node in root.findall('.//a:t', a_ns)
                    if (node.text or '').strip()
                ]
                if slide_lines:
                    text_runs.append('\n'.join(slide_lines))
        return '\n\n'.join(text_runs)

    def _extract_ppt_text(self, file_path: str) -> str:
        with open(file_path, 'rb') as f:
            raw = f.read()

        unicode_fragments = re.findall(
            rb'(?:[\x20-\x7e\x80-\xff]\x00){4,}',
            raw
        )
        ascii_fragments = re.findall(
            rb'[\x20-\x7e]{6,}',
            raw
        )

        texts = []
        seen = set()

        for fragment in unicode_fragments:
            try:
                candidate = fragment.decode('utf-16le', errors='ignore').strip()
            except Exception:
                continue
            candidate = self._normalize_binary_text(candidate)
            if len(candidate) >= 4 and candidate not in seen:
                seen.add(candidate)
                texts.append(candidate)

        for fragment in ascii_fragments:
            try:
                candidate = fragment.decode('latin1', errors='ignore').strip()
            except Exception:
                continue
            candidate = self._normalize_binary_text(candidate)
            if len(candidate) >= 6 and candidate not in seen:
                seen.add(candidate)
                texts.append(candidate)

        return '\n'.join(texts)

    def _chunk_text(self, text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
        cleaned = re.sub(r'\n{3,}', '\n\n', text).strip()
        if len(cleaned) <= chunk_size:
            return [cleaned]

        chunks = []
        start = 0
        while start < len(cleaned):
            end = min(len(cleaned), start + chunk_size)
            window = cleaned[start:end]
            cut = max(window.rfind('\n'), window.rfind('。'), window.rfind('；'), window.rfind('.'))
            if cut > chunk_size * 0.45:
                end = start + cut + 1
            chunk = cleaned[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= len(cleaned):
                break
            start = max(0, end - overlap)
        return chunks

    def _summarize(self, text: str) -> str:
        normalized = re.sub(r'\s+', ' ', text).strip()
        return normalized[:220] + ('...' if len(normalized) > 220 else '')

    def _extract_keywords(self, text: str, limit: int = 12) -> List[str]:
        tokens = self._tokenize(text)
        freq = {}
        for token in tokens:
            if len(token) < 2:
                continue
            freq[token] = freq.get(token, 0) + 1
        return [item[0] for item in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:limit]]

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'[\u4e00-\u9fa5]{2,}|[A-Za-z][A-Za-z0-9_+-]{1,}', text.lower())

    def _highlight_preview(self, text: str, query: str) -> str:
        sentence = self._best_sentence(text, query)
        return sentence[:240] + ('...' if len(sentence) > 240 else '')

    def _best_sentence(self, text: str, query: str) -> str:
        sentences = [s.strip() for s in re.split(r'(?<=[。！？!?；;.\n])', text) if s.strip()]
        if not sentences:
            return text[:260]
        terms = set(self._tokenize(query))
        best = max(sentences, key=lambda s: len(terms & set(self._tokenize(s))))
        return best[:320] + ('...' if len(best) > 320 else '')

    def _hash_text(self, text: str) -> str:
        return hashlib.sha256(text.encode('utf-8', errors='ignore')).hexdigest()

    def _get_retrieval_engine_label(self) -> str:
        if self.retrieval_backend == 'chroma':
            return 'ChromaDB vector retrieval'
        return 'TF-IDF semantic retrieval'

    def _generate_rag_answer(self, question: str, contexts: List[Dict]) -> str:
        prompt_blocks = []
        for i, ctx in enumerate(contexts, 1):
            prompt_blocks.append(
                f"[来源{i}] 文档：{ctx['document_title']}（{ctx['filename']}）\n"
                f"片段：{ctx['content'][:900]}"
            )

        messages = [
            {
                'role': 'system',
                'content': (
                    "你是高校课程知识库问答助手。"
                    "你的任务是仅根据提供的材料回答问题，禁止编造材料中没有的信息。"
                    "如果材料不足，请明确说资料不足，并建议用户补充讲义、课件或题库。"
                    "回答要自然、适合学生阅读，尽量先直接回答，再补充理解建议。"
                    "引用时使用 [来源1] 这种格式。"
                )
            },
            {
                'role': 'user',
                'content': (
                    f"问题：{question}\n\n"
                    f"可用材料：\n{chr(10).join(prompt_blocks)}\n\n"
                    "请输出一段中文回答，要求："
                    "1. 先给出直接答案；"
                    "2. 关键结论后带来源标记；"
                    "3. 若多份材料互相补充，可合并说明；"
                    "4. 最后补一句学习建议。"
                )
            }
        ]

        try:
            answer = (self.llm.chat(messages, temperature=0.2, max_tokens=900) or '').strip()
        except Exception:
            answer = ''

        if self._looks_like_mock_answer(answer):
            answer = ''

        if answer:
            if '参考来源：' not in answer:
                answer = answer.rstrip() + "\n\n参考来源：\n" + "\n".join(
                    f"- [来源{i}] {ctx['document_title']}（{ctx['filename']}）"
                    for i, ctx in enumerate(contexts, 1)
                )
            return answer

        answer_lines = [
            f"基于已上传知识库，我检索到 {len(contexts)} 条相关材料：",
            ""
        ]
        for i, ctx in enumerate(contexts, 1):
            sentence = self._best_sentence(ctx['content'], question)
            answer_lines.append(f"{i}. {sentence} [来源{i}]")

        answer_lines.extend([
            "",
            "建议学习路径：先阅读最高相关来源，提炼概念定义，再用练习题验证掌握度；若多个来源表述不一致，以课程讲义或教师上传材料优先。"
        ])
        return "\n".join(answer_lines)

    def _normalize_binary_text(self, text: str) -> str:
        text = text.replace('\x00', ' ')
        text = re.sub(r'[\x01-\x08\x0b-\x1f]+', ' ', text)
        text = re.sub(r'\s{2,}', ' ', text)
        return text.strip()

    def _looks_like_mock_answer(self, text: str) -> bool:
        if not text:
            return True
        mock_markers = [
            '感谢您的提问！关于',
            '这是基于您的学习情况生成的个性化回答',
            '如果您需要更具体的帮助',
            '当前为演示模式'
        ]
        return any(marker in text for marker in mock_markers)
