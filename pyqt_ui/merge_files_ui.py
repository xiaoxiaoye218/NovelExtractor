import sys
import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QFileDialog, QTextEdit, QMenu
from PyQt5.QtCore import Qt

from app.merge_files import merge_files_by_number

class MergeFilesUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Input directory
        input_layout = QHBoxLayout()
        self.input_dir_label = QLabel("输入目录:")
        self.input_dir_edit = QLineEdit()
        self.input_dir_button = QPushButton("选择目录")
        self.input_dir_button.clicked.connect(self.select_input_dir)
        input_layout.addWidget(self.input_dir_label)
        input_layout.addWidget(self.input_dir_edit)
        input_layout.addWidget(self.input_dir_button)
        layout.addLayout(input_layout)

        # Output directory
        output_dir_layout = QHBoxLayout()
        self.output_dir_label = QLabel("输出目录:")
        self.output_dir_edit = QLineEdit()
        self.output_dir_button = QPushButton("选择目录")
        self.output_dir_button.clicked.connect(self.select_output_dir)
        output_dir_layout.addWidget(self.output_dir_label)
        output_dir_layout.addWidget(self.output_dir_edit)
        output_dir_layout.addWidget(self.output_dir_button)
        layout.addLayout(output_dir_layout)

        # Output file name
        output_layout = QHBoxLayout()
        self.output_file_label = QLabel("输出文件名:")
        self.output_file_edit = QLineEdit("merged_output.txt")
        output_layout.addWidget(self.output_file_label)
        output_layout.addWidget(self.output_file_edit)
        layout.addLayout(output_layout)

        # Show name checkbox
        self.show_name_checkbox = QCheckBox("在合并时显示文件名")
        layout.addWidget(self.show_name_checkbox)

        # Run button
        self.run_button = QPushButton("开始合并")
        self.run_button.clicked.connect(self.run_merge)
        layout.addWidget(self.run_button)

        # Log display
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.log_edit.customContextMenuRequested.connect(self.show_log_context_menu)
        layout.addWidget(self.log_edit)

        self.setLayout(layout)

    def show_log_context_menu(self, pos):
        context_menu = QMenu(self)
        clear_action = context_menu.addAction("清除日志")
        action = context_menu.exec_(self.log_edit.mapToGlobal(pos))
        if action == clear_action:
            self.log_edit.clear()

    def select_input_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择输入目录")
        if dir_path:
            self.input_dir_edit.setText(dir_path)

    def select_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.output_dir_edit.setText(dir_path)

    def run_merge(self):
        input_dir = self.input_dir_edit.text().strip()
        output_dir = self.output_dir_edit.text().strip()
        output_name = self.output_file_edit.text().strip()
        show_name = self.show_name_checkbox.isChecked()

        if not input_dir or not os.path.isdir(input_dir):
            self.log_edit.append("错误: 请选择一个有效的输入目录。")
            return

        # 输出目录为必填
        if not output_dir or not os.path.isdir(output_dir):
            self.log_edit.append("错误: 请选择一个有效的输出目录。")
            return
        
        # 默认文件名
        if not output_name:
            output_name = "merged_output.txt"


        output_file = os.path.join(output_dir, output_name)

        try:
            # Redirect stdout to log_edit
            sys.stdout = self
            merge_files_by_number(input_dir, output_file, show_name)
            self.log_edit.append(f"成功合并文件到 {output_file}")
        except Exception as e:
            self.log_edit.append(f"合并过程中发生错误: {e}")
        finally:
            # Restore stdout
            sys.stdout = sys.__stdout__

    def write(self, text):
        self.log_edit.append(text.strip())

    def flush(self):
        pass