"""
统一文本文件读取模块
提供自动编码检测和路径处理功能
"""

import os
from typing import Optional


def read_text_file(file_path: str, base_dir: Optional[str] = None) -> str:
    """
    读取文本文件，自动处理编码问题和路径解析
    
    Args:
        file_path: 文件路径（可以是相对路径或绝对路径）
        base_dir: 基础目录，如果提供则相对路径会基于此目录解析
        
    Returns:
        文件内容字符串
        
    Raises:
        FileNotFoundError: 文件不存在
        Exception: 其他读取错误
    """
    # 处理路径
    if base_dir is not None and not os.path.isabs(file_path):
        # 如果提供了基础目录且文件路径是相对路径，则基于基础目录解析
        resolved_path = os.path.join(base_dir, file_path)
    elif not os.path.isabs(file_path):
        # 如果是相对路径且没有提供基础目录，则基于当前工作目录解析
        resolved_path = os.path.join(os.getcwd(), file_path)
    else:
        # 绝对路径直接使用
        resolved_path = file_path
    
    # 标准化路径
    resolved_path = os.path.normpath(resolved_path)
    
    # 检查文件是否存在
    if not os.path.exists(resolved_path):
        raise FileNotFoundError(f"文件不存在: {resolved_path}")
    
    encodings_to_try = ["utf-8", "gbk", "gb2312"]
    
    for encoding in encodings_to_try:
        try:
            with open(resolved_path, "r", encoding=encoding) as f:
                content = f.read()
            print(f"成功读取文件 ({encoding}): {resolved_path}")
            return content
        except UnicodeDecodeError:
            continue
            
    # 如果所有编码都失败，尝试使用错误处理
    try:
        with open(resolved_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        print(f"成功读取文件 (UTF-8 with errors ignored): {resolved_path}")
        return content
    except Exception as e:
        raise Exception(f"无法使用所有指定编码读取文件 {resolved_path}: {str(e)}")
