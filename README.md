# NLP学习项目 - PDF微调数据版

这是为语言学研究者设计的NLP实践项目集合，**专门用于从PDF生成微调数据**。

## 🎯 核心理解：两种微调方式

### 1️⃣ 指令微调（Instruction Fine-tuning）- 适合你！

**格式：问答对**
```json
{
  "instruction": "什么是计算语言学？",
  "input": "",
  "output": "计算语言学是语言学和计算机科学的交叉领域..."
}
```

**特点：**
- 让模型学会回答特定领域的问题
- 数据量需求少（几百到几千条）
- 适合你的PDF文献知识库
- **推荐使用！**

### 2️⃣ 预训练（Pre-training）

**格式：纯文本**
```
计算语言学是语言学和计算机科学的交叉领域。它使用计算方法来研究语言...
```

**特点：**
- 让模型学习语言模式
- 需要大量数据（百万级token）
- 适合从零训练基座模型
- 不推荐个人使用

---

## 📦 微调数据准备项目

### 🆕 项目8：PDF内容提取与结构化工具
**文件：** `project8_pdf_structurer.py`

**功能：**
- 从PDF中提取文本
- 按章节分割
- 提取关键概念
- 生成结构化数据

**输出：**
```json
{
  "file_name": "论文.pdf",
  "key_concepts": [{"concept": "计算语言学", "frequency": 23}],
  "sections": [{"title": "引言", "content": "..."}],
  "chunks": ["文本块1", "文本块2", ...]
}
```

**运行方式：**
```bash
python project8_pdf_structurer.py
```

**依赖：**
```bash
pip install PyPDF2 jieba
```

---

### 🆕 项目9：问答对生成器
**文件：** `project9_qa_generator.py`

**功能：**
- 从PDF内容自动生成问答对
- 多种问题类型：
  - 定义类："什么是X？"
  - 解释类："为什么X？"
  - 对比类："X与Y有什么区别？"
  - 总结类："请总结这段内容"
- 生成训练数据格式

**输出：**
```json
{
  "question": "什么是计算语言学？",
  "answer": "计算语言学是...",
  "type": "definition",
  "chunk_id": 1
}
```

**运行方式：**
```bash
python project9_qa_generator.py
```

**特点：** ⭐⭐⭐⭐⭐ **核心工具！自动生成问答对**

---

### 🆕 项目10：指令微调数据生成器
**文件：** `project10_finetuning_data.py`

**功能：**
- 支持多种训练格式：
  - Alpaca格式 (instruction-input-output)
  - Chat格式 (messages)
  - ShareGPT格式 (conversations)
  - LLaMA-2格式 (text)
- 数据集分割（训练/验证/测试）
- 数据质量检查
- 生成微调脚本

**输出格式示例：**

**Alpaca格式：**
```json
{
  "instruction": "什么是计算语言学？",
  "input": "",
  "output": "计算语言学是..."
}
```

**Chat格式：**
```json
{
  "messages": [
    {"role": "user", "content": "什么是计算语言学？"},
    {"role": "assistant", "content": "计算语言学是..."}
  ]
}
```

**运行方式：**
```bash
python project10_finetuning_data.py
```

**特点：** ⭐⭐⭐⭐⭐ **格式转换工具！**

---

### 🆕 项目11：PDF微调数据完整流程工具
**文件：** `project11_complete_pipeline.py`

**功能：** 一键完成整个流程！
1. 提取PDF内容
2. 生成问答对
3. 转换为训练格式
4. 数据质量检查
5. 生成微调脚本

**运行方式：**
```bash
python project11_complete_pipeline.py
```

**特点：** ⭐⭐⭐⭐⭐ **推荐！一站式解决方案**

---

## 🚀 快速开始

### 安装依赖

**必需依赖：**
```bash
pip install PyPDF2 jieba
```

**可选依赖（用于微调）：**
```bash
pip install transformers datasets torch
```

### 完整工作流程（推荐）

**方式1：使用完整流程工具（最简单）**

```bash
cd "D:\Program Files\Desktop\文献2010-2013\NLP"
python project11_complete_pipeline.py
```

然后按提示操作：
1. 选择批量处理（默认目录）
2. 等待处理完成
3. 检查生成的数据
4. 使用生成的微调脚本

**方式2：分步执行（更灵活）**

```bash
# 步骤1：提取PDF内容
python project8_pdf_structurer.py

# 步骤2：生成问答对
python project9_qa_generator.py

# 步骤3：转换为训练格式
python project10_finetuning_data.py
```

---

## 📊 你会得到什么

运行完整流程后，你会得到：

### 1. 结构化数据
- `batch_structured_pdfs.json`
- 包含PDF的章节、关键概念、文本块

