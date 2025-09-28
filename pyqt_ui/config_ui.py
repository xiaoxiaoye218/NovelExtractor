import sys
import json
from PyQt5.QtCore import pyqtSignal, QTimer, Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QPushButton, QListWidget, QAbstractItemView, QMessageBox,
    QTabWidget, QInputDialog, QGroupBox, QScrollArea, QMenu
)

from utils.paths import get_config_path
from utils.i18n import t

class ConfigUI(QWidget):
    config_saved = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.config_path = get_config_path()
        self.config_data = {}
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self.save_config)
        self._loading = False  # Flag to prevent saving while loading data

        self.init_ui()
        self.load_config()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)

        self.layout = QVBoxLayout(scroll_content)

        # Providers Group
        self.providers_group = QGroupBox(t('config.providers'))
        providers_layout = QVBoxLayout()
        self.tabs = QTabWidget()
        # Context menu for renaming providers via tab bar
        tab_bar = self.tabs.tabBar()
        tab_bar.setContextMenuPolicy(Qt.CustomContextMenu)
        tab_bar.customContextMenuRequested.connect(self._on_tab_context_menu)

        self.add_provider_button = QPushButton(t('config.add_provider'))
        self.add_provider_button.clicked.connect(self.add_provider)
        providers_layout.addWidget(self.tabs)
        providers_layout.addWidget(self.add_provider_button)
        self.providers_group.setLayout(providers_layout)
        self.layout.addWidget(self.providers_group)

        # Other settings Group
        self.other_settings_group = QGroupBox(t('config.other_settings'))
        self.other_settings_layout = QFormLayout()
        self.other_settings_group.setLayout(self.other_settings_layout)
        self.layout.addWidget(self.other_settings_group)

    def schedule_save(self):
        if not self._loading:
            self._save_timer.start(1000)  # Save 1 second after the last change

    def load_config(self):
        self._loading = True
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            QMessageBox.critical(self, t('common.error'), t('config.cannot_load', err=str(e)))
            self.config_data = {"PROVIDER_CONFIG": {}, "DEFAULT_SYSTEM_PROMPT": ""}

        self.tabs.clear()
        # Clear old widgets from other_settings_layout
        while self.other_settings_layout.count():
            child = self.other_settings_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Load providers
        provider_config = self.config_data.get("PROVIDER_CONFIG", {})
        for provider_name, config in provider_config.items():
            self.add_provider_tab(provider_name, config)

        # Load other settings
        self.other_widgets = {}
        for key, value in self.config_data.items():
            if key != "PROVIDER_CONFIG":
                label = key
                widget = QLineEdit(str(value))
                widget.textChanged.connect(self.schedule_save)
                self.other_settings_layout.addRow(label, widget)
                self.other_widgets[key] = widget

        self._loading = False

    def add_provider(self):
        provider_name, ok = QInputDialog.getText(self, t('config.add_provider_title'), t('config.add_provider_prompt'))
        if ok and provider_name:
            if provider_name in self.config_data.get("PROVIDER_CONFIG", {}):
                QMessageBox.warning(self, t('common.warning'), t('config.provider_exists'))
                return

            new_config = {
                "type": "openai",
                "base_url": "",
                "api_key": "",
                "models": []
            }
            if "PROVIDER_CONFIG" not in self.config_data:
                self.config_data["PROVIDER_CONFIG"] = {}
            self.config_data["PROVIDER_CONFIG"][provider_name] = new_config
            self.add_provider_tab(provider_name, new_config)
            self.schedule_save()

    def add_provider_tab(self, provider_name, config):
        tab = QWidget()
        layout = QFormLayout()

        # Type
        type_combo = QComboBox()
        type_combo.addItems(["openai", "gemini", "anthropic"])
        type_combo.setCurrentText(config.get("type", "openai"))
        type_combo.currentTextChanged.connect(self.schedule_save)
        layout.addRow("type:", type_combo)

        # Base URL
        base_url_edit = QLineEdit(config.get("base_url", ""))
        base_url_edit.textChanged.connect(self.schedule_save)
        layout.addRow("base_url:", base_url_edit)

        # API Key
        api_key_edit = QLineEdit(config.get("api_key", ""))
        api_key_edit.textChanged.connect(self.schedule_save)
        layout.addRow("api_key:", api_key_edit)

        # Models
        models_list = QListWidget()
        models_list.setSelectionMode(QAbstractItemView.SingleSelection)
        models_list.addItems(config.get("models", []))

        # Right-click context menu on models list for managing models
        models_list.setContextMenuPolicy(Qt.CustomContextMenu)
        def _show_models_menu(point):
            item = models_list.itemAt(point)
            menu = QMenu(models_list)
            if item is None:
                add_action = menu.addAction(t('config.add_model'))
                action = menu.exec_(models_list.mapToGlobal(point))
                if action == add_action:
                    model_name, ok = QInputDialog.getText(self, t('config.add_model'), t('config.add_model_prompt'))
                    if ok and model_name:
                        models_list.addItem(model_name)
                        self.schedule_save()
                return
            # When clicking on an existing item: only rename/delete
            rename_action = menu.addAction(t('config.rename_model'))
            delete_action = menu.addAction(t('config.delete_model'))
            action = menu.exec_(models_list.mapToGlobal(point))
            if action == rename_action:
                new_name, ok = QInputDialog.getText(self, t('config.rename_model'), t('config.rename_model_prompt'), text=item.text())
                if ok and new_name and new_name != item.text():
                    item.setText(new_name)
                    self.schedule_save()
            elif action == delete_action:
                row = models_list.row(item)
                models_list.takeItem(row)
                self.schedule_save()
        models_list.customContextMenuRequested.connect(_show_models_menu)

        layout.addRow("models:", models_list)


        tab.setLayout(layout)
        tab.setProperty("provider_name", provider_name)
        tab.setProperty("widgets", {
            "type": type_combo,
            "base_url": base_url_edit,
            "api_key": api_key_edit,
            "models": models_list
        })
        self.tabs.addTab(tab, provider_name)

    def _on_tab_context_menu(self, pos):
        tab_bar = self.tabs.tabBar()
        index = tab_bar.tabAt(pos)
        if index < 0:
            return
        menu = QMenu(self)
        rename_action = menu.addAction(t('config.rename_provider'))
        delete_action = menu.addAction(t('config.delete_provider'))
        action = menu.exec_(tab_bar.mapToGlobal(pos))
        if action == rename_action:
            self.rename_provider(index)
        elif action == delete_action:
            name = self.tabs.widget(index).property("provider_name")
            reply = QMessageBox.question(self, t('common.confirm'), t('config.delete_confirm', name=name),
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.tabs.removeTab(index)
                self.schedule_save()

    def rename_provider(self, index: int):
        tab = self.tabs.widget(index)
        old_name = tab.property("provider_name")
        new_name, ok = QInputDialog.getText(self, t('config.rename_provider'), t('config.rename_provider_prompt'), text=old_name)
        if not ok or not new_name or new_name == old_name:
            return
        # Ensure uniqueness among provider names
        for i in range(self.tabs.count()):
            if i == index:
                continue
            other_tab = self.tabs.widget(i)
            if other_tab.property("provider_name") == new_name:
                QMessageBox.warning(self, t('common.warning'), t('config.provider_exists'))
                return
        tab.setProperty("provider_name", new_name)
        self.tabs.setTabText(index, new_name)
        self.schedule_save()

    def save_config(self):
        if self._loading:
            return

        new_config_data = {}

        # Save providers
        provider_config = {}
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            provider_name = tab.property("provider_name")
            widgets = tab.property("widgets")

            models = []
            for j in range(widgets["models"].count()):
                models.append(widgets["models"].item(j).text())

            provider_config[provider_name] = {
                "type": widgets["type"].currentText(),
                "base_url": widgets["base_url"].text(),
                "api_key": widgets["api_key"].text(),
                "models": models
            }
        new_config_data["PROVIDER_CONFIG"] = provider_config

        # Save other settings
        for key, widget in self.other_widgets.items():
            new_config_data[key] = widget.text()

        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(new_config_data, f, indent=4, ensure_ascii=False)
            self.config_data = new_config_data
            self.config_saved.emit()
            print("Configuration saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, t('common.error'), t('config.cannot_save', err=str(e)))

    def update_language(self):
        """Update UI text when language changes"""
        self.providers_group.setTitle(t('config.providers'))
        self.other_settings_group.setTitle(t('config.other_settings'))
        self.add_provider_button.setText(t('config.add_provider'))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = ConfigUI()
    win.show()
    sys.exit(app.exec_())