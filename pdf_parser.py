"""
PDF解析器 - 提取PDF文本和元数据
"""

import fitz  # PyMuPDF
import os
from pathlib import Path
import json
from typing import List, Dict, Any
import re

class PDFParser:
    def __init__(self):
        pass
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        从PDF提取文本和元数据
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            包含页面文本和元数据的列表
        """
        if not os.path.exists(pdf_path):
            print(f"错误: 文件不存在 {pdf_path}")
            return []
        
        doc = fitz.open(pdf_path)
        pages_data = []
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            
            # 清洗文本
            cleaned_text = self.clean_text(text)
            
            if cleaned_text.strip():
                pages_data.append({
                    "page": page_num + 1,
                    "text": cleaned_text,
                    "source": os.path.basename(pdf_path),
                    "path": pdf_path
                })
        
        doc.close()
        return pages_data
    
    def clean_text(self, text: str) -> str:
        """
        清洗文本，去除页眉页脚等
        
        Args:
            text: 原始文本
            
        Returns:
            清洗后的文本
        """
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # 去除纯数字行（可能是页码）
            if line.isdigit():
                continue
            # 去除过短的行
            if len(line) < 10:
                continue
            # 去除常见的页眉页脚模式
            if re.match(r'^\d+\s*$', line):
                continue
            if re.match(r'^Page\s*\d+\s*$', line):
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def extract_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """
        提取PDF元数据
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            元数据字典
        """
        doc = fitz.open(pdf_path)
        metadata = {
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "subject": doc.metadata.get("subject", ""),
            "keywords": doc.metadata.get("keywords", ""),
            "creator": doc.metadata.get("creator", ""),
            "producer": doc.metadata.get("producer", ""),
            "page_count": len(doc),
            "filename": os.path.basename(pdf_path),
            "path": pdf_path
        }
        doc.close()
        return metadata
    
    def parse_directory(self, directory: str, output_file: str = "parsed_pdfs.json") -> List[Dict[str, Any]]:
        """
        解析目录中的所有PDF文件
        
        Args:
            directory: 目录路径
            output_file: 输出文件路径
            
        Returns:
            所有页面的数据列表
        """
        pdf_files = list(Path(directory).rglob("*.pdf"))
        
        print(f"找到 {len(pdf_files)} 个PDF文件")
        
        all_pages = []
        
        for idx, pdf_file in enumerate(pdf_files):
            print(f"\n处理 {idx+1}/{len(pdf_files)}: {pdf_file.name}")
            
            try:
                pages = self.extract_text_from_pdf(str(pdf_file))
                all_pages.extend(pages)
                print(f"  提取了 {len(pages)} 页")
            except Exception as e:
                print(f"  错误: {e}")
        
        # 保存结果
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_pages, f, ensure_ascii=False, indent=2)
        
        print(f"\n总计提取 {len(all_pages)} 页")
        print(f"结果已保存到: {output_file}")
        
        return all_pages


if __name__ == "__main__":
    parser = PDFParser()
    
    # 解析static目录下的所有PDF
    pdf_dir = "static"
    output_file = "parsed_pdfs.json"
    
    if os.path.exists(pdf_dir):
        pages = parser.parse_directory(pdf_dir, output_file)
        print(f"\n完成！共处理 {len(pages)} 页")
    else:
        print(f"错误: 目录不存在 {pdf_dir}")
