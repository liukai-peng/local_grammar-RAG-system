"""
RAG查询系统 - 检索增强生成
"""

import os
from typing import List, Dict, Any
from pure_vector_store import get_vector_store
from openai import OpenAI


class RAGQuerySystem:
    def __init__(
        self,
        collection_name: str = "local_grammar_papers",
        persist_directory: str = "./chroma_db",
        embedding_model: str = "BAAI/bge-large-zh-v1.5",
        local_model_path: str = None,
        api_key: str = None,
        llm_model: str = "deepseek-chat"
    ):
        """
        初始化RAG查询系统
        
        Args:
            collection_name: 集合名称（保留参数兼容）
            persist_directory: 持久化目录（保留参数兼容）
            embedding_model: 嵌入模型名称（如果local_model_path为None）
            local_model_path: 本地模型路径（优先使用）
            api_key: API密钥（如果使用在线LLM）
            llm_model: LLM模型名称
        """
        # 初始化纯Python向量检索，完全不需要Chroma！
        self.vector_store = get_vector_store()
        
        # 初始化LLM客户端
        self.api_key = api_key
        self.llm_model = llm_model
        
        if api_key:
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
        else:
            self.client = None
            print("警告: 未提供API密钥，将仅进行检索，不生成答案")
    
    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        where: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        检索相关文档
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            where: 元数据过滤条件
            
        Returns:
            检索结果列表
        """
        results = self.vector_store.search(query, n_results=n_results, where=where)
        return results
    
    def generate_answer(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]],
        temperature: float = 0.3
    ) -> str:
        """
        基于检索结果生成答案
        
        Args:
            query: 用户查询
            retrieved_docs: 检索到的文档
            temperature: 生成温度
            
        Returns:
            生成的答案
        """
        if not self.client:
            return "错误: 未配置LLM客户端，无法生成答案"
        
        # 构建上下文
        context = self._build_context(retrieved_docs)
        
        # 构建提示词
        prompt = self._build_prompt(query, context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的局部语法研究助手。请基于提供的文献内容回答用户问题，确保答案准确、完整、有依据。如果文献中没有相关信息，请明确说明。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"生成答案时出错: {str(e)}"
    
    def _build_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """
        构建上下文文本
        
        Args:
            retrieved_docs: 检索到的文档
            
        Returns:
            上下文文本
        """
        context_parts = []
        
        for idx, doc in enumerate(retrieved_docs, 1):
            text = doc.get('text', '')
            metadata = doc.get('metadata', {})
            
            source = metadata.get('source', 'unknown')
            page = metadata.get('page', 0)
            doc_type = metadata.get('type', 'text')
            
            context_part = f"\n[来源 {idx}]\n"
            context_part += f"文件: {source}\n"
            context_part += f"页码: {page}\n"
            context_part += f"类型: {doc_type}\n"
            context_part += f"内容: {text}\n"
            
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, query: str, context: str) -> str:
        """
        构建提示词
        
        Args:
            query: 用户查询
            context: 上下文文本
            
        Returns:
            提示词
        """
        prompt = f"""请基于以下文献内容回答问题：

问题: {query}

文献内容:
{context}

请根据上述文献内容回答问题，要求：
1. 答案要准确、完整
2. 引用相关文献内容作为依据
3. 如果文献中没有相关信息，请明确说明
4. 答案要清晰、有条理

答案:"""

        return prompt
    
    def query(
        self,
        query: str,
        n_results: int = 5,
        generate_answer: bool = True,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        执行完整的RAG查询
        
        Args:
            query: 用户查询
            n_results: 检索结果数量
            generate_answer: 是否生成答案
            temperature: 生成温度
            
        Returns:
            查询结果
        """
        # 检索
        retrieved_docs = self.retrieve(query, n_results=n_results)
        
        result = {
            "query": query,
            "retrieved_docs": retrieved_docs,
            "answer": None
        }
        
        # 生成答案
        if generate_answer:
            answer = self.generate_answer(query, retrieved_docs, temperature)
            result["answer"] = answer
        
        return result
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """
        格式化查询结果
        
        Args:
            result: 查询结果
            
        Returns:
            格式化的文本
        """
        output = []
        
        output.append("=" * 60)
        output.append("RAG查询结果")
        output.append("=" * 60)
        
        output.append(f"\n问题: {result['query']}")
        
        if result['answer']:
            output.append(f"\n答案:")
            output.append(result['answer'])
        
        output.append(f"\n\n检索到的相关文献 (共{len(result['retrieved_docs'])}条):")
        
        for idx, doc in enumerate(result['retrieved_docs'], 1):
            metadata = doc.get('metadata', {})
            text = doc.get('text', '')
            
            output.append(f"\n[{idx}] {metadata.get('source', 'unknown')} - 第{metadata.get('page', 0)}页")
            output.append(f"类型: {metadata.get('type', 'text')}")
            output.append(f"相似度: {1 - doc.get('distance', 0):.4f}")
            output.append(f"内容: {text[:200]}...")
        
        output.append("\n" + "=" * 60)
        
        return "\n".join(output)


if __name__ == "__main__":
    # 测试RAG查询系统
    # 注意: 需要先构建向量数据库
    
    # 如果有本地模型，指定路径
    local_model_path = "./bge-large-zh-v1.5"  # 修改为你的本地模型路径
    
    # 初始化系统
    rag_system = RAGQuerySystem(
        local_model_path=local_model_path,
        api_key="sk-7c679cc5cc024856a4ffd2311a2b556c"  # 替换为你的API密钥
    )
    
    # 测试查询
    query = "什么是局部语法？"
    result = rag_system.query(query, n_results=5, generate_answer=True)
    
    # 打印结果
    print(rag_system.format_result(result))
