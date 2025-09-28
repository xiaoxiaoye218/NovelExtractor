from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from PyQt5.QtCore import pyqtSignal
from utils.i18n import t, set_language, get_language


class LanguageUI(QWidget):
    # Emit selected language code, e.g., 'zh' or 'en'
    language_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        row = QHBoxLayout()
        row.addStretch()

        self.label = QLabel(t('language.label') + ':')
        row.addWidget(self.label)

        self.combo = QComboBox()
        self.combo.addItem(t('language.zh'), 'zh')
        self.combo.addItem(t('language.en'), 'en')

        current = get_language()
        self.combo.setCurrentIndex(0 if current == 'zh' else 1)
        self.combo.currentIndexChanged.connect(self._on_combo_changed)

        row.addWidget(self.combo)
        row.addStretch()

        layout.addLayout(row)
        layout.addStretch()

    def _on_combo_changed(self):
        lang = self.combo.currentData()
        if lang:
            set_language(lang)
            self.language_changed.emit(lang)

    def update_language(self):
        # Preserve current selection
        current_lang = get_language()
        self.label.setText(t('language.label') + ':')
        self.combo.blockSignals(True)
        self.combo.clear()
        self.combo.addItem(t('language.zh'), 'zh')
        self.combo.addItem(t('language.en'), 'en')
        self.combo.setCurrentIndex(0 if current_lang == 'zh' else 1)
        self.combo.blockSignals(False)

