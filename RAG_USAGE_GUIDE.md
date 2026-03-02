# RAG系统使用指南

## 📚 系统概述

这是一个完整的RAG（检索增强生成）系统，用于处理局部语法文献，支持：

- ✅ 自动解析PDF文献
- ✅ 智能文本分块
- ✅ 本地向量化（无需API费用）
- ✅ 整合高质量问答对
- ✅ 基于Deepseek的答案生成
- ✅ 增量更新支持

---

## 🚀 快速开始

### 步骤1: 安装依赖

```bash
python rag_setup.py
```

### 步骤2: 运行完整流程

```bash
python rag_pipeline.py
```

### 步骤3: 查询测试

```bash
python rag_query.py
```

---

## 📁 文件说明

| 文件 | 功能 |
|------|------|
| `rag_setup.py` | 安装必要的依赖 |
| `pdf_parser.py` | PDF解析器，提取文本和元数据 |
| `text_chunker.py` | 文本分块器，智能分割文本 |
| `qa_integrator.py` | 问答对整合器，格式化问答对 |
| `vector_store.py` | 向量数据库管理器，使用Chroma |
| `rag_query.py` | RAG查询系统，检索和生成 |
| `rag_pipeline.py` | 完整流程，从PDF到查询 |

---

## 🔧 配置说明

### 1. PDF目录

默认PDF目录: `static/`

包含:
- `国内局部语法文献收集/` - 国内文献
- `国外局部语法文献收集/` - 国外文献

### 2. 问答对文件

默认问答对文件: `deepseek_detailed_results.json`

包含你之前提取的高质量问答对。

### 3. 向量数据库

默认配置:
- 集合名称: `local_grammar_papers`
- 持久化目录: `./chroma_db`
- 嵌入模型: `BAAI/bge-large-zh-v1.5`

### 4. LLM配置

默认使用Deepseek API:
- 模型: `deepseek-chat`
- API密钥: 需要提供

---

## 📖 详细使用方法

### 方法1: 运行完整流程（推荐）

```python
from rag_pipeline import RAGPipeline

# 初始化流程
pipeline = RAGPipeline()

# 运行完整流程
pipeline.run_full_pipeline(
    api_key="your-deepseek-api-key",
    test_query="什么是局部语法？"
)
```

### 方法2: 分步执行

```python
from rag_pipeline import RAGPipeline

# 初始化流程
pipeline = RAGPipeline()

# 步骤1: 解析PDF
pages = pipeline.step1_parse_pdfs("parsed_pdfs.json")

# 步骤2: 分块文本
chunks = pipeline.step2_chunk_text(pages, "chunks.json")

# 步骤3: 加载问答对
qa_chunks = pipeline.step3_load_qa_pairs()

# 步骤4: 构建向量数据库
pipeline.step4_build_vector_store(chunks, qa_chunks)

# 步骤5: 查询
pipeline.step5_query("局部语法研究有哪些应用？", api_key="your-api-key")
```

### 方法3: 使用查询系统

```python
from rag_query import RAGQuerySystem

# 初始化查询系统
rag_system = RAGQuerySystem(
    api_key="your-deepseek-api-key"
)

# 执行查询
result = rag_system.query(
    query="局部语法在学术写作中有什么应用？",
    n_results=5,
    generate_answer=True
)

# 打印结果
print(rag_system.format_result(result))
```

### 方法4: 仅检索（不生成答案）

```python
from rag_query import RAGQuerySystem

# 初始化查询系统（不提供API密钥）
rag_system = RAGQuerySystem()

# 仅检索
result = rag_system.retrieve(
    query="局部语法",
    n_results=5
)

# 打印检索结果
for idx, doc in enumerate(result, 1):
    print(f"\n[{idx}] {doc['metadata']['source']}")
    print(f"内容: {doc['text'][:200]}...")
```

---

## 🎯 高级功能

### 1. 增量更新

```python
from rag_pipeline import RAGPipeline

# 初始化流程
pipeline = RAGPipeline()

# 增量更新新的PDF
new_pdfs = ["new_paper1.pdf", "new_paper2.pdf"]
pipeline.incremental_update(new_pdfs)

# 增量更新新的问答对
pipeline.incremental_update([], "new_qa_pairs.json")
```

