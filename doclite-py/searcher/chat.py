import logging
from typing import List, Dict, Optional
from .retriever import DocumentRetriever

logger = logging.getLogger(__name__)

class DocumentChat:
    """文档对话管理器"""
    
    def __init__(self, retriever: DocumentRetriever):
        """
        初始化对话管理器
        
        Args:
            retriever: 文档检索器
        """
        self.retriever = retriever
        self.conversation_history = []
    
    def _build_context_from_history(self, max_history: int = 3) -> str:
        """
        从对话历史构建上下文
        
        Args:
            max_history: 最多使用的历史对话数量
        
        Returns:
            上下文字符串
        """
        if not self.conversation_history:
            return ""
        
        # 获取最近的历史对话
        recent_history = self.conversation_history[-max_history:]
        
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
            
            # 构建答案
            answer_parts = []
            sources = []
            
            for i, result in enumerate(results):
                text = result.get('text', '')
                if text:
                    answer_parts.append(f"[{i+1}] {text}")
                    sources.append({
                        'filename': result.get('filename', ''),
                        'path': result.get('path', ''),
                        'file_type': result.get('file_type', ''),
                        'similarity': result.get('similarity', 0),
                        'excerpt': text[:200] + '...' if len(text) > 200 else text
                    })
            
            # 组合答案
            answer = "根据文档内容，找到以下相关信息：\n\n" + "\n\n".join(answer_parts)
            
            # 计算平均相似度作为置信度
            avg_similarity = sum(r.get('similarity', 0) for r in results) / len(results)
            
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
