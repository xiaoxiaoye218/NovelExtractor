from typing import Dict

_current_lang = 'zh'

_translations: Dict[str, Dict[str, str]] = {
    'zh': {
        # Language
        'language.label': '语言',
        'language.zh': '中文',
        'language.en': '英文',

        # App & tabs
        'app.title': '小说提取工具',
        'tab.preprocess': '小说预处理',
        'tab.merge': '合并文件',
        'tab.query': '查询',
        'tab.reader': '小说阅读',
        'tab.config': '配置',

        # Common
        'common.input_dir': '输入目录:',
        'common.output_dir': '输出目录:',
        'common.select_dir': '选择目录',
        'common.select_input_dir': '选择输入目录',
        'common.select_output_dir': '选择输出目录',
        'common.input_file': '输入文件路径:',
        'common.output_dir_path': '输出目录路径:',
        'common.select_file': '选择文件',
        'common.clear_log': '清除日志',
        'common.run': '开始',
        'common.stop': '中止',
        'common.ok': '确定',
        'common.cancel': '取消',
        'common.warning': '警告',
        'common.error': '错误',
        'common.confirm': '确认',
        'common.text_files_filter': 'Text Files (*.txt)',

        # Query
        'query.provider': '提供商:',
        'query.model_id': '模型ID:',
        'query.concurrent': '并发数量:',
        'query.batch_size': '批次大小:',
        'query.prompt_file': 'Prompt文件:',
        'query.output_prefix': '输出文件名前缀:',
        'query.start_pos': '起始位置 (可选):',
        'query.end_pos': '终止位置 (可选):',
        'query.start': '开始查询',
        'query.stopping': '正在中止任务...',
        'query.stopped': '任务已中止。',
        'query.completed': '所有任务处理完成。',
        'query.init_failed': '初始化查询处理器失败: {err}',
        'query.run_error': '查询过程中发生错误: {err}',
        'query.invalid_input_dir': '错误: 请选择一个有效的输入目录。',
        'query.invalid_output_dir': '错误: 请选择一个有效的输出目录。',
        'query.invalid_prompt': '错误: 请选择一个有效的Prompt文件。',
        'query.started': '开始查询...',

        # Merge
        'merge.output_file_name': '输出文件名:',
        'merge.show_name': '在合并时显示文件名',
        'merge.start': '开始合并',
        'merge.success': '成功合并文件到 {path}',
        'merge.error': '合并过程中发生错误: {err}',
        'merge.invalid_input_dir': '错误: 请选择一个有效的输入目录。',
        'merge.invalid_output_dir': '错误: 请选择一个有效的输出目录。',

        # Preprocess
        'pre.start': '开始预处理',
        'pre.success': '成功预处理文件到 {path}',
        'pre.error': '预处理过程中发生错误: {err}',
        'pre.invalid_input_file': '错误: 请选择一个有效的输入文件。',
        'pre.invalid_output_dir': '错误: 请选择一个有效的输出目录。',

        # Reader
        'reader.browser_title': '📚 文件浏览器',
        'reader.select_folder': '选择文件夹',
        'reader.clear': '清空',
        'reader.clear_tooltip': '清空所有文件夹',
        'reader.no_dir': '未选择目录',
        'reader.current_dir': '当前目录: {path}',
        'reader.selected_dirs_header': '已选择 {count} 个文件夹:',
        'reader.more_dirs': '... 还有 {rest} 个',
        'reader.choose_file': '📖 请选择文件',
        'reader.ready': '就绪',
        'reader.word_count': '字数: {count}',
        'reader.edit': '编辑',
        'reader.save': '保存',
        'reader.edit_mode': '编辑模式',
        'reader.preview_mode': '预览模式',
        'reader.font_size': '字体大小:',
        'reader.font_size_status': '字体大小: {size}px',
        'reader.added_dir': '已添加目录: {path}',
        'reader.read_dir_failed': '读取文件夹失败: {path} - {err}',
        'reader.file_reloaded': '文件已从外部更新并重新加载',
        'reader.file_read_failed': '读取失败: {name}',
        'reader.file_monitor_error': '文件监控出错: {err}',
        'reader.close_folder': '关闭文件夹',
        'reader.folder_closed': '已关闭文件夹: {name}',
            'reader.saved': '已保存: {name}',
            'reader.autosave_failed': '自动保存失败: {err}',
            'reader.cleared_all': '已清空所有文件夹',


        # Config
        'config.providers': 'Providers',
        'config.other_settings': '其他设置',
        'config.add_provider': '添加 Provider',
        'config.add_provider_title': '添加 Provider',
        'config.add_provider_prompt': '输入 Provider 名称 (例如: my_provider):',
        'config.provider_exists': '该 Provider 名称已存在。',
        'config.rename_provider': '重命名 Provider',
        'config.rename_provider_prompt': '输入新的 Provider 名称:',
        'config.delete_provider': '删除 Provider',
        'config.delete_confirm': "确定要删除 Provider '{name}' 吗?",
        'config.cannot_load': '无法加载配置文件: {err}',
        'config.cannot_save': '无法保存配置文件: {err}',
        'config.add_model': '添加 Model',
        'config.add_model_prompt': '输入 Model 名称:',
        'config.rename_model': '重命名 Model',
        'config.rename_model_prompt': '输入新的 Model 名称:',
        'config.delete_model': '删除 Model',
    },
    'en': {
        # Language
        'language.label': 'Language',
        'language.zh': 'Chinese',
        'language.en': 'English',

        # App & tabs
        'app.title': 'Novel Extractor',
        'tab.preprocess': 'Preprocess',
        'tab.merge': 'Merge Files',
        'tab.query': 'Query',
        'tab.reader': 'Reader',
        'tab.config': 'Config',

        # Common
        'common.input_dir': 'Input Directory:',
        'common.output_dir': 'Output Directory:',
        'common.select_dir': 'Browse',
        'common.select_input_dir': 'Select Input Directory',
        'common.select_output_dir': 'Select Output Directory',
        'common.input_file': 'Input File Path:',
        'common.output_dir_path': 'Output Directory Path:',
        'common.select_file': 'Browse File',
        'common.clear_log': 'Clear Log',
        'common.run': 'Start',
        'common.stop': 'Stop',
        'common.ok': 'OK',
        'common.cancel': 'Cancel',
        'common.warning': 'Warning',
        'common.error': 'Error',
        'common.confirm': 'Confirm',
        'common.text_files_filter': 'Text Files (*.txt)',

        # Query
        'query.provider': 'Provider:',
        'query.model_id': 'Model ID:',
        'query.concurrent': 'Concurrency:',
        'query.batch_size': 'Batch Size:',
        'query.prompt_file': 'Prompt File:',
        'query.output_prefix': 'Output Filename Prefix:',
        'query.start_pos': 'Start Position (optional):',
        'query.end_pos': 'End Position (optional):',
        'query.start': 'Start Query',
        'query.stopping': 'Stopping task...',
        'query.stopped': 'Task was stopped.',
        'query.completed': 'All tasks completed.',
        'query.init_failed': 'Failed to initialize query processor: {err}',
        'query.run_error': 'Error occurred during query: {err}',
        'query.invalid_input_dir': 'Error: Please select a valid input directory.',
        'query.invalid_output_dir': 'Error: Please select a valid output directory.',
        'query.invalid_prompt': 'Error: Please select a valid prompt file.',
        'query.started': 'Starting query...',

        # Merge
        'merge.output_file_name': 'Output Filename:',
        'merge.show_name': 'Show filename when merging',
        'merge.start': 'Start Merge',
        'merge.success': 'Successfully merged files to {path}',
        'merge.error': 'Error during merge: {err}',
        'merge.invalid_input_dir': 'Error: Please select a valid input directory.',
        'merge.invalid_output_dir': 'Error: Please select a valid output directory.',

        # Preprocess
        'pre.start': 'Start Preprocessing',
        'pre.success': 'Preprocessed successfully to {path}',
        'pre.error': 'Error during preprocessing: {err}',
        'pre.invalid_input_file': 'Error: Please select a valid input file.',
        'pre.invalid_output_dir': 'Error: Please select a valid output directory.',

        # Reader
        'reader.browser_title': '📚 File Browser',
        'reader.select_folder': 'Select Folder',
        'reader.clear': 'Clear',
        'reader.clear_tooltip': 'Clear all folders',
        'reader.no_dir': 'No directory selected',
        'reader.current_dir': 'Current directory: {path}',
        'reader.selected_dirs_header': '{count} folders selected:',
        'reader.more_dirs': '... and {rest} more',
        'reader.choose_file': '📖 Please select a file',
        'reader.ready': 'Ready',
        'reader.word_count': 'Words: {count}',
        'reader.edit': 'Edit',
        'reader.save': 'Save',
        'reader.edit_mode': 'Edit mode',
        'reader.preview_mode': 'Preview mode',
        'reader.font_size': 'Font size:',
        'reader.font_size_status': 'Font size: {size}px',
        'reader.added_dir': 'Added directory: {path}',
        'reader.read_dir_failed': 'Failed to read folder: {path} - {err}',
        'reader.file_reloaded': 'File updated externally and reloaded',
        'reader.file_read_failed': 'Read failed: {name}',
        'reader.file_monitor_error': 'File monitor error: {err}',
        'reader.close_folder': 'Close folder',
        'reader.folder_closed': 'Closed folder: {name}',
            'reader.autosave_failed': 'Auto-save failed: {err}',
            'reader.cleared_all': 'All folders cleared',
            'reader.saved': 'Saved: {name}',

        # Config
        'config.providers': 'Providers',
        'config.other_settings': 'Other Settings',
        'config.add_provider': 'Add Provider',
        'config.add_provider_title': 'Add Provider',
        'config.add_provider_prompt': 'Enter provider name (e.g., my_provider):',
        'config.provider_exists': 'Provider name already exists.',
        'config.rename_provider': 'Rename Provider',
        'config.rename_provider_prompt': 'Enter new provider name:',
        'config.delete_provider': 'Delete Provider',
        'config.delete_confirm': "Are you sure to delete provider '{name}'?",
        'config.cannot_load': 'Failed to load config file: {err}',
        'config.cannot_save': 'Failed to save config file: {err}',
        'config.add_model': 'Add Model',
        'config.add_model_prompt': 'Enter model name:',
        'config.rename_model': 'Rename Model',
        'config.rename_model_prompt': 'Enter new model name:',
        'config.delete_model': 'Delete Model',
    }
}

def set_language(lang: str):
    global _current_lang
    if lang in _translations:
        _current_lang = lang


def get_language() -> str:
    return _current_lang


def t(key: str, **kwargs) -> str:
    lang_map = _translations.get(_current_lang, {})
    text = lang_map.get(key)
    if text is None:
        # fallback to zh then key
        text = _translations.get('zh', {}).get(key, key)
    try:
        return text.format(**kwargs)
    except Exception:
        return text