### 2. 自定义分块参数

```python
from text_chunker import TextChunker

# 创建自定义分块器
chunker = TextChunker(
    chunk_size=800,  # 更大的块
    chunk_overlap=100,  # 更大的重叠
    separators=["\n\n", "\n", "。", "；", "，"]  # 自定义分隔符
)
```

### 3. 自定义嵌入模型

```python
from vector_store import VectorStore

# 使用不同的嵌入模型
vector_store = VectorStore(
    embedding_model="BAAI/bge-small-zh-v1.5"  # 更小的模型
)
```

### 4. 元数据过滤

```python
from rag_query import RAGQuerySystem

# 初始化查询系统
rag_system = RAGQuerySystem()

# 检索特定类型的文档
results = rag_system.retrieve(
    query="局部语法",
    n_results=5,
    where={"type": "qa_pair"}  # 只检索问答对
)
```

---

## 💡 使用建议

### 1. 首次使用

- 使用默认配置运行完整流程
- 观察每个步骤的输出
- 测试几个查询，检查效果

### 2. 优化检索效果

- 调整`chunk_size`（500-1000）
- 调整`chunk_overlap`（50-100）
- 调整`n_results`（3-10）

### 3. 优化答案质量

- 调整`temperature`（0.1-0.7）
- 提供更详细的提示词
- 使用更强大的LLM模型

### 4. 性能优化

- 使用更小的嵌入模型（`bge-small-zh-v1.5`）
- 减少检索结果数量
- 使用批量处理

---

## 📊 系统架构

```
PDF文献 → 解析 → 分块 → 向量化 → 存储到Chroma
                                              ↓
问答对 → 格式化 → 向量化 → 存储到Chroma
                                              ↓
用户查询 → 检索 → 生成答案 → 返回结果
```

---

## 🔍 查询示例

### 示例1: 基础查询

```python
query = "什么是局部语法？"
```

### 示例2: 应用查询

```python
query = "局部语法在学术写作中有什么应用？"
```

### 示例3: 对比查询

```python
query = "中西方学者在局部语法使用上有什么差异？"
```

### 示例4: 方法查询

```python
query = "如何构建局部语法模式？"
```

---

## 🐛 常见问题

### 1. 嵌入模型下载慢

**解决方案**:
- 使用国内镜像
- 使用更小的模型
- 预下载模型

### 2. 向量数据库占用空间大

**解决方案**:
- 使用更小的嵌入模型
- 减少chunk大小
- 定期清理

### 3. 检索结果不准确

**解决方案**:
- 调整chunk大小
- 调整chunk重叠
- 增加检索数量
- 优化查询文本

### 4. 答案质量不高

**解决方案**:
- 调整temperature
- 增加检索数量
- 优化提示词
- 使用更强大的LLM

---

## 📈 性能指标

### 预期性能

- **PDF解析**: ~1页/秒
- **文本分块**: ~1000块/秒
- **向量化**: ~100块/秒（取决于模型）
- **检索**: <1秒
- **答案生成**: ~5-10秒（取决于查询长度）

### 资源占用

- **内存**: ~2-4GB（取决于模型大小）
- **磁盘**: ~1-5GB（取决于文档数量）
- **网络**: 仅首次下载模型需要

---

## 🎓 学习资源

### 相关文档

- `RAG.md` - RAG理论基础
- `Finetune_Parameters_Guide.md` - 微调参数指南
- `QUICK_START_FINETUNE.md` - 微调快速开始

### 技术文档

- ChromaDB: https://docs.trychroma.com/
- Sentence-Transformers: https://www.sbert.net/
- Deepseek API: https://platform.deepseek.com/

---

## 🚀 下一步

1. **运行完整流程**: `python rag_pipeline.py`
2. **测试查询**: 修改`rag_query.py`中的查询
3. **优化参数**: 根据效果调整参数
4. **增量更新**: 添加新的文献和问答对
5. **构建应用**: 基于RAG系统构建应用

---

## 💬 获取帮助

如果遇到问题:

1. 查看错误日志
2. 检查配置文件
3. 参考常见问题
4. 查看技术文档

---

**祝你使用愉快！** 🎉📚
