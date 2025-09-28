import sys
import os
import asyncio
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QTextEdit, QSpinBox, QComboBox, QMenu
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from utils.paths import get_config_path
from utils.i18n import t

from app.query import Query

class QueryWorker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    log_output = pyqtSignal(str)

    def __init__(self, query_processor):
        super().__init__()
        self.query_processor = query_processor

    def run(self):
        try:
            # Redirect stdout to emit signal
            sys.stdout = self
            asyncio.run(self.query_processor.process_query())
            # 无论是否请求过中止，任务结束后都发出 finished，UI 会根据中止标志显示不同提示
            self.finished.emit()
        except Exception as e:
            # 中止场景下不弹错误
            if not self.isInterruptionRequested():
                self.error.emit(str(e))
        finally:
            # Restore stdout
            sys.stdout = sys.__stdout__

    def write(self, text):
        self.log_output.emit(text.strip())

    def flush(self):
        pass

class QueryUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.reload_config_and_update_ui()

    def load_config(self):
        try:
            with open(get_config_path(), 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def reload_config_and_update_ui(self):
        """Reloads config and updates UI elements."""
        self.config_data = self.load_config()
        self.provider_combo.clear()
        if self.config_data and "PROVIDER_CONFIG" in self.config_data:
            providers = self.config_data["PROVIDER_CONFIG"].keys()
            self.provider_combo.addItems(providers)
            default_provider = self.config_data.get("DEFAULT_PROVIDER")
            if default_provider in providers:
                self.provider_combo.setCurrentText(default_provider)
        # The currentIndexChanged signal will automatically call update_model_combo

    def init_ui(self):
        layout = QVBoxLayout()

        # Input Path
        input_path_layout = QHBoxLayout()
        self.input_path_label = QLabel(t('common.input_dir'))
        self.input_path_edit = QLineEdit()
        self.input_path_button = QPushButton(t('common.select_dir'))
        self.input_path_button.clicked.connect(lambda: self.select_directory(self.input_path_edit))
        input_path_layout.addWidget(self.input_path_label)
        input_path_layout.addWidget(self.input_path_edit)
        input_path_layout.addWidget(self.input_path_button)
        layout.addLayout(input_path_layout)

        # Output Path
        output_path_layout = QHBoxLayout()
        self.output_path_label = QLabel(t('common.output_dir'))
        self.output_path_edit = QLineEdit()
        self.output_path_button = QPushButton(t('common.select_dir'))
        self.output_path_button.clicked.connect(lambda: self.select_directory(self.output_path_edit))
        output_path_layout.addWidget(self.output_path_label)
        output_path_layout.addWidget(self.output_path_edit)
        output_path_layout.addWidget(self.output_path_button)
        layout.addLayout(output_path_layout)

        # Provider
        provider_layout = QHBoxLayout()
        self.provider_label = QLabel(t('query.provider'))
        self.provider_combo = QComboBox()
        self.provider_combo.currentIndexChanged.connect(self.update_model_combo)
        provider_layout.addWidget(self.provider_label)
        provider_layout.addWidget(self.provider_combo)
        layout.addLayout(provider_layout)

        # Model
        model_layout = QHBoxLayout()
        self.model_label = QLabel(t('query.model_id'))
        self.model_combo = QComboBox()
        model_layout.addWidget(self.model_label)
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)

        # Concurrent
        concurrent_layout = QHBoxLayout()
        self.concurrent_label = QLabel(t('query.concurrent'))
        self.concurrent_spin = QSpinBox()
        self.concurrent_spin.setRange(1, 1000)
        self.concurrent_spin.setValue(100)
        concurrent_layout.addWidget(self.concurrent_label)
        concurrent_layout.addWidget(self.concurrent_spin)
        layout.addLayout(concurrent_layout)

        # Batch Size
        batch_size_layout = QHBoxLayout()
        self.batch_size_label = QLabel(t('query.batch_size'))
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(1, 1000)
        self.batch_size_spin.setValue(30)
        batch_size_layout.addWidget(self.batch_size_label)
        batch_size_layout.addWidget(self.batch_size_spin)
        layout.addLayout(batch_size_layout)

        # Prompt Path
        prompt_path_layout = QHBoxLayout()
        self.prompt_path_label = QLabel(t('query.prompt_file'))
        self.prompt_path_edit = QLineEdit()
        self.prompt_path_button = QPushButton(t('common.select_file'))
        self.prompt_path_button.clicked.connect(lambda: self.select_file(self.prompt_path_edit, t('common.text_files_filter')))
        prompt_path_layout.addWidget(self.prompt_path_label)
        prompt_path_layout.addWidget(self.prompt_path_edit)
        prompt_path_layout.addWidget(self.prompt_path_button)
        layout.addLayout(prompt_path_layout)

        # Name Prefix
        name_prefix_layout = QHBoxLayout()
        self.name_prefix_label = QLabel(t('query.output_prefix'))
        self.name_prefix_edit = QLineEdit("查询结果")
        name_prefix_layout.addWidget(self.name_prefix_label)
        name_prefix_layout.addWidget(self.name_prefix_edit)
        layout.addLayout(name_prefix_layout)

        # Start Position
        start_pos_layout = QHBoxLayout()
        self.start_pos_label = QLabel(t('query.start_pos'))
        self.start_pos_spin = QSpinBox()
        self.start_pos_spin.setRange(0, 999999) # 0 means None
        self.start_pos_spin.setValue(0)
        start_pos_layout.addWidget(self.start_pos_label)
        start_pos_layout.addWidget(self.start_pos_spin)
        layout.addLayout(start_pos_layout)

        # End Position
        end_pos_layout = QHBoxLayout()
        self.end_pos_label = QLabel(t('query.end_pos'))
        self.end_pos_spin = QSpinBox()
        self.end_pos_spin.setRange(0, 999999) # 0 means None
        self.end_pos_spin.setValue(0)
        end_pos_layout.addWidget(self.end_pos_label)
        end_pos_layout.addWidget(self.end_pos_spin)
        layout.addLayout(end_pos_layout)

        # Run button
        run_button_layout = QHBoxLayout()
        self.run_button = QPushButton(t('query.start'))
        self.run_button.clicked.connect(self.run_query)
        self.stop_button = QPushButton(t('common.stop'))
        self.stop_button.clicked.connect(self.stop_query)
        self.stop_button.setEnabled(False)
        run_button_layout.addWidget(self.run_button)
        run_button_layout.addWidget(self.stop_button)
        layout.addLayout(run_button_layout)

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

    def update_model_combo(self):
        if not self.config_data:
            return

        provider = self.provider_combo.currentText()
        self.model_combo.clear()

        if provider and "PROVIDER_CONFIG" in self.config_data and provider in self.config_data["PROVIDER_CONFIG"]:
            models = self.config_data["PROVIDER_CONFIG"][provider].get("models", [])
            self.model_combo.addItems(models)

            default_provider = self.config_data.get("DEFAULT_PROVIDER")
            if provider == default_provider:
                default_model = self.config_data.get("DEFAULT_MODEL_NAME")
                if default_model in models:
                    self.model_combo.setCurrentText(default_model)

    def select_directory(self, line_edit):
        dir_path = QFileDialog.getExistingDirectory(self, t('common.select_dir'))
        if dir_path:
            line_edit.setText(dir_path)

    def select_file(self, line_edit, file_filter):
        file_path, _ = QFileDialog.getOpenFileName(self, t('common.select_file'), "", file_filter)
        if file_path:
            line_edit.setText(file_path)

    def stop_query(self):
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.requestInterruption()
            # 通知Query逻辑取消未开始的任务
            try:
                if hasattr(self.worker, 'query_processor'):
                    self.worker.query_processor.request_cancel()
            except Exception:
                pass
            self.log_edit.append(t('query.stopping'))
            # 中止进行中时，开始/中止按钮都置灰
            self.run_button.setEnabled(False)
            self.stop_button.setEnabled(False)

    def run_query(self):
        input_path = self.input_path_edit.text()
        output_path = self.output_path_edit.text()
        provider_id = self.provider_combo.currentText()
        model_id = self.model_combo.currentText()
        concurrent = self.concurrent_spin.value()
        batch_size = self.batch_size_spin.value()
        prompt_path = self.prompt_path_edit.text()
        name_prefix = self.name_prefix_edit.text()
        start_pos = self.start_pos_spin.value()
        end_pos = self.end_pos_spin.value()

        if start_pos == 0: start_pos = None
        if end_pos == 0: end_pos = None

        if not input_path or not os.path.isdir(input_path):
            self.log_edit.append(t('query.invalid_input_dir'))
            return
        if not output_path:
            self.log_edit.append(t('query.invalid_output_dir'))
            return
        if not prompt_path or not os.path.exists(prompt_path):
            self.log_edit.append(t('query.invalid_prompt'))
            return

        self.log_edit.clear()
        self.log_edit.append(t('query.started'))

        try:
            query_processor = Query(
                input_path=input_path,
                output_path=output_path,
                provider_id=provider_id,
                model_id=model_id,
                concurrent=concurrent,
                batch_size=batch_size,
                prompt_path=prompt_path,
                name_prefix=name_prefix,
                start_pos=start_pos,
                end_pos=end_pos
            )

            self.worker = QueryWorker(query_processor)
            self.worker.finished.connect(self.query_finished)
            self.worker.error.connect(self.query_error)
            self.worker.log_output.connect(self.log_edit.append)
            # 启动任务前，更新按钮状态
            self.run_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.worker.start()

        except Exception as e:
            self.log_edit.append(t('query.init_failed', err=str(e)))
            self.run_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def query_finished(self):
        if self.worker.isInterruptionRequested():
            self.log_edit.append(t('query.stopped'))
        else:
            self.log_edit.append(t('query.completed'))
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def query_error(self, error_message):
        self.log_edit.append(t('query.run_error', err=error_message))
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_language(self):
        """Update UI text when language changes"""
        self.input_path_label.setText(t('common.input_dir'))
        self.output_path_label.setText(t('common.output_dir'))
        self.provider_label.setText(t('query.provider'))
        self.model_label.setText(t('query.model_id'))
        self.concurrent_label.setText(t('query.concurrent'))
        self.batch_size_label.setText(t('query.batch_size'))
        self.prompt_path_label.setText(t('query.prompt_file'))
        self.name_prefix_label.setText(t('query.output_prefix'))
        self.start_pos_label.setText(t('query.start_pos'))
        self.end_pos_label.setText(t('query.end_pos'))
        self.input_path_button.setText(t('common.select_dir'))
        self.output_path_button.setText(t('common.select_dir'))
        self.prompt_path_button.setText(t('common.select_file'))
        self.run_button.setText(t('query.start'))
        self.stop_button.setText(t('common.stop'))