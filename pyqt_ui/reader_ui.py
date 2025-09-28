import sys
import os
import re
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QTextEdit,
                             QLabel, QFileDialog, QSplitter, QFrame, QMenu)
from PyQt5.QtCore import Qt, QTimer, QEvent
from PyQt5.QtGui import QFont, QColor
from utils.readtxt import read_text_file


class ReaderUI(QWidget):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.current_directory = ""
        self.directories = []
        self.directory_items = {}
        self.last_modified_time = None
        self._cached_raw_content = "" # Cache for raw text content
        self.is_dirty = False
        self.text_display = None
        self.file_list = None
        self.font_size_value_label = None

        self.file_check_timer = QTimer()
        self.file_check_timer.timeout.connect(self.check_file_changes)
        self.file_check_timer.start(2000)

        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.save_file)
        
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)

        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)

        splitter.setSizes([300, 900])

        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton#fontAdjustButton {
                padding: 4px;
                font-weight: bold;
            }
            #如果设置的太大，会导致“padding: 8px 16px; 对于一个 30x30 像素的按钮来说太大了，这导致没有足够的空间来正确渲染文本 "A+" 和 "A-"，从而出现乱码。而“选择文件夹”等其他按钮因为可以根据内容自适应宽度，所以没有受到影响”
            QTreeWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QTreeWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QTreeWidget::item:hover {
                background-color: #f0f0f0;
            }
            QTreeWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QTextEdit {
                background-color: #fafafa;
                border: 1px solid #ddd;
                border-radius: 4px;
                line-height: 1.6;
                padding: 20px;
            }
        """)

    def create_left_panel(self):
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(10, 10, 10, 10)

        title_label = QLabel("📚 文件浏览器")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333;
            padding: 10px 0;
        """)
        left_layout.addWidget(title_label)

        dir_button_layout = QHBoxLayout()

        self.select_dir_btn = QPushButton("选择文件夹")
        self.select_dir_btn.clicked.connect(self.select_directory)
        dir_button_layout.addWidget(self.select_dir_btn)

        self.clear_dir_btn = QPushButton("清空")
        self.clear_dir_btn.clicked.connect(self.clear_directories)
        self.clear_dir_btn.setToolTip("清空所有文件夹")
        dir_button_layout.addWidget(self.clear_dir_btn)

        left_layout.addLayout(dir_button_layout)

        self.dir_label = QLabel("未选择目录")
        self.dir_label.setWordWrap(True)
        self.dir_label.setStyleSheet("""
            font-size: 12px;
            color: #666;
            padding: 5px;
            background-color: #f9f9f9;
            border-radius: 4px;
            max-height: 60px;
        """)
        left_layout.addWidget(self.dir_label)

        self.file_list = QTreeWidget()
        self.file_list.setHeaderHidden(True)
        self.file_list.itemClicked.connect(self.on_tree_item_clicked)
        self.file_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.file_list.setFocusPolicy(Qt.StrongFocus)
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        left_layout.addWidget(self.file_list)

        return left_frame

    def create_right_panel(self):
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(10, 10, 10, 10)

        # Create text_display first to get initial font size
        self.text_display = QTextEdit()
        self.text_display.setFont(QFont("Microsoft YaHei", 12))
        self.text_display.installEventFilter(self)

        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)

        self.file_title = QLabel("📖 请选择文件")
        self.file_title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #333;
            padding: 10px 0;
        """)
        toolbar_layout.addWidget(self.file_title)

        toolbar_layout.addStretch()

        self.edit_save_btn = QPushButton("编辑")
        self.edit_save_btn.clicked.connect(self.toggle_edit_mode)
        self.edit_save_btn.setEnabled(False) # Disable until a file is loaded
        toolbar_layout.addWidget(self.edit_save_btn)

        self.font_size_label = QLabel("字体大小:")
        toolbar_layout.addWidget(self.font_size_label)
        
        self.font_size_value_label = QLabel(f"{self.text_display.font().pointSize()}px")
        toolbar_layout.addWidget(self.font_size_value_label)

        self.decrease_font_btn = QPushButton("A-")
        self.decrease_font_btn.setObjectName("fontAdjustButton")
        self.decrease_font_btn.setFixedSize(30, 30)
        self.decrease_font_btn.clicked.connect(self.decrease_font_size)
        toolbar_layout.addWidget(self.decrease_font_btn)

        self.increase_font_btn = QPushButton("A+")
        self.increase_font_btn.setObjectName("fontAdjustButton")
        self.increase_font_btn.setFixedSize(30, 30)
        self.increase_font_btn.clicked.connect(self.increase_font_size)
        toolbar_layout.addWidget(self.increase_font_btn)

        right_layout.addWidget(toolbar)
        
        right_layout.addWidget(self.text_display)

        status_bar = QWidget()
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(0, 0, 0, 0)

        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("""
            font-size: 12px;
            color: #666;
            padding: 5px;
        """)
        status_layout.addWidget(self.status_label)

        status_layout.addStretch()

        self.word_count_label = QLabel("字数: 0")
        self.word_count_label.setStyleSheet("""
            font-size: 12px;
            color: #666;
            padding: 5px;
        """)
        status_layout.addWidget(self.word_count_label)

        right_layout.addWidget(status_bar)

        return right_frame

    def eventFilter(self, obj, event):
        # This event filter is now only for handling Ctrl+S shortcut
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_S and (event.modifiers() & Qt.ControlModifier):
            if not self.text_display.isReadOnly(): # Only save in edit mode
                self.leave_edit_mode() # This also saves the file
                return True
        return super().eventFilter(obj, event)

    def toggle_edit_mode(self):
        if self.text_display.isReadOnly():
            self.enter_edit_mode()
        else:
            self.leave_edit_mode()

    def enter_edit_mode(self):
        if not self.current_file:
            return
        try:
            self.text_display.textChanged.disconnect()
        except TypeError:
            pass
        
        self.text_display.setPlainText(self._cached_raw_content)
        self.text_display.setReadOnly(False)
        self.text_display.textChanged.connect(self.on_text_changed)
        self.status_label.setText("编辑模式")
        self.edit_save_btn.setText("保存")
        self.text_display.setFocus()

    def leave_edit_mode(self, save=False):
        try:
            self.text_display.textChanged.disconnect()
        except TypeError:
            pass

        if self.save_timer.isActive():
            self.save_timer.stop()
            self.save_file()

        # 切换为预览模式并按 Markdown 渲染
        self.text_display.setReadOnly(True)
        self._render_preview(self._cached_raw_content)
        self.status_label.setText("预览模式")
        self.edit_save_btn.setText("编辑")
        self.update_file_title()

    def on_text_changed(self):
        self.is_dirty = True
        self.save_timer.start(1000)

    def save_file(self):
        if not self.current_file or not self.is_dirty:
            return
        try:
            current_text = self.text_display.toPlainText()
            # Compare with cached content
            if self._cached_raw_content == current_text:
                self.is_dirty = False
                self.update_file_title()
                return

            self._cached_raw_content = current_text
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(self._cached_raw_content)

            self.last_modified_time = os.path.getmtime(self.current_file)
            self.is_dirty = False
            self.update_file_title()
            self.status_label.setText(f"已保存: {os.path.basename(self.current_file)}")

            word_count = len(self._cached_raw_content.replace('\n', '').replace(' ', ''))
            self.word_count_label.setText(f"字数: {word_count:,}")

        except Exception as e:
            self.status_label.setText(f"自动保存失败: {str(e)}")

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择文件夹", self.current_directory or "")
        if directory and directory not in self.directories:
            self.directories.append(directory)
            if not self.current_directory:
                self.current_directory = directory
            self.update_directory_display()
            self.add_directory_to_tree(directory)

    def clear_directories(self):
        self.directories.clear()
        self.current_directory = ""
        self.file_list.clear()
        self.directory_items.clear()
        self.dir_label.setText("未选择目录")
        self.status_label.setText("已清空所有文件夹")

    def update_directory_display(self):
        if not self.directories:
            self.dir_label.setText("未选择目录")
        elif len(self.directories) == 1:
            self.dir_label.setText(f"当前目录: {self.directories[0]}")
        else:
            dir_text = f"已选择 {len(self.directories)} 个文件夹:\n"
            for i, dir_path in enumerate(self.directories[:3], 1):
                dir_text += f"{i}. {os.path.basename(dir_path)}\n"
            if len(self.directories) > 3:
                dir_text += f"... 还有 {len(self.directories) - 3} 个"
            self.dir_label.setText(dir_text.strip())

    def load_all_files(self):
        self.file_list.clear()
        self.directory_items = {} # Map directory path to QTreeWidgetItem

        for directory in self.directories:
            self.add_directory_to_tree(directory)

        if self.file_list.topLevelItemCount() > 0:
            first_folder = self.file_list.topLevelItem(0)
            if first_folder.childCount() > 0:
                first_file = first_folder.child(0)
                self.file_list.setCurrentItem(first_file)
                # self.load_file(first_file) # Selection change will trigger load

    def add_directory_to_tree(self, directory):
        if directory in self.directory_items:
            return # Already exists

        try:
            folder_name = os.path.basename(directory)
            folder_item = QTreeWidgetItem(self.file_list, [f"📁 {folder_name}"])
            folder_item.setData(0, Qt.UserRole, directory)
            folder_item.setExpanded(True)
            font = folder_item.font(0)
            font.setBold(True)
            folder_item.setFont(0, font)
            self.directory_items[directory] = folder_item

            txt_files = [f for f in os.listdir(directory) if f.endswith('.txt')]
            
            def natural_sort_key(filename):
                return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', filename)]
            
            txt_files.sort(key=natural_sort_key)
            
            for filename in txt_files:
                full_path = os.path.join(directory, filename)
                file_item = QTreeWidgetItem(folder_item, [f"  📄 {filename}"])
                file_item.setData(0, Qt.UserRole, full_path)
            
            self.status_label.setText(f"已添加目录: {directory}")

        except Exception as e:
            self.status_label.setText(f"读取文件夹失败: {directory} - {str(e)}")


    def on_tree_item_clicked(self, item, column):
        if item.childCount() > 0:  # It's a folder
            item.setExpanded(not item.isExpanded())
        else:  # It's a file
            self.load_file(item)

    def on_selection_changed(self):
        current_item = self.file_list.currentItem()
        if current_item and current_item.childCount() == 0:
            self.load_file(current_item)

    def load_file(self, item):
        if not item or item.childCount() > 0:
            return

        filepath = item.data(0, Qt.UserRole)
        if not filepath: return

        if self.current_file == filepath:
            return

        if not self.text_display.isReadOnly():
            self.leave_edit_mode()

        try:
            content = read_text_file(filepath)
            self._cached_raw_content = content

            self.text_display.setReadOnly(True)
            self._render_preview(self._cached_raw_content)
            self.file_title.setText(f"📖 {os.path.basename(filepath)}")
            self.current_file = filepath
            self.last_modified_time = os.path.getmtime(filepath)
            self.is_dirty = False
            self.edit_save_btn.setEnabled(True)

            word_count = len(content.replace('\n', '').replace(' ', ''))
            self.word_count_label.setText(f"字数: {word_count:,}")
            self.status_label.setText("预览模式")

        except Exception as e:
            self.text_display.setPlainText(f"读取文件失败: {str(e)}")
            self.status_label.setText(f"读取失败: {os.path.basename(filepath)}")
            self.edit_save_btn.setEnabled(False)


    def _render_preview(self, text):
        """Render given text in preview (read-only) mode as Markdown when possible.
        Treats .txt content as Markdown for display only.
        Fallbacks: Qt Markdown -> python-markdown -> plain text.
        Also preserves single newlines as hard line breaks to avoid losing
        visual line breaks for plain text.
        """
        # Normalize and preserve single line breaks as Markdown hard breaks
        try:
            norm = text.replace('\r\n', '\n').replace('\r', '\n')
            # Turn single newlines into hard breaks, keep paragraph breaks (double newlines)
            norm = re.sub(r'(?<!\n)\n(?!\n)', '  \n', norm)
        except Exception:
            norm = text

        # Prefer Qt's native Markdown support (Qt >= 5.14)
        try:
            if hasattr(self.text_display, "setMarkdown"):
                self.text_display.setMarkdown(norm)
                return
        except Exception:
            pass

        # Fallback: try python-markdown if available
        try:
            import markdown as _md
            html = _md.markdown(norm, extensions=['extra'])
            self.text_display.setHtml(html)
        except Exception:
            # Last resort: show plain text
            self.text_display.setPlainText(text)

    def update_file_title(self):
        if not self.current_file:
            self.file_title.setText("📖 请选择文件")
            return

        title = os.path.basename(self.current_file)
        if self.is_dirty:
            title += " *"
        self.file_title.setText(f"📖 {title}")

    def increase_font_size(self):
        current_font = self.text_display.font()
        new_size = min(current_font.pointSize() + 2, 36)
        current_font.setPointSize(new_size)
        self.text_display.setFont(current_font)
        self.font_size_value_label.setText(f"{new_size}px")
        self.status_label.setText(f"字体大小: {new_size}px")

    def decrease_font_size(self):
        current_font = self.text_display.font()
        new_size = max(current_font.pointSize() - 2, 8)
        current_font.setPointSize(new_size)
        self.text_display.setFont(current_font)
        self.font_size_value_label.setText(f"{new_size}px")
        self.status_label.setText(f"字体大小: {new_size}px")

    def check_file_changes(self):
        if not self.current_file or not os.path.exists(self.current_file) or not self.text_display.isReadOnly():
            return

        try:
            current_modified_time = os.path.getmtime(self.current_file)
            if self.last_modified_time and current_modified_time > self.last_modified_time:
                new_content = read_text_file(self.current_file)
                if new_content != self._cached_raw_content:
                    self.reload_current_file(new_content)
                self.last_modified_time = current_modified_time
        except Exception as e:
            self.status_label.setText(f"文件监控出错: {str(e)}")

    def reload_current_file(self, new_content=None):
        if not self.current_file: return

        try:
            if new_content is None:
                new_content = read_text_file(self.current_file)

            self._cached_raw_content = new_content

            if not self.text_display.isReadOnly(): # In edit mode
                cursor_pos = self.text_display.textCursor().position()
                self.text_display.textChanged.disconnect()
                self.text_display.setPlainText(new_content)
                cursor = self.text_display.textCursor()
                cursor.setPosition(min(cursor_pos, len(new_content)))
                self.text_display.setTextCursor(cursor)
                self.text_display.textChanged.connect(self.on_text_changed)
            else: # In preview mode
                self._render_preview(new_content)

            self.last_modified_time = os.path.getmtime(self.current_file)
            self.status_label.setText("文件已从外部更新并重新加载")
            word_count = len(new_content.replace('\n', '').replace(' ', ''))
            self.word_count_label.setText(f"字数: {word_count:,}")

        except Exception as e:
            self.status_label.setText(f"重新加载文件失败: {str(e)}")

    def show_context_menu(self, pos):
        item = self.file_list.itemAt(pos)
        if item and item.parent() is None: # It's a top-level item (folder)
            menu = QMenu()
            close_action = menu.addAction("关闭文件夹")
            action = menu.exec_(self.file_list.mapToGlobal(pos))
            if action == close_action:
                self.close_folder(item)

    def close_folder(self, item):
        directory_to_close = item.data(0, Qt.UserRole)
        if directory_to_close in self.directories:
            self.directories.remove(directory_to_close)

            # If the closed folder contained the currently open file, clear the display
            if self.current_file and self.current_file.startswith(directory_to_close):
                self.text_display.clear()
                self.file_title.setText("📖 请选择文件")
                self.current_file = None
                self._cached_raw_content = ""
                self.word_count_label.setText("字数: 0")
                self.edit_save_btn.setEnabled(False)

            # Remove from tree and dictionary
            if directory_to_close in self.directory_items:
                index = self.file_list.indexOfTopLevelItem(self.directory_items[directory_to_close])
                if index != -1:
                    self.file_list.takeTopLevelItem(index)
                del self.directory_items[directory_to_close]

            self.update_directory_display()
            self.status_label.setText(f"已关闭文件夹: {os.path.basename(directory_to_close)}")