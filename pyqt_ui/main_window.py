import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSignal
from pyqt_ui.novel_pre_processor_ui import NovelPreProcessorUI
from pyqt_ui.merge_files_ui import MergeFilesUI
from pyqt_ui.query_ui import QueryUI
from pyqt_ui.config_ui import ConfigUI
from pyqt_ui.reader_ui import ReaderUI
from pyqt_ui.language_ui import LanguageUI

from utils.i18n import t, set_language

class MainWindow(QMainWindow):
    language_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(t('app.title'))
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)


        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.novel_pre_processor_tab = NovelPreProcessorUI()
        self.tabs.addTab(self.novel_pre_processor_tab, t('tab.preprocess'))

        self.merge_files_tab = MergeFilesUI()
        self.tabs.addTab(self.merge_files_tab, t('tab.merge'))

        self.query_tab = QueryUI()
        self.tabs.addTab(self.query_tab, t('tab.query'))

        self.reader_tab = ReaderUI()
        self.tabs.addTab(self.reader_tab, t('tab.reader'))

        self.config_tab = ConfigUI()
        self.tabs.addTab(self.config_tab, t('tab.config'))
        # Language settings tab
        self.language_tab = LanguageUI()
        self.tabs.addTab(self.language_tab, t('language.label'))


        self.config_tab.config_saved.connect(self.query_tab.reload_config_and_update_ui)

        # Connect language change signal to all tabs
        # From Language tab -> MainWindow
        self.language_tab.language_changed.connect(self.handle_language_change)
        # MainWindow -> All tabs (including Language tab)
        self.language_changed.connect(self.language_tab.update_language)

        self.language_changed.connect(self.novel_pre_processor_tab.update_language)
        self.language_changed.connect(self.merge_files_tab.update_language)
        self.language_changed.connect(self.query_tab.update_language)
        self.language_changed.connect(self.reader_tab.update_language)
        self.language_changed.connect(self.config_tab.update_language)


    def handle_language_change(self, lang: str):
        set_language(lang)
        self.update_language()
        self.language_changed.emit()

    def update_language(self):
        self.setWindowTitle(t('app.title'))
        # Update tab titles
        self.tabs.setTabText(0, t('tab.preprocess'))
        self.tabs.setTabText(1, t('tab.merge'))
        self.tabs.setTabText(2, t('tab.query'))
        self.tabs.setTabText(3, t('tab.reader'))
        self.tabs.setTabText(4, t('tab.config'))
        # Language tab (last)
        self.tabs.setTabText(5, t('language.label'))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())