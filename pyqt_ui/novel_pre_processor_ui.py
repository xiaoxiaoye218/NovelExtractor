import sys
import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QTextEdit, QMenu
from PyQt5.QtCore import Qt

from app.novel_pre_processor import TextProcessor, read_text_file # 假设这些是需要导入的
from utils.i18n import t

class NovelPreProcessorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Input file path
        input_layout = QHBoxLayout()
        self.input_path_label = QLabel(t('common.input_file'))
        self.input_path_edit = QLineEdit()
        self.input_path_button = QPushButton(t('common.select_file'))
        self.input_path_button.clicked.connect(self.select_input_path)
        input_layout.addWidget(self.input_path_label)
        input_layout.addWidget(self.input_path_edit)
        input_layout.addWidget(self.input_path_button)
        layout.addLayout(input_layout)

        # Output directory path
        output_layout = QHBoxLayout()
        self.output_path_label = QLabel(t('common.output_dir_path'))
        self.output_path_edit = QLineEdit()
        self.output_path_button = QPushButton(t('common.select_dir'))
        self.output_path_button.clicked.connect(self.select_output_path)
        output_layout.addWidget(self.output_path_label)
        output_layout.addWidget(self.output_path_edit)
        output_layout.addWidget(self.output_path_button)
        layout.addLayout(output_layout)

        # Run button
        self.run_button = QPushButton(t('pre.start'))
        self.run_button.clicked.connect(self.run_pre_processor)
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
        clear_action = context_menu.addAction(t('common.clear_log'))
        action = context_menu.exec_(self.log_edit.mapToGlobal(pos))
        if action == clear_action:
            self.log_edit.clear()

    def select_input_path(self):
        file_path, _ = QFileDialog.getOpenFileName(self, t('common.select_file'), "", t('common.text_files_filter'))
        if file_path:
            self.input_path_edit.setText(file_path)

    def select_output_path(self):
        dir_path = QFileDialog.getExistingDirectory(self, t('common.select_output_dir'))
        if dir_path:
            self.output_path_edit.setText(dir_path)

    def run_pre_processor(self):
        input_path = self.input_path_edit.text()
        output_path = self.output_path_edit.text()

        if not input_path or not os.path.exists(input_path):
            self.log_edit.append(t('pre.invalid_input_file'))
            return

        if not output_path:
            self.log_edit.append(t('pre.invalid_output_dir'))
            return

        try:
            # Redirect stdout to log_edit
            sys.stdout = self
            
            processor = TextProcessor()
            test_text = read_text_file(input_path)
            chapters = processor.split_chapters(test_text)
            
            os.makedirs(output_path, exist_ok=True)
            
            for chapter in chapters:
                chapter_title = f"第{chapter.number}章_{chapter.title.replace(' ', '').replace('　', '')}"
                filename = f"{chapter_title}_{chapter.number}.txt"
                filename = "".join(c for c in filename if c not in r'\/:*?"<>|')
                
                output_file = os.path.join(output_path, filename)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"{chapter_title}\n\n{chapter.content}")
                print(f"保存章节: {filename}")
            
            print(f"完成！共保存 {len(chapters)} 个章节文件到 {output_path}")
            self.log_edit.append(t('pre.success', path=output_path))
        except Exception as e:
            self.log_edit.append(t('pre.error', err=str(e)))
        finally:
            # Restore stdout
            sys.stdout = sys.__stdout__

    def write(self, text):
        self.log_edit.append(text.strip())

    def flush(self):
        pass

    def update_language(self):
        """Update UI text when language changes"""
        self.input_path_label.setText(t('common.input_file'))
        self.output_path_label.setText(t('common.output_dir_path'))
        self.input_path_button.setText(t('common.select_file'))
        self.output_path_button.setText(t('common.select_dir'))
        self.run_button.setText(t('pre.start'))