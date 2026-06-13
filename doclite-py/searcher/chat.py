import logging
import json
import os
from typing import List, Dict, Optional
from collections import deque
import requests
from .retriever import DocumentRetriever

logger = logging.getLogger(__name__)

class DocumentChat:
    """文档对话管理器"""
    
    def __init__(self, retriever: DocumentRetriever, max_history: int = 10):
        """
        初始化对话管理器
        
        Args:
            retriever: 文档检索器
            max_history: 最大历史对话数量
        """
        self.retriever = retriever
        self.max_history = max_history
        self.conversation_history: deque = deque(maxlen=max_history)
    
    def _load_settings(self) -> Dict:
        """加载应用设置"""
        from api.settings import SETTINGS_FILE
        if not os.path.exists(SETTINGS_FILE):
            return {}
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载设置失败: {e}")
            return {}
    
    def _build_prompt(self, document_content: str, question: str) -> str:
        """构建 prompt"""
        return f"""基于以下文档内容回答用户问题。

文档内容：
{document_content}

用户问题：{question}

请根据文档内容给出准确的回答。如果文档中没有相关信息，请说明。"""

    def _call_ollama(self, prompt: str, settings: Dict) -> Optional[str]:
        """调用 Ollama API"""
        api_url = settings.get('api_base_url', 'http://localhost:11434')
        model = settings.get('api_model', 'qwen2:1.5b')

        try:
            response = requests.post(
                f"{api_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            if response.status_code == 200:
                return response.json().get("response")
            else:
                logger.error(f"Ollama API 调用失败: {response.status_code} {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"连接 Ollama 服务失败: {e}")
            return None

    def _call_openai_compatible(self, prompt: str, settings: Dict) -> Optional[str]:
        """调用 OpenAI 兼容 API（OpenAI / 自定义 API）"""
        api_url = settings.get('api_base_url', '').rstrip('/')
        model = settings.get('api_model', 'gpt-3.5-turbo')
        api_key = settings.get('api_key', '')

        if not api_url:
            logger.error("未配置 API 地址")
            return None

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            response = requests.post(
                f"{api_url}/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                },
                timeout=60
            )
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                logger.error(f"API 调用失败: {response.status_code} {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"连接 API 服务失败: {e}")
            return None
    
    def _build_context_from_history(self, max_context: int = 3) -> str:
        """
        从对话历史构建上下文
        
        Args:
            max_context: 最多使用的历史对话数量
        
        Returns:
            上下文字符串
        """
        if not self.conversation_history:
            return ""
        
        # 获取最近的历史对话
        recent_history = list(self.conversation_history)[-max_context:]
        
        context_parts = []
        for item in recent_history:
            context_parts.append(f"用户问: {item['question']}")
            # 只取回答的前200个字符作为上下文
            answer_preview = item['answer'][:200] + '...' if len(item['answer']) > 200 else item['answer']
            context_parts.append(f"回答: {answer_preview}")
        
        return "\n".join(context_parts)
    
    def answer_question(self, question: str, top_k: int = 5, use_context: bool = True) -> Dict:
        """
        根据文档回答问题
        
        Args:
            question: 用户问题
            top_k: 检索的文档块数量
            use_context: 是否使用上下文
        
        Returns:
            包含答案和引用的结果
        """
        try:
            # 构建包含历史的查询
            search_query = question
            
            # 如果使用上下文且有历史对话，将历史加入查询
            if use_context and self.conversation_history:
                history_context = self._build_context_from_history()
                search_query = f"{history_context}\n\n当前问题: {question}"
            
            # 检索相关文档
            if use_context:
                results = self.retriever.retrieve_with_context(search_query, top_k)
            else:
                results = self.retriever.retrieve(question, top_k)
            
            if not results:
                return {
                    'answer': '抱歉，没有找到与您问题相关的文档内容。',
                    'sources': [],
                    'confidence': 0.0
                }
            
            # 构建文档内容
            document_parts = []
            sources = []
            
            for i, result in enumerate(results):
                text = result.get('text', '')
                if text:
                    document_parts.append(f"[文档片段 {i+1}]\n{text}")
                    sources.append({
                        'filename': result.get('filename', ''),
                        'path': result.get('path', ''),
                        'file_type': result.get('file_type', ''),
                        'similarity': result.get('similarity', 0),
                        'excerpt': text[:200] + '...' if len(text) > 200 else text
                    })
            
            document_content = "\n\n".join(document_parts)
            
            # 计算平均相似度作为置信度
            avg_similarity = sum(r.get('similarity', 0) for r in results) / len(results)
            
            # 调用 LLM 生成回答
            settings = self._load_settings()
            provider = settings.get('api_provider', 'ollama')
            prompt = self._build_prompt(document_content, question)

            llm_answer = None
            if provider == 'ollama':
                llm_answer = self._call_ollama(prompt, settings)
            elif provider in ('openai', 'custom'):
                llm_answer = self._call_openai_compatible(prompt, settings)

            if llm_answer:
                answer = llm_answer
            else:
                answer = "根据文档内容，找到以下相关信息：\n\n" + "\n\n".join(document_parts)
            
            # 记录对话历史
            self.conversation_history.append({
                'question': question,
                'answer': answer,
                'sources': sources
            })
            
            return {
                'answer': answer,
                'sources': sources,
                'confidence': avg_similarity
            }
            
        except Exception as e:
            logger.error(f"回答问题失败: {e}")
            return {
                'answer': f'处理问题时出错: {str(e)}',
                'sources': [],
                'confidence': 0.0
            }
    
    def get_conversation_history(self) -> List[Dict]:
        """获取对话历史"""
        return self.conversation_history
    
    def clear_conversation_history(self):
        """清空对话历史"""
        self.conversation_history = []
