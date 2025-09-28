# NovelExtractor｜小说提取工具

一个拆书工具，利用AI对超长的小说内容进行任意的拆解，比如“剧情压缩”，“世界地图归纳”，“战斗描述拆解”，“指定相似剧情查找”等。



## 目录结构

````text
NovelExtractor/
├─ run_ui.py                    # 启动图形界面
├─ requirements.txt             # 依赖
├─ configs/
│  └─ config.json               # 模型配置
├─ app/
│  ├─ query.py                  # 批量 LLM 查询逻辑（并发/批次/断点重续）
│  ├─ novel_pre_processor.py    # 预处理，将整本小说逐章节拆分并保存为txt
│  └─ merge_files.py            # txt文件合并工具
├─ pyqt_ui/
│  ├─ main_window.py            # 主窗体（多标签页）
│  ├─ query_ui.py               # 查询页（利用AI对小说内容进行处理）
│  ├─ merge_files_ui.py         # 合并页
│  ├─ novel_pre_processor_ui.py # 预处理页
│  ├─ reader_ui.py              # 阅读页（对AI生成的内容进行查看）
│  └─ config_ui.py              # 配置页
└─ utils/
   ├─ unified_chat.py           # 多厂商模型统一路由
   ├─ text_processor.py         # 将txt小说逐章节拆分提取到变量中
   ├─ readtxt.py                # 自动编码识别读取
   └─ paths.py                  # 打包/开发模式路径与配置定位
````

厂商兼容：
目前仅实现了OpenAI兼容格式
Gemini 待实现
Anthropic 待实现

## 使用流程

1. 在“配置”页添加/编辑 Provider（如 aliyun、zhipu、moonshot、doubao、siliconflow、openai），填入 `api_key`、`base_url`，添加可用 `models`

2. 在“小说预处理”页：选择整本小说 `.txt`，输出到一个章节目录（自动识别“第X章”并按自然顺序拆分）

   一定要先做，因为query查询页面以一个txt为最小输入单位，内部不会再自动拆分成多个章节

3. 在“查询”页：

   - 选择“输入目录”为步骤 2 生成的章节目录
   - 选择“输出目录”与 Prompt 文件（必须包含 `{input_content}` 占位符）
   - 选择 Provider/Model，设置并发与批次大小，开始查询
   - 结果会生成如 `查询结果_bs30_批次1.txt`、`查询结果_bs30_批次2.txt` …

4. 在“合并文件”页：将多个章节 `.txt` 按末尾编号顺序合并为一个总文档（可选写入文件名分隔）

5. 在“小说阅读”页：打开章节目录或合并后的文本进行浏览、预览与快速编辑（Ctrl+S 保存）