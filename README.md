# NovelExtractor｜小说提取工具

一个基于 PyQt5 的桌面应用，帮助你从整本小说文本中完成「分章 → 批量大模型查询 → 合并 → 阅读/编辑」的全流程处理。内置多厂商大模型路由（OpenAI 兼容/Gemini 等），支持高并发与断点重试，并提供 Windows 免安装可执行文件。

---

## 功能概览
- 小说预处理：将整本 `.txt` 小说按“第X章 标题”自动拆分为多个章节文件
- 批量查询：对章节批量调用 LLM，支持并发、批次控制、断点续跑、自定义 Prompt 模板
- 文件合并：按章节末尾编号顺序合并多个章节文件，可选在输出中写入文件名分隔
- 小说阅读：文件夹树浏览、Markdown 预览、快速编辑/自动保存、字号调节、外部变更自动刷新
- 可视化配置：图形化管理各 Provider 的 `base_url`、`api_key` 与 `models` 列表，保存到 `configs/config.json`

---

## 快速开始

### 方式 A：直接运行（Windows）
- 双击运行根目录下的 `NovelExtractor.exe`
- 首次使用请在“配置”页填写各大模型平台的 Base URL 与 API Key，并保存

### 方式 B：源码运行
1. 安装依赖（Python 3.9+）

   <augment_code_snippet mode="EXCERPT">
````bash
pip install -r requirements.txt
````
</augment_code_snippet>

2. 启动应用

   <augment_code_snippet mode="EXCERPT" path="run_ui.py">
````bash
python run_ui.py
````
</augment_code_snippet>

> 提示：配置文件默认位于 `configs/config.json`。打包后（exe 运行时）会优先使用可执行文件同级目录下的 `configs/config.json`（便携式配置）。

---

## 推荐使用流程
1. 在“配置”页添加/编辑 Provider（如 aliyun、zhipu、moonshot、doubao、siliconflow、google、openai），填入 `api_key`、`base_url`，添加可用 `models`
2. 在“小说预处理”页：选择整本小说 `.txt`，输出到一个章节目录（自动识别“第X章”并按自然顺序拆分）
3. 在“查询”页：
   - 选择“输入目录”为步骤 2 生成的章节目录
   - 选择“输出目录”与 Prompt 文件（必须包含 `{input_content}` 占位符）
   - 选择 Provider/Model，设置并发与批次大小，开始查询
   - 结果会生成如 `查询结果_bs30_批次1.txt`、`查询结果_bs30_批次2.txt` …
4. 在“合并文件”页：将多个章节 `.txt` 按末尾编号顺序合并为一个总文档（可选写入文件名分隔）
5. 在“小说阅读”页：打开章节目录或合并后的文本进行浏览、预览与快速编辑（Ctrl+S 保存）

---

## Prompt 模板要求
- Prompt 模板文件需为文本文件，并包含占位符 `{input_content}`，程序会将一个批次内的多章内容替换到该占位符处。

示例：

<augment_code_snippet mode="EXCERPT">
````text
你是一个小说分析助手。请阅读下面的章节内容，抽取主要人物、关键事件与时间线，并输出要点列表：

{input_content}
````
</augment_code_snippet>

---

## 命令行用法（可选）
除图形界面外，项目也提供命令行脚本，适合批处理或与其他流程集成。

- 批量查询：

  <augment_code_snippet mode="EXCERPT" path="app/query.py">
````bash
python app/query.py \
  --input_path "/path/to/chapters" \
  --output_path "/path/to/outputs" \
  --prompt_path "/path/to/prompt.txt" \
  --batch_size 10 \
  --concurrent 20 \
  --name_prefix "分析结果" \
  --provider aliyun \
  --model qwen3-next-80b-a3b-instruct \
  --start_pos 1 \
  --end_pos 50
````
</augment_code_snippet>

- 合并章节：

  <augment_code_snippet mode="EXCERPT" path="app/merge_files.py">
````bash
python app/merge_files.py \
  /path/to/chapters \
  -o /path/to/output/merged_output.txt \
  --show_name
````
</augment_code_snippet>

- 小说预处理（整本拆章）：

  <augment_code_snippet mode="EXCERPT" path="app/novel_pre_processor.py">
````bash
python app/novel_pre_processor.py -i /path/to/book.txt -o /path/to/chapters_dir
````
</augment_code_snippet>

---

## 配置说明
- 配置文件：`configs/config.json`
- 关键字段：
  - `PROVIDER_CONFIG`：各平台的 `type`（openai/gemini）、`base_url`、`api_key`、`models`
  - `DEFAULT_SYSTEM_PROMPT`：系统提示词
  - `DEFAULT_STREAM`、`DEFAULT_TEMPERATURE`、`DEFAULT_TOP_P`、`DEFAULT_MAX_TOKENS`、`DEFAULT_DOUBAO_THINKING` 等默认参数
  - 可在“配置”页可视化增删改 Provider、编辑模型列表、重命名 Provider，并自动保存
- 便携式配置：打包后优先读取 EXE 同目录下的 `configs/config.json`，不存在时会从内置默认拷贝一份

---

## 目录结构
<augment_code_snippet mode="EXCERPT">
````text
NovelExtractor/
├─ NovelExtractor.exe           # Windows 可执行文件（可选）
├─ run_ui.py                    # 启动图形界面
├─ requirements.txt             # 依赖
├─ configs/
│  └─ config.json               # 模型与全局配置
├─ app/
│  ├─ query.py                  # 批量 LLM 查询逻辑（并发/批次/断点续跑）
│  ├─ novel_pre_processor.py    # 整本小说拆分成章节
│  └─ merge_files.py            # 章节文件按编号合并
├─ pyqt_ui/
│  ├─ main_window.py            # 主窗体（多标签页）
│  ├─ query_ui.py               # 查询页
│  ├─ merge_files_ui.py         # 合并页
│  ├─ novel_pre_processor_ui.py # 预处理页
│  ├─ reader_ui.py              # 阅读/预览/编辑页
│  └─ config_ui.py              # 配置页
└─ utils/
   ├─ unified_chat.py           # 多厂商模型统一路由
   ├─ text_processor.py         # 拆章/统计/格式化
   ├─ readtxt.py                # 自动编码识别读取
   └─ paths.py                  # 打包/开发模式路径与配置定位
````
</augment_code_snippet>

---

## 注意事项与建议
- 模型无法调用/401：检查 `api_key` 与 `base_url` 是否正确，模型名称是否在该 Provider 的 `models` 列表中
- 超时或 429：适当降低并发，或检查网络情况
- 输入目录为空：确保选择的目录下有 `.txt` 文件
- 编码问题：`utils/readtxt.py` 会自动尝试 `utf-8`/`gbk`/`gb2312`，必要时请先转换编码
- 日志与状态：各页面底部日志/状态栏或控制台可查看实时输出

---

## 许可与贡献
- 许可证：暂未指定
- 欢迎提交 Issue/PR 改进功能或体验

---

## 致谢
- PyQt5
- OpenAI SDK（兼容接口）
- Google Generative AI SDK
