import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget
from pyqt_ui.novel_pre_processor_ui import NovelPreProcessorUI
from pyqt_ui.merge_files_ui import MergeFilesUI
from pyqt_ui.query_ui import QueryUI
from pyqt_ui.config_ui import ConfigUI
from pyqt_ui.reader_ui import ReaderUI

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("小说提取工具")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.novel_pre_processor_tab = NovelPreProcessorUI()
        self.tabs.addTab(self.novel_pre_processor_tab, "小说预处理")

        self.merge_files_tab = MergeFilesUI()
        self.tabs.addTab(self.merge_files_tab, "合并文件")

        self.query_tab = QueryUI()
        self.tabs.addTab(self.query_tab, "查询")

        self.reader_tab = ReaderUI()
        self.tabs.addTab(self.reader_tab, "小说阅读")

        self.config_tab = ConfigUI()
        self.tabs.addTab(self.config_tab, "配置")

        self.config_tab.config_saved.connect(self.query_tab.reload_config_and_update_ui)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())