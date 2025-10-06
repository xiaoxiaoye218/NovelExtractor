import os
import re
import glob
import asyncio
import threading
import sys
import argparse
import json
from typing import List, Optional
from pathlib import Path


from utils.unified_chat import ModelRouter

"""
使用LLM对小说章节进行批量的Query-Answer操作
支持并发控制和断点重续
"""
class Query:
    def __init__(self, input_path:str, output_path:str,provider_id:str, model_id:str,concurrent:int,batch_size:int,prompt_path:str,name_prefix:str,start_pos:Optional[int]=None,end_pos:Optional[int]=None):
        self.input_path = input_path
        self.output_path = output_path
        self.concurrent = concurrent
        self.batch_size = batch_size
        self.prompt_path = prompt_path
        self.name_prefix = name_prefix
        self.provider_id = provider_id
        self.model_id = model_id
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.router = ModelRouter()

        # 并发状态与取消控制
        self._active = 0
        self._active_lock = asyncio.Lock()
        self._cancel_event = threading.Event()

    def request_cancel(self):
        """由外部（如UI）调用，发出中止请求。
        已开始进入router调用的批次不强行中断；尚未进入调用的批次将被跳过。
        """
        self._cancel_event.set()

    def clear_cancel_flag(self):
        """清理中止标志，避免影响下次运行。"""
        self._cancel_event.clear()

    def _load_prompt_template(self) -> str:
        try:
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                prompt_template = f.read().strip()
        except Exception as e:
            raise RuntimeError(f"读取 Prompt 文件 '{self.prompt_path}' 时发生未知错误: {str(e)}")
        return prompt_template
    
    async def _call_llm(self,prompt:str)->str:
        try:
            # 使用LLMrouter调用API
            response = await self.router.chat(
                model_name=self.model_id,
                provider=self.provider_id,
                message=prompt
            )
            # 检查响应是否成功
            if response.get("success", True) and "content" in response:
                return response["content"]
            else:
                error_msg = response.get("error", "未知错误")
                raise Exception(f"API调用失败: {error_msg}")

        except Exception as e:
            raise Exception(f"调用{self.provider_id}/{self.model_id} API失败: {str(e)}")

    def _get_existing_results(self) -> set:
        """
        获取已存在的处理结果文件信息（批次号从1开始）

        Returns:
            set: 已处理批次数集合
        """
        pattern = os.path.join(self.output_path, f"{self.name_prefix}_bs{self.batch_size}_批次*.txt")
        existing_files = glob.glob(pattern)

        existing = set()
        for file_path in existing_files:
            filename = os.path.basename(file_path)
            match = re.search(rf"{re.escape(self.name_prefix)}_bs{self.batch_size}_批次(\d+)\.txt", filename)
            if match:
                batch_num = int(match.group(1))
                existing.add(batch_num)

        return existing

    def _natural_sort_files(self, files: List[str]) -> List[str]:
        """
        对文件列表进行自然排序，只提取最后的下划线后面的数字进行排序
        例如：第140章__不懂规矩？_140.txt → 提取140，章节提取_140.txt → 提取140
        """
        def natural_key(filename):
            # 提取文件名中的数字
            basename = os.path.basename(filename)
            
            # 只匹配最后的下划线后面的数字（如_140.txt中的140）
            match = re.search(r'_(\d+)\.txt$', basename)
            if match:
                return int(match.group(1))
            
            # 如果没有找到最后的下划线数字，按文件名排序
            return (float('inf'), basename)
        
        return sorted(files, key=natural_key)

    async def process_query(self):
        """
        对input_path下的所有txt文件进行处理，每次处理batch_size个文件，
        分别调用_process_with_semaphore处理
        """
        try:
            # 获取所有txt文件
            txt_files = glob.glob(os.path.join(self.input_path, "*.txt"))
            if not txt_files:
                print(f"在 {self.input_path} 中没有找到txt文件")
                return

            # 按自然排序对文件进行排序
            txt_files = self._natural_sort_files(txt_files)

            # 应用起始和终止位置过滤（左闭右闭，以1为开始）
            if self.start_pos is not None or self.end_pos is not None:
                start_idx = (self.start_pos - 1) if self.start_pos is not None else 0
                end_idx = self.end_pos if self.end_pos is not None else len(txt_files)
                # 确保索引在有效范围内
                start_idx = max(0, start_idx)
                end_idx = min(len(txt_files), end_idx)
                if start_idx >= end_idx:
                    print(f"起始位置 {self.start_pos} 大于等于终止位置 {self.end_pos}，没有文件需要处理")
                    return
                txt_files = txt_files[start_idx:end_idx]
                print(f"根据位置范围 [{self.start_pos or 1}, {self.end_pos or len(txt_files)}] 过滤后，找到 {len(txt_files)} 个txt文件")
            else:
                print(f"总共找到 {len(txt_files)} 个txt文件")

            if self._cancel_event.is_set():
                print("收到中止请求，未开始创建任务，直接退出")
                return

            # 检查已存在的批次
            existing = self._get_existing_results()

            # 计算批次信息（批次号从1开始）
            batch_size = int(self.batch_size)
            total_batches = (len(txt_files) + batch_size - 1) // batch_size

            missing_batches = [i+1 for i in range(total_batches) if i+1 not in existing]

            if not missing_batches:
                print("所有批次都已完成，无需重新处理")
                return

            print(f"需要处理 {len(missing_batches)} 个批次")

            # 使用信号量控制并发数
            semaphore = asyncio.Semaphore(self.concurrent)

            # 准备异步任务
            tasks = []
            for batch_num in missing_batches:
                if self._cancel_event.is_set():
                    print("收到中止请求，停止创建剩余任务")
                    break
                # 批次号从1开始，计算文件索引时要减1
                # 输入批次和处理批次的顺序是对应上的，是从头开始按顺序读
                start_idx = (batch_num - 1) * batch_size
                end_idx = min(start_idx + batch_size, len(txt_files))
                batch_files = txt_files[start_idx:end_idx]

                task = asyncio.create_task(self._process_batch_with_semaphore(semaphore, batch_files, batch_num))
                tasks.append(task)

            if not tasks:
                print("没有任务需要执行或已被中止")
                return

            print(f"开始并发处理 {len(tasks)} 个批次（并发数: {self.concurrent}）...")

            # 直接执行所有任务
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 处理结果
            for i, result in enumerate(results):
                batch_no = missing_batches[i]
                if isinstance(result, Exception):
                    print(f"批次 {batch_no} 处理失败: {str(result)}")
                elif isinstance(result, str) and result == "cancelled":
                    #print(f"批次 {batch_no} 已跳过（收到中止请求）")
                    pass
                else:
                    print(f"批次 {batch_no} 处理成功")
        finally:
            # 清理取消标志，避免影响下次运行
            # 能确保无论函数如何退出（正常返回、异常抛出、或中途被取消），_cancel_event.clear() 都会被执行
            self._cancel_event.clear()

    async def _process_batch_with_semaphore(self, semaphore: asyncio.Semaphore, batch_files: List[str], batch_num: int) -> str:
        """
        使用信号量控制并发处理单个批次

        Args:
            semaphore: 信号量，用于控制并发数
            batch_files: 该批次要处理的文件列表
            batch_num: 批次号

        Returns:
            AI生成的结果文本
        """
        # 如果已经请求中止且该批次尚未开始处理，直接跳过
        if self._cancel_event.is_set():
            return "cancelled"

        async with semaphore:
            # 更新活跃任务数并打印诊断日志
            async with self._active_lock:
                self._active += 1
                active = self._active
            print(f"[active {active}/{self.concurrent}] 正在处理批次 {batch_num}")

            try:

                # 读取批次中的所有文件内容
                batch_content = ""
                for file_path in batch_files:
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read().strip()
                            if content:
                                # 添加文件名作为标识
                                filename = os.path.basename(file_path)
                                batch_content += f"\n=== {filename} ===\n{content}\n"
                    except Exception as e:
                        print(f"读取文件 {file_path} 失败: {str(e)}")
                        continue

                if not batch_content:
                    raise Exception("批次中没有有效的文件内容")

                # 加载prompt模板
                prompt_template = self._load_prompt_template()

                # 替换prompt模板中的占位符
                prompt = prompt_template.replace("{input_content}", batch_content)


                # 调用LLM API
                result = await self._call_llm(prompt)

                # 保存结果到文件
                output_file = os.path.join(self.output_path, f"{self.name_prefix}_bs{self.batch_size}_批次{batch_num}.txt")
                os.makedirs(self.output_path, exist_ok=True)

                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(result)

                # 打印成功日志
                async with self._active_lock:
                    active = self._active
                print(f"[active {active}/{self.concurrent}] 批次 {batch_num} 成功完成")

                return result

            except Exception as e:
                async with self._active_lock:
                    active = self._active
                print(f"[active {active}/{self.concurrent}] 批次 {batch_num} 失败: {str(e)}")
                raise

            finally:
                # 释放活跃计数
                async with self._active_lock:
                    self._active -= 1
                    active = self._active
                print(f"[active {active}/{self.concurrent}] 批次 {batch_num} 释放信号量")


