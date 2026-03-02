"""
完整的RAG流程 - 从PDF到查询
"""

import os
import json
from pdf_parser import PDFParser
from text_chunker import TextChunker
from qa_integrator import QAIntegrator
from vector_store import VectorStore
from rag_query import RAGQuerySystem


class RAGPipeline:
    def __init__(
        self,
        pdf_directory: str = "static",
        qa_file: str = "deepseek_detailed_results.json",
        collection_name: str = "local_grammar_papers",
        persist_directory: str = "./chroma_db",
        embedding_model: str = "BAAI/bge-large-zh-v1.5",
        local_model_path: str = None
    ):
        """
        初始化RAG流程
        
        Args:
            pdf_directory: PDF文件目录
            qa_file: 问答对文件
            collection_name: 集合名称
            persist_directory: 持久化目录
            embedding_model: 嵌入模型名称（如果local_model_path为None）
            local_model_path: 本地模型路径（优先使用）
        """
        self.pdf_directory = pdf_directory
        self.qa_file = qa_file
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        self.local_model_path = local_model_path
        
        # 初始化各个组件
        self.pdf_parser = PDFParser()
        self.text_chunker = TextChunker(
            chunk_size=500,
            chunk_overlap=50
        )
        self.qa_integrator = QAIntegrator()
        self.vector_store = VectorStore(
            collection_name=collection_name,
            persist_directory=persist_directory,
            embedding_model=embedding_model,
            local_model_path=local_model_path
        )
    
    def step1_parse_pdfs(self, output_file: str = "parsed_pdfs.json") -> list:
        """
        步骤1: 解析PDF文件
        
        Args:
            output_file: 输出文件
            
        Returns:
            解析的页面数据
        """
        print("\n" + "=" * 60)
        print("步骤1: 解析PDF文件")
        print("=" * 60)
        
        if not os.path.exists(self.pdf_directory):
            print(f"错误: 目录不存在 {self.pdf_directory}")
            return []
        
        pages = self.pdf_parser.parse_directory(self.pdf_directory, output_file)
        
        print(f"\n✓ 解析完成，共 {len(pages)} 页")
        
        return pages
    
    def step2_chunk_text(self, pages: list, output_file: str = "chunks.json") -> list:
        """
        步骤2: 分块文本
        
        Args:
            pages: 页面数据
            output_file: 输出文件
            
        Returns:
            分块数据
        """
        print("\n" + "=" * 60)
        print("步骤2: 分块文本")
        print("=" * 60)
        
        chunks = self.text_chunker.split_pages(pages)
        
        # 保存分块结果
        self.text_chunker.save_chunks(chunks, output_file)
        
        print(f"\n✓ 分块完成，共 {len(chunks)} 个块")
        
        return chunks
    
    def step3_load_qa_pairs(self) -> list:
        """
        步骤3: 加载问答对
        
        Returns:
            问答对分块数据
        """
        print("\n" + "=" * 60)
        print("步骤3: 加载问答对")
        print("=" * 60)
        
        if not os.path.exists(self.qa_file):
            print(f"警告: 问答对文件不存在 {self.qa_file}")
            return []
        
        qa_chunks = self.qa_integrator.load_and_format(self.qa_file)
        
        print(f"\n✓ 问答对加载完成，共 {len(qa_chunks)} 个")
        
        return qa_chunks
    
    def step4_build_vector_store(self, pdf_chunks: list, qa_chunks: list):
        """
        步骤4: 构建向量数据库
        
        Args:
            pdf_chunks: PDF分块数据
            qa_chunks: 问答对分块数据
        """
        print("\n" + "=" * 60)
        print("步骤4: 构建向量数据库")
        print("=" * 60)
        
        # 合并所有块
        all_chunks = pdf_chunks + qa_chunks
        
        print(f"\n总块数: {len(all_chunks)}")
        print(f"  PDF块: {len(pdf_chunks)}")
        print(f"  问答对块: {len(qa_chunks)}")
        
        # 添加到向量数据库
        self.vector_store.add_chunks(all_chunks)
        
        # 获取集合信息
        info = self.vector_store.get_collection_info()
        print(f"\n✓ 向量数据库构建完成")
        print(f"  集合名称: {info['collection_name']}")
        print(f"  文档数量: {info['count']}")
        print(f"  存储位置: {info['persist_directory']}")
    
    def step5_query(self, query: str, api_key: str = None, n_results: int = 5) -> dict:
        """
        步骤5: 查询
        
        Args:
            query: 查询文本
            api_key: API密钥
            n_results: 返回结果数量
            
        Returns:
            查询结果
        """
        print("\n" + "=" * 60)
        print("步骤5: 查询")
        print("=" * 60)
        
        # 初始化查询系统
        rag_system = RAGQuerySystem(
            collection_name=self.collection_name,
            persist_directory=self.persist_directory,
            embedding_model=self.embedding_model,
            api_key=api_key
        )
        
        # 执行查询
        result = rag_system.query(query, n_results=n_results)
        
        # 格式化结果
        formatted_result = rag_system.format_result(result)
        
        print(formatted_result)
        
        return result
    
    def run_full_pipeline(
        self,
        api_key: str = None,
        test_query: str = "什么是局部语法？"
    ):
        """
        运行完整流程
        
        Args:
            api_key: API密钥
            test_query: 测试查询
        """
        print("\n" + "=" * 60)
        print("RAG完整流程")
        print("=" * 60)
        
        # 步骤1: 解析PDF
        pages = self.step1_parse_pdfs()
        
        if not pages:
            print("错误: 没有解析到任何页面")
            return
        
        # 步骤2: 分块
        chunks = self.step2_chunk_text(pages)
        
        # 步骤3: 加载问答对
        qa_chunks = self.step3_load_qa_pairs()
        
        # 步骤4: 构建向量数据库
        self.step4_build_vector_store(chunks, qa_chunks)
        
        # 步骤5: 测试查询
        if api_key:
            self.step5_query(test_query, api_key)
        else:
            print("\n" + "=" * 60)
            print("注意: 未提供API密钥，跳过答案生成")
            print("如需生成答案，请提供Deepseek API密钥")
            print("=" * 60)
    
    def incremental_update(self, new_pdf_files: list, new_qa_file: str = None):
        """
        增量更新向量数据库
        
        Args:
            new_pdf_files: 新的PDF文件列表
            new_qa_file: 新的问答对文件
        """
        print("\n" + "=" * 60)
        print("增量更新向量数据库")
        print("=" * 60)
        
        # 解析新的PDF
        new_pages = []
        for pdf_file in new_pdf_files:
            pages = self.pdf_parser.extract_text_from_pdf(pdf_file)
            new_pages.extend(pages)
        
        if new_pages:
            new_chunks = self.text_chunker.split_pages(new_pages)
            self.vector_store.add_chunks(new_chunks)
            print(f"✓ 添加了 {len(new_chunks)} 个PDF块")
        
        # 加载新的问答对
        if new_qa_file and os.path.exists(new_qa_file):
            new_qa_chunks = self.qa_integrator.load_and_format(new_qa_file)
            self.vector_store.add_chunks(new_qa_chunks)
            print(f"✓ 添加了 {len(new_qa_chunks)} 个问答对块")
        
        # 获取更新后的信息
        info = self.vector_store.get_collection_info()
        print(f"\n✓ 更新完成，当前文档数量: {info['count']}")


if __name__ == "__main__":
    # 运行完整流程
    # 如果有本地模型，指定路径（使用绝对路径）
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    local_model_path = os.path.join(current_dir, "bge-large-zh-v1.5")
    
    print(f"模型路径: {local_model_path}")
    print(f"模型存在: {os.path.exists(local_model_path)}")
    
    pipeline = RAGPipeline(local_model_path=local_model_path)
    
    # 运行完整流程（需要API密钥才能生成答案）
    pipeline.run_full_pipeline(
        api_key="sk-7c679cc5cc024856a4ffd2311a2b556c",  # 替换为你的API密钥
        test_query="什么是局部语法？"
    )
