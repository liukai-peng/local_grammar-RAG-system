"""
局部语法RAG桌面应用
"""

import sys
import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QTabWidget,
    QFormLayout, QSpinBox, QDoubleSpinBox, QGroupBox, QListWidget,
    QListWidgetItem, QSplitter, QMessageBox, QProgressBar, QStatusBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

# 导入现有RAG功能
from rag_query import RAGQuerySystem

class QueryWorker(QThread):
    """后台查询线程"""
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, rag_system, query, n_results, temperature):
        super().__init__()
        self.rag_system = rag_system
        self.query = query
        self.n_results = n_results
        self.temperature = temperature
    
    def run(self):
        try:
            result = self.rag_system.query(
                self.query,
                n_results=self.n_results,
                generate_answer=True,
                temperature=self.temperature
            )
            self.result_ready.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))

class RAGDesktopApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("局部语法RAG助手")
        self.setGeometry(100, 100, 1200, 800)
        
        # 加载配置
        self.config = self.load_config()
        
        # 初始化RAG系统
        self.rag_system = None
        self.init_rag_system()
        
        # 历史记录
        self.history = []
        
        # 初始化UI
        self.init_ui()
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
    
    def load_config(self):
        """加载配置文件"""
        default_config = {
            "api_key": "",
            "llm_model": "deepseek-chat",
            "persist_directory": "./chroma_db_merged_final",
            "local_model_path": "./bge-large-zh-v1.5-onnx",
            "n_results": 5,
            "temperature": 0.3,
            "collection_name": "local_grammar_papers"
        }
        
        config_path = "config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                QMessageBox.warning(self, "配置错误", f"加载配置失败，使用默认配置: {str(e)}")
        
        return default_config
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open("config.json", 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            QMessageBox.warning(self, "保存失败", f"保存配置失败: {str(e)}")
            return False
    
    def init_rag_system(self):
        """初始化RAG系统"""
        try:
            self.rag_system = RAGQuerySystem(
                collection_name=self.config["collection_name"],
                persist_directory=self.config["persist_directory"],
                local_model_path=self.config["local_model_path"],
                api_key=self.config["api_key"],
                llm_model=self.config["llm_model"]
            )
            return True
        except Exception as e:
            QMessageBox.warning(self, "初始化失败", f"RAG系统初始化失败: {str(e)}")
            return False
    
    def init_ui(self):
        """初始化用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 选项卡
        self.tab_widget = QTabWidget()
        
        # 1. 查询页面
        self.query_tab = self.create_query_tab()
        self.tab_widget.addTab(self.query_tab, "智能查询")
        
        # 2. 设置页面
        self.settings_tab = self.create_settings_tab()
        self.tab_widget.addTab(self.settings_tab, "系统设置")
        
        # 3. 历史记录页面
        self.history_tab = self.create_history_tab()
        self.tab_widget.addTab(self.history_tab, "历史记录")
        
        main_layout.addWidget(self.tab_widget)
    
    def create_query_tab(self):
        """创建查询页面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 顶部查询区域
        query_layout = QHBoxLayout()
        
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("请输入你的问题，例如：什么是局部语法？")
        self.query_input.setFont(QFont("微软雅黑", 12))
        self.query_input.returnPressed.connect(self.on_query)
        
        self.query_btn = QPushButton("查询")
        self.query_btn.setFont(QFont("微软雅黑", 12))
        self.query_btn.clicked.connect(self.on_query)
        self.query_btn.setFixedWidth(100)
        
        query_layout.addWidget(self.query_input)
        query_layout.addWidget(self.query_btn)
        
        layout.addLayout(query_layout)
        
        # 中间内容区域（分割器）
        splitter = QSplitter(Qt.Vertical)
        
        # 答案显示区域
        self.answer_text = QTextEdit()
        self.answer_text.setReadOnly(True)
        self.answer_text.setFont(QFont("微软雅黑", 11))
        self.answer_text.setPlaceholderText("答案将显示在这里...")
        splitter.addWidget(self.answer_text)
        
        # 参考文献区域
        self.refs_list = QListWidget()
        self.refs_list.setFont(QFont("微软雅黑", 10))
        self.refs_list.setMaximumHeight(200)
        splitter.addWidget(self.refs_list)
        
        layout.addWidget(splitter)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        return widget
    
    def create_settings_tab(self):
        """创建设置页面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 基础设置组
        basic_group = QGroupBox("基础设置")
        basic_layout = QFormLayout(basic_group)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setText(self.config["api_key"])
        self.api_key_input.setEchoMode(QLineEdit.Password)
        basic_layout.addRow("Deepseek API密钥:", self.api_key_input)
        
        self.llm_model_input = QLineEdit()
        self.llm_model_input.setText(self.config["llm_model"])
        basic_layout.addRow("LLM模型名称:", self.llm_model_input)
        
        self.db_path_input = QLineEdit()
        self.db_path_input.setText(self.config["persist_directory"])
        basic_layout.addRow("向量库路径:", self.db_path_input)
        
        self.model_path_input = QLineEdit()
        self.model_path_input.setText(self.config["local_model_path"])
        basic_layout.addRow("本地模型路径:", self.model_path_input)
        
        layout.addWidget(basic_group)
        
        # 查询参数组
        query_group = QGroupBox("查询参数")
        query_layout = QFormLayout(query_group)
        
        self.n_results_spin = QSpinBox()
        self.n_results_spin.setRange(1, 20)
        self.n_results_spin.setValue(self.config["n_results"])
        query_layout.addRow("检索结果数量:", self.n_results_spin)
        
        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0.0, 1.0)
        self.temp_spin.setSingleStep(0.1)
        self.temp_spin.setValue(self.config["temperature"])
        query_layout.addRow("生成温度:", self.temp_spin)
        
        layout.addWidget(query_group)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        self.save_settings_btn = QPushButton("保存设置")
        self.save_settings_btn.clicked.connect(self.on_save_settings)
        btn_layout.addWidget(self.save_settings_btn)
        
        self.restart_rag_btn = QPushButton("重启RAG系统")
        self.restart_rag_btn.clicked.connect(self.on_restart_rag)
        btn_layout.addWidget(self.restart_rag_btn)
        
        layout.addLayout(btn_layout)
        
        # 添加说明
        help_label = QLabel("""
        <h3>使用说明</h3>
        <p>1. API密钥需要在Deepseek官网申请: <a href='https://platform.deepseek.com/'>https://platform.deepseek.com/</a></p>
        <p>2. 向量库路径默认使用合并后的数据库: ./chroma_db_merged</p>
        <p>3. 本地模型路径默认使用: ./bge-large-zh-v1.5</p>
        <p>4. 生成温度越低，答案越稳定；越高，答案越有创造性</p>
        """)
        help_label.setOpenExternalLinks(True)
        help_label.setWordWrap(True)
        layout.addWidget(help_label)
        
        layout.addStretch()
        
        return widget
    
    def create_history_tab(self):
        """创建历史记录页面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 历史记录列表
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.on_history_select)
        layout.addWidget(self.history_list)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        self.clear_history_btn = QPushButton("清空历史记录")
        self.clear_history_btn.clicked.connect(self.on_clear_history)
        btn_layout.addWidget(self.clear_history_btn)
        
        layout.addLayout(btn_layout)
        
        return widget
    
    def on_query(self):
        """处理查询请求"""
        query = self.query_input.text().strip()
        if not query:
            QMessageBox.warning(self, "输入错误", "请输入查询内容")
            return
        
        if not self.rag_system:
            QMessageBox.warning(self, "系统错误", "RAG系统未初始化，请检查设置")
            return
        
        # 禁用按钮，显示进度条
        self.query_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 无限进度
        self.status_bar.showMessage("正在查询...")
        self.answer_text.clear()
        self.refs_list.clear()
        
        # 启动后台线程
        self.worker = QueryWorker(
            self.rag_system,
            query,
            self.n_results_spin.value(),
            self.temp_spin.value()
        )
        self.worker.result_ready.connect(self.on_query_result)
        self.worker.error_occurred.connect(self.on_query_error)
        self.worker.finished.connect(self.on_query_finished)
        self.worker.start()
    
    def on_query_result(self, result):
        """处理查询结果"""
        # 显示答案
        answer = result.get("answer", "没有生成答案")
        self.answer_text.setHtml(f"""
        <h3>问题：{result['query']}</h3>
        <h3>答案：</h3>
        <p style='line-height: 1.6;'>{answer.replace('\n', '<br>')}</p>
        """)
        
        # 显示参考文献
        self.refs_list.clear()
        for idx, doc in enumerate(result["retrieved_docs"], 1):
            metadata = doc.get("metadata", {})
            source = metadata.get("source", "unknown")
            page = metadata.get("page", 0)
            similarity = 1 - doc.get("distance", 0)
            text = doc.get("text", "")[:200] + "..."
            
            item = QListWidgetItem(f"[{idx}] {os.path.basename(source)} - 第{page}页 (相似度: {similarity:.4f})\n{text}")
            item.setToolTip(f"完整内容:\n{doc.get('text', '')}")
            self.refs_list.addItem(item)
        
        # 添加到历史记录
        history_item = {
            "query": result["query"],
            "answer": answer,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(history_item)
        
        # 更新历史列表
        list_item = QListWidgetItem(f"{history_item['timestamp']} - {history_item['query'][:30]}...")
        list_item.setData(Qt.UserRole, history_item)
        self.history_list.insertItem(0, list_item)
        
        self.status_bar.showMessage("查询完成")
    
    def on_query_error(self, error_msg):
        """处理查询错误"""
        QMessageBox.critical(self, "查询错误", f"查询失败: {error_msg}")
        self.status_bar.showMessage("查询失败")
    
    def on_query_finished(self):
        """查询完成后清理"""
        self.query_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
    
    def on_save_settings(self):
        """保存设置"""
        self.config["api_key"] = self.api_key_input.text().strip()
        self.config["llm_model"] = self.llm_model_input.text().strip()
        self.config["persist_directory"] = self.db_path_input.text().strip()
        self.config["local_model_path"] = self.model_path_input.text().strip()
        self.config["n_results"] = self.n_results_spin.value()
        self.config["temperature"] = self.temp_spin.value()
        
        if self.save_config():
            QMessageBox.information(self, "保存成功", "配置已保存，重启RAG系统后生效")
    
    def on_restart_rag(self):
        """重启RAG系统"""
        self.status_bar.showMessage("正在重启RAG系统...")
        if self.init_rag_system():
            QMessageBox.information(self, "重启成功", "RAG系统已成功重启")
            self.status_bar.showMessage("RAG系统已就绪")
        else:
            self.status_bar.showMessage("RAG系统重启失败")
    
    def on_history_select(self, item):
        """选择历史记录"""
        history_item = item.data(Qt.UserRole)
        self.query_input.setText(history_item["query"])
        self.tab_widget.setCurrentIndex(0)  # 切换到查询页面
        
        # 显示历史结果
        self.answer_text.setHtml(f"""
        <h3>问题：{history_item['query']}</h3>
        <p><i>查询时间：{history_item['timestamp']}</i></p>
        <h3>答案：</h3>
        <p style='line-height: 1.6;'>{history_item['answer'].replace('\n', '<br>')}</p>
        """)
    
    def on_clear_history(self):
        """清空历史记录"""
        reply = QMessageBox.question(self, "确认清空", "确定要清空所有历史记录吗？",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.history.clear()
            self.history_list.clear()
            self.status_bar.showMessage("历史记录已清空")

if __name__ == "__main__":
    # 设置高DPI适配
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    app.setFont(QFont("微软雅黑", 9))
    
    window = RAGDesktopApp()
    window.show()
    
    sys.exit(app.exec_())