import time
import argparse
from typing import List

if __name__ == "__main__":
    # 开始计时
    start_time = time.perf_counter() 
    
    parser = argparse.ArgumentParser(description="批量Query-Answer处理工具")
    parser.add_argument("--input_path", help="输入目录，包含多个txt文件")
    parser.add_argument("--output_path", help="输出目录，保存处理后的txt文件")
    parser.add_argument("--provider", help="提供商ID，如zhipu、aliyun等（默认aliyun）")
    parser.add_argument("--model",  help="模型ID，如glm-4.5、qwen3-next-80b-a3b-instruct等（默认qwen3-next-80b-a3b-instruct）")
    parser.add_argument("--concurrent", type=int, default=1, help="异步并发数量")
    parser.add_argument("--batch_size", default="10", help="一个批次的大小")
    parser.add_argument("--prompt_path",  help="LLM调用指令文件路径，需包含{input_content}占位符")
    parser.add_argument("--name_prefix", default="查询结果", help="输出文件名前缀")
    parser.add_argument("--start_pos", type=int, default=None, help="起始位置（从1开始）")
    parser.add_argument("--end_pos", type=int, default=None, help="终止位置")
    args = parser.parse_args()
    
    try:
        # 初始化Query处理器
        query_processor = Query(
            input_path=args.input_path,
            output_path=args.output_path,
            provider_id=args.provider,
            model_id=args.model,
            concurrent=args.concurrent,
            batch_size=args.batch_size,
            prompt_path=args.prompt_path,
            name_prefix=args.name_prefix,
            start_pos=args.start_pos,
            end_pos=args.end_pos
        )
        
        # 开始处理
        asyncio.run(query_processor.process_query())
        
    except Exception as e:
        # 计时结束（处理过程或参数解析出错时）
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"处理过程发生错误，总耗时: {elapsed_time:.6f} 秒")
        print(f"错误信息: {str(e)}")
        sys.exit(1)
    
    # 计时结束（处理成功时）
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"所有任务处理完成，总耗时: {elapsed_time:.6f} 秒")


"""
示例用法:
# 处理所有文件
python query.py \
    --input_path "../wyft/chatper" \
    --output_path "../outputs/query_results" \
    --prompt_path "../prompts/查询prompt.txt" \
    --batch_size 10 \
    --concurrent 20 \
    --name_prefix "分析结果"

# 只处理第1到第50个文件（左闭右闭，以1为开始）
python query.py \
    --input_path "../wyft/chatper" \
    --output_path "../outputs/query_results" \
    --prompt_path "../prompts/查询prompt.txt" \
    --batch_size 10 \
    --concurrent 20 \
    --name_prefix "分析结果" \
    --start_pos 1 \
    --end_pos 50

这将:
1. 读取 ../wyft/chatper 目录下的所有txt文件（按自然排序：第1章、第2章...第10章）
2. 每10个文件为一个批次进行处理
3. 输出文件名为 "分析结果_批次1.txt", "分析结果_批次2.txt" 等（批次号从1开始）
4. 并发数为20，支持断点重续
5. 支持指定起始和终止位置，只处理指定范围内的文件
"""
    
    
    
    
   
