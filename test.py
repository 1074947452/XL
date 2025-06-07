import sys
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QTextEdit,
    QVBoxLayout, QPushButton, QHBoxLayout, QLineEdit, QDialog, QDialogButtonBox
)
import os
import re
from ollama import embeddings,chat,Message,generate
import base64
from threading import Thread
from PyQt5.QtWidgets import QTextEdit, QSizePolicy
from PyQt5.QtCore import Qt

ELEMENTS_FILE = "elements_all.txt"

def load_elements():
    if os.path.exists(ELEMENTS_FILE):
        with open(ELEMENTS_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return []

SCAMPER_STEPS = [
    ("S", "Substitute（替代）", "替换元素、材料、流程、人员等 我能替代哪些部分？如果用其他材料会怎样？"),
    ("C", "Combine（结合）", "将两个或多个元素结合 能否合并两个功能或产品？"),
    ("A", "Adapt（适应）", "调整形式、用途或环境 这个东西能在其他行业使用吗？"),
    ("M", "Modify（修改）", "改变形状、颜色、功能等 可以把它缩小、放大或增强吗？"),
    ("P", "Put to other use（用途转换）", "改变产品或功能的用途 它还能干别的吗？"),
    ("E", "Eliminate（消除）", "删除无用部分或简化流程 哪些部分可以省略？"),
    ("R", "Reverse（反转）", "调换顺序、功能或结构 如果我们反过来做会怎样？")
]

class ScamperApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCAMPER 创新工具")
        self.resize(600, 500)
        self.elements = load_elements()
        self.answers = {}
        self.step_index = 0
        self.element = ""
        self.initUI()
        self.messages = []

    def initUI(self):
        self.layout = QVBoxLayout()

        # 元素输入提示和输入框
        self.layout.addWidget(QLabel("请输入或点击按钮生成一个元素："))
        self.element_input = QLineEdit()
        self.element_input.setPlaceholderText("输入元素或者点击按钮生成")
        self.layout.addWidget(self.element_input)

        # 创建 QTextEdit 用于显示 AI 输出
        self.text_ai = QTextEdit()
        self.text_ai.setReadOnly(True)
        self.text_ai.setPlaceholderText("没有创意？可以尝试点击询问AI!!")
        # 设置高度策略，允许自动扩展
        self.text_ai.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.text_ai.setMinimumHeight(100)
        # 确保滚动条策略启用
        self.text_ai.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # 添加到布局
        self.layout.addWidget(self.text_ai)

        # 创建 QTextEdit 用于显示 AI 输出
        self.ask_ai = QLineEdit()
        self.ask_ai.setPlaceholderText("请输入你的问题!!")
        self.layout.addWidget(self.ask_ai)

        # 四个按钮：AI生成元素 / 本地生成元素 / AI生成例子 / 本地生成例子
        btn_layout = QHBoxLayout()
        btn_ai_elem = QPushButton("问AI")
        btn_ai_elem.clicked.connect(self.generate_element_from_llm)
        btn_local_elem = QPushButton("本地生成元素")
        btn_local_elem.clicked.connect(self.generate_element_from_local)
        btn_local_ex = QPushButton("本地生成例子")
        btn_local_ex.clicked.connect(self.generate_example_from_local)


        btn_layout.addWidget(btn_local_elem)
        btn_layout.addWidget(btn_local_ex)
        btn_layout.addWidget(btn_ai_elem)
        self.layout.addLayout(btn_layout)

        # 问题展示
        self.question_label = QLabel()
        self.layout.addWidget(self.question_label)

        # 示例提示
        self.example_label = QLabel("点击按钮生成例子以获取灵感")
        self.layout.addWidget(self.example_label)

        # 用户输入框
        self.answer_edit = QTextEdit()
        self.layout.addWidget(self.answer_edit)

        sx_layout = QHBoxLayout()
        self.pre_button = QPushButton("上一步")
        self.pre_button.clicked.connect(self.pre_step)


        # 下一步按钮
        self.next_button = QPushButton("下一步")
        self.next_button.clicked.connect(self.next_step)
        sx_layout.addWidget(self.pre_button)
        sx_layout.addWidget(self.next_button)
        self.layout.addLayout(sx_layout)

        self.setLayout(self.layout)
        self.load_step()

    def generate_element_from_llm(self):
        q = self.ask_ai.text()
        self.ask_ai.clear()
        if q == "":
            self.text_ai.insertPlainText("输入为空，请输入！\n")
            scroll_bar = self.text_ai.verticalScrollBar()
            scroll_bar.setValue(scroll_bar.maximum())
        else:
            self.text_ai.insertPlainText("正在生成中，请稍后！\n")
            scroll_bar = self.text_ai.verticalScrollBar()
            scroll_bar.setValue(scroll_bar.maximum())
            ask = q
            generate_example_thread = Thread(target=self.askllm, args=(ask,))
            generate_example_thread.start()

    def generate_element_from_local(self):
        if self.elements:
            self.element = random.choice(self.elements)
        else:
            self.element = "（本地元素为空）"
        self.element_input.setText(self.element)

    def generate_example_from_local(self):
        if self.elements:
            example = random.choice(self.elements)
        else:
            example = "（本地元素为空）"
        self.example_label.setText(f"灵感示例：{example}")
    def load_step(self):
        key, title, question = SCAMPER_STEPS[self.step_index]
        self.question_label.setText(f"步骤 {self.step_index + 1}：{title}\n{question}")
        self.answer_edit.setText(self.answers.get(key, ""))
        self.example_label.setText("点击按钮生成例子以获取灵感")
    def next_step(self):
        self.element = self.element_input.text().strip() or "未命名元素"
        key, _, _ = SCAMPER_STEPS[self.step_index]
        self.answers[key] = self.answer_edit.toPlainText()
        if self.step_index < len(SCAMPER_STEPS) - 1:
            self.step_index += 1
            self.load_step()
        else:
            self.show_summary()

    def pre_step(self):
        self.step_index = self.step_index - 1
        key, title, question = SCAMPER_STEPS[self.step_index]
        self.question_label.setText(f"步骤 {self.step_index+1}：{title}\n{question}")
        pre = self.answers.get(key, '(未填写)')
        self.answer_edit.setPlainText(pre)

    def show_summary(self):
        summary = f"SCAMPER 创意草案（元素：{self.element}）\n\n"
        for key, title, _ in SCAMPER_STEPS:
            summary += f"{title}: {self.answers.get(key, '(未填写)')}\n"
        safe_filename = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]+', '_', self.element)[:20]
        output_filename = f"output_{safe_filename}.txt"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(summary)

        dialog = QDialog(self)
        dialog.setWindowTitle("创意草案完成")
        layout = QVBoxLayout()
        text_box = QTextEdit()
        text_box.setReadOnly(True)
        text_box.setText(summary)
        layout.addWidget(text_box)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)
        dialog.setLayout(layout)
        dialog.resize(600, 400)
        dialog.exec_()
        self.close()
    def askllm(self,ask):

        self.messages.append(Message(role='user', content=ask, images=None, tool_calls=None))
        stream = chat('deepseek-r1:8b', messages=self.messages, stream=True)
        for chunk in stream:
            #print(chunk['message']['content'], end='', flush=True)
            respone = chunk['message']['content']
            self.text_ai.insertPlainText(respone)
            scroll_bar = self.text_ai.verticalScrollBar()
            scroll_bar.setValue(scroll_bar.maximum())
        self.text_ai.insertPlainText("\r\n"+"-"*90+"\r\n")
        scroll_bar = self.text_ai.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())





if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScamperApp()
    window.show()
    sys.exit(app.exec_())