### 2. 问答对
- `batch_qa_pairs.json`
- 包含自动生成的问答对
- 多种问题类型

### 3. 训练数据
- `train_data_alpaca.json` - Alpaca格式
- `train_data_chat.json` - Chat格式
- `train_data_sharegpt.json` - ShareGPT格式
- `train_data_llama2.json` - LLaMA-2格式

### 4. 微调脚本
- `finetune_script.py`
- 可直接运行的训练脚本

---

## 💡 使用建议

### 数据量建议

| 任务类型 | 最小数据量 | 推荐数据量 |
|---------|------------|------------|
| 简单问答 | 100-500条 | 1000-3000条 |
| 领域知识 | 500-1000条 | 3000-10000条 |
| 复杂推理 | 1000-2000条 | 10000+条 |

**你的PDF：** 100+篇，每篇生成20-50个问答对 = 2000-5000条数据

### 质量检查

生成数据后，务必检查：
1. ✓ 问答对是否准确
2. ✓ 问题是否清晰
3. ✓ 回答是否完整
4. ✓ 是否有重复
5. ✓ 格式是否正确

### 微调模型选择

**推荐模型：**
- **中文模型：** Qwen2.5-7B-Instruct, Baichuan2-7B-Chat
- **英文模型：** LLaMA-2-7B-Chat, Mistral-7B-Instruct
- **多语言：** Qwen2.5-14B-Instruct, Yi-34B-Chat

---

## 🎯 实际应用场景

### 场景1：创建领域问答机器人
```
你的PDF → 问答对 → 微调模型 → 领域问答机器人
```

### 场景2：文献知识库
```
你的PDF → 问答对 → 微调模型 → 智能文献检索
```

### 场景3：研究助手
```
你的PDF → 问答对 → 微调模型 → 研究助手AI
```

### 场景4：教学工具
```
你的PDF → 问答对 → 微调模型 → 教学辅助工具
```

---

## 📖 详细使用指南

### 步骤1：提取PDF内容

```bash
python project8_pdf_structurer.py
```

选择模式：
- 1. 单个PDF
- 2. 批量处理
- 3. 使用默认目录（推荐）

**输出：** `batch_structured_pdfs.json`

### 步骤2：生成问答对

```bash
python project9_qa_generator.py
```

选择模式：
- 1. 单个PDF
- 2. 批量处理
- 3. 使用默认目录（推荐）

**输出：** `batch_qa_pairs.json`

### 步骤3：转换为训练格式

```bash
python project10_finetuning_data.py
```

选择输出格式：
- 1. Alpaca格式（推荐）
- 2. Chat格式
- 3. ShareGPT格式
- 4. LLaMA-2格式
- 5. 生成所有格式

**输出：** `train_data_*.json`

### 步骤4：数据质量检查

工具会自动检查：
- 空字段
- 长度分布
- 重复数据

### 步骤5：生成微调脚本

工具会自动生成：
- 加载模型代码
- 数据预处理代码
- 训练参数
- 保存模型代码

---

## 🔧 微调执行

### 使用生成的脚本

```bash
# 安装依赖
pip install transformers datasets torch

# 运行微调脚本
python finetune_script.py
```

### 手动微调（推荐）

参考transformers官方文档：
https://huggingface.co/docs/transformers/training

---

## ❓ 常见问题

### Q: 问答对质量如何保证？
A:
1. 生成后人工检查
2. 删除不准确的问答对
3. 补充重要的问答对
4. 多轮迭代优化

### Q: 数据量不够怎么办？
A:
1. 增加PDF数量
2. 从同一PDF生成更多问答对
3. 使用数据增强（同义改写）
4. 结合公开数据集

### Q: 微调需要什么硬件？
A:
- **最小配置：** 16GB GPU (7B模型)
- **推荐配置：** 24GB+ GPU (7B-14B模型)
- **CPU训练：** 可能需要几天（不推荐）

### Q: 如何评估微调效果？
A:
1. 使用验证集评估
2. 人工测试问答效果
3. 对比基座模型表现
4. 收集用户反馈

---

## 🎓 下一步

完成数据准备后，你可以：

1. **开始微调**
   - 使用生成的脚本
   - 调整训练参数
   - 监控训练过程

2. **评估模型**
   - 在验证集上测试
   - 人工评估回答质量
   - 对比不同模型

3. **部署应用**
   - 部署为API服务
   - 集成到应用中
   - 持续优化

4. **分享成果**
   - 开源微调模型
   - 发布数据集
   - 撰写技术博客

---

## 📞 需要帮助？

遇到问题时：
1. 检查是否安装了PyPDF2和jieba
2. 查看生成的JSON文件
3. 检查问答对质量
4. 随时向我提问

**祝微调成功！用你的PDF创建专属的领域模型吧！** 🚀📚
