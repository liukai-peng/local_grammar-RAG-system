"""
RAG系统设置 - 安装必要的依赖
"""

import subprocess
import sys

print("=" * 60)
print("RAG系统依赖安装")
print("=" * 60)

packages = [
    "chromadb",
    "sentence-transformers",
    "pymupdf",
    "langchain",
    "langchain-community",
    "langchain-openai",
    "openai",
]

for package in packages:
    print(f"\n安装 {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ {package} 安装成功")
    except Exception as e:
        print(f"✗ {package} 安装失败: {e}")

print("\n" + "=" * 60)
print("依赖安装完成！")
print("=" * 60)
