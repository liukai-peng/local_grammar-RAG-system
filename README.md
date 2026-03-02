# 局部语法RAG系统 (Local Grammar RAG System)

## 📚 项目概述

这是一个专为语言学研究者设计的**检索增强生成(RAG)系统**，专注于局部语法研究领域。系统通过向量检索技术，从大量PDF文献中快速找到相关内容，并结合大语言模型生成准确、专业的回答。

## ✨ 核心功能

### 🎯 智能检索
- **语义搜索**：基于BGE-Large-ZH模型的向量检索
- **多维度过滤**：支持按文献类型、作者等元数据过滤
- **高效索引**：纯Python实现的向量存储，无需依赖ChromaDB

### 🤖 智能生成
- **专业回答**：基于DeepSeek等大语言模型
- **上下文感知**：结合检索结果生成有依据的回答
- **可调节参数**：支持调整温度、结果数量等参数

### 🖥️ 桌面应用
- **直观界面**：基于PyQt5的现代化GUI
- **实时反馈**：查询过程实时显示
- **历史记录**：保存查询历史，方便重复查询
- **参数配置**：可视化调整系统参数

### 📄 文献管理
- **PDF解析**：支持从PDF中提取文本
- **结构化存储**：按章节、关键词组织文献内容
- **多语言支持**：主要支持中文和英文文献

## 🛠️ 技术栈

- **前端**：PyQt5 (桌面应用)
- **后端**：Python 3.12+
- **向量检索**：Sentence-Transformers (BGE-Large-ZH)
- **大语言模型**：DeepSeek (可配置)
- **PDF处理**：PyMuPDF
- **数据存储**：纯Python向量存储

## 📦 安装说明

### 1. 环境准备

```bash
# 推荐使用Conda创建虚拟环境
conda create -n rag_env python=3.12
conda activate rag_env

# 安装依赖
pip install -r requirements_app.txt
```

### 2. 模型下载

需要下载以下模型文件：

1. **BGE-Large-ZH模型**：
   - 下载地址：https://huggingface.co/BAAI/bge-large-zh-v1.5
   - 解压到 `./bge-large-zh-v1.5/` 目录

2. **ONNX版本**（可选，性能更优）：
   - 下载地址：https://huggingface.co/BAAI/bge-large-zh-v1.5/tree/onnx
   - 解压到 `./bge-large-zh-v1.5-onnx/` 目录

### 3. 配置文件

复制配置文件模板并填写API密钥：

```bash
cp config.json.example config.json
# 编辑config.json文件，填写你的API密钥
```

配置文件说明：

```json
{
  "api_key": "your-api-key-here",       // DeepSeek API密钥
  "llm_model": "deepseek-chat",          // LLM模型名称
  "persist_directory": "./chroma_db_merged_1024",  // 向量存储目录
  "local_model_path": "./bge-large-zh-v1.5-onnx",  // 本地模型路径
  "n_results": 5,                         // 检索结果数量
  "temperature": 0.3,                     // 生成温度
  "collection_name": "local_grammar_papers"  // 集合名称
}
```

## 🚀 使用方法

### 1. 启动应用

```bash
# 方法1：使用批处理脚本
start_rag.bat

# 方法2：直接运行Python文件
python rag_desktop_app.py
```

### 2. 基本操作

1. **输入查询**：在搜索框中输入你的问题
2. **调整参数**：可调整检索结果数量和生成温度
3. **执行查询**：点击"查询"按钮或按Enter键
4. **查看结果**：在结果区域查看生成的回答和相关文献
5. **历史记录**：在历史标签页查看之前的查询

### 3. 示例查询

- "什么是局部语法？"
- "局部语法与系统功能语法的区别是什么？"
- "如何构建局部语法模型？"
- "局部语法在学术论文中的应用"

## 📁 项目结构

```
RAG/
├── bge-large-zh-v1.5/          # BGE模型文件
├── bge-large-zh-v1.5-onnx/     # ONNX版本模型
├── chroma_db_*/                # 向量数据库（自动生成）
├── static/                     # 静态资源和PDF文献
├── __pycache__/                # Python缓存
├── rag_desktop_app.py          # 桌面应用主文件
├── rag_query.py                # RAG查询系统
├── pure_vector_store.py        # 纯Python向量存储
├── pdf_parser.py               # PDF解析工具
├── config.json.example         # 配置文件模板
├── requirements_app.txt        # 依赖文件
├── start_rag.bat               # 启动脚本
├── README.md                   # 项目说明
└── LICENSE                     # 开源许可证
```

## 🔍 工作原理

1. **文档处理**：系统首先解析PDF文献，提取文本内容并进行分块
2. **向量索引**：使用BGE-Large-ZH模型将文本块转换为向量并建立索引
3. **用户查询**：接收用户输入的问题
4. **语义检索**：将查询转换为向量，在索引中查找最相似的文本块
5. **答案生成**：将检索到的相关文本作为上下文，通过大语言模型生成回答
6. **结果展示**：在界面上展示生成的回答和相关文献信息

## 📝 注意事项

1. **API密钥**：需要有效的DeepSeek API密钥才能生成回答
2. **模型文件**：首次运行需要下载模型文件，约1GB左右
3. **性能要求**：推荐使用8GB以上内存的设备
4. **网络连接**：生成回答时需要网络连接（如果使用在线LLM）
5. **文献准备**：首次使用需要准备PDF文献并建立索引

## 🤝 贡献

欢迎贡献代码、提出问题或建议！

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 📞 联系

- 作者：liukai-peng
- 邮箱：1284877660@qq.com
- GitHub：https://github.com/liukai-peng/local_grammar-RAG-system

---

**⭐ 如果这个项目对你有帮助，请给它一个星标！**