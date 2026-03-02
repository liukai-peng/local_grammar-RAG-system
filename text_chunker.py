"""
文本分块器 - 将长文本分成适合嵌入的小块
"""

import re
from typing import List, Dict, Any
import json


class TextChunker:
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: List[str] = None
    ):
        """
        初始化文本分块器
        
        Args:
            chunk_size: 每块的最大字符数
            chunk_overlap: 块之间的重叠字符数
            separators: 分隔符列表，按优先级排序
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        if separators is None:
            # 中文优先按句号、分号、逗号分割
            self.separators = ["\n\n", "\n", "。", "；", "，", ".", ";", ","]
        else:
            self.separators = separators
    
    def split_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        将文本分成多个块
        
        Args:
            text: 要分割的文本
            metadata: 元数据
            
        Returns:
            分块后的文本列表，每个块包含文本和元数据
        """
        if metadata is None:
            metadata = {}
        
        # 使用递归分割
        chunks = self._recursive_split(text)
        
        # 为每个块添加元数据
        chunk_list = []
        for idx, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_id"] = idx + 1
            chunk_metadata["chunk_count"] = len(chunks)
            
            chunk_list.append({
                "text": chunk,
                "metadata": chunk_metadata
            })
        
        return chunk_list
    
    def _recursive_split(self, text: str) -> List[str]:
        """
        递归分割文本
        
        Args:
            text: 要分割的文本
            
        Returns:
            分割后的文本列表
        """
        # 如果文本足够短，直接返回
        if len(text) <= self.chunk_size:
            return [text]
        
        # 尝试用分隔符分割
        for separator in self.separators:
            if separator in text:
                parts = text.split(separator)
                
                chunks = []
                current_chunk = ""
                
                for part in parts:
                    part = part.strip()
                    if not part:
                        continue
                    
                    # 如果当前块加上新部分不超过大小限制
                    if len(current_chunk) + len(part) + len(separator) <= self.chunk_size:
                        if current_chunk:
                            current_chunk += separator + part
                        else:
                            current_chunk = part
                    else:
                        # 保存当前块
                        if current_chunk:
                            chunks.append(current_chunk)
                        # 开始新块
                        current_chunk = part
                
                # 添加最后一个块
                if current_chunk:
                    chunks.append(current_chunk)
                
                # 如果成功分割，返回结果
                if len(chunks) > 1:
                    return chunks
        
        # 如果没有合适的分隔符，按字符分割
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk = text[i:i + self.chunk_size]
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def split_pages(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        分割多个页面
        
        Args:
            pages: 页面数据列表
            
        Returns:
            分块后的数据列表
        """
        all_chunks = []
        
        for page in pages:
            text = page.get("text", "")
            metadata = {
                "source": page.get("source", ""),
                "path": page.get("path", ""),
                "page": page.get("page", 0)
            }
            
            chunks = self.split_text(text, metadata)
            all_chunks.extend(chunks)
        
        return all_chunks
    
    def save_chunks(self, chunks: List[Dict[str, Any]], output_file: str = "chunks.json"):
        """
        保存分块结果
        
        Args:
            chunks: 分块数据
            output_file: 输出文件
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
        
        print(f"分块结果已保存到: {output_file}")
        print(f"共 {len(chunks)} 个块")


if __name__ == "__main__":
    # 测试分块器
    chunker = TextChunker(chunk_size=500, chunk_overlap=50)
    
    # 测试文本
    test_text = """
    局部语法是语料库语言学中的一个重要概念。它关注特定词汇或短语在特定语境中的语法模式。
    与传统语法不同，局部语法更加关注词汇和语法的结合，强调词汇-语法共现模式。
    局部语法研究在语料库语言学中有着广泛的应用，特别是在学术写作分析、话语分析等领域。
    通过局部语法分析，研究者可以揭示特定话语行为的语言特征和语用功能。
    例如，在学术写作中，定义、评价、例举等话语行为都有其独特的局部语法模式。
    这些模式不仅反映了语言的结构特征，也体现了特定学科的文化和规范。
    因此，局部语法研究对于理解学术话语具有重要意义。
    """
    
    chunks = chunker.split_text(test_text, {"test": "metadata"})
    
    print(f"测试文本分成了 {len(chunks)} 个块:")
    for idx, chunk in enumerate(chunks):
        print(f"\n块 {idx + 1}:")
        print(chunk["text"][:100] + "...")
        print(f"元数据: {chunk['metadata']}")
