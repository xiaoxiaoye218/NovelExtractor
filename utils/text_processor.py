"""
文本预处理模块
处理输入文本，进行章节分割和格式化
"""

import re
import os
import sys
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from .readtxt import read_text_file


@dataclass
class Chapter:
    """章节数据结构"""
    number: int         #章节编号（阿拉伯数字），如 1, 2, 3...
    title: str          #章节标题（不含“第X章”前缀），如 “初遇”、“决战紫禁之巅”从正则匹配中提取，已去除前后空白
    content: str        #章节正文内容（不包含标题行）
    word_count: int


class TextProcessor:
    """文本预处理器"""
    
    def __init__(self):
        # 章节标题的正则表达式模式（"第"字前面可以有其他内容）
        self.chapter_pattern = r'.*第[一二三四五六七八九十百千万零\d]+章[：:\s]*(.*)$'
        
        # 数字转换映射
        self.chinese_numbers = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '百': 100, '千': 1000, '万': 10000, '零': 0
        }
    
    def extract_chapter_number(self, chapter_title: str) -> int:
        """
        从章节标题中提取章节号
        
        Args:
            chapter_title: 章节标题
            
        Returns:
            章节号
        """
        # 提取数字部分
        number_match = re.search(r'第([一二三四五六七八九十百千万零\d]+)章', chapter_title)
        if not number_match:
            return 0
        
        number_str = number_match.group(1)
        
        # 如果是阿拉伯数字，直接转换
        if number_str.isdigit():
            return int(number_str)
        
        # 转换中文数字
        return self.chinese_to_arabic(number_str)
    
    def chinese_to_arabic(self, chinese_num: str) -> int:
        """
        将中文数字转换为阿拉伯数字

        Args:
            chinese_num: 中文数字字符串

        Returns:
            阿拉伯数字
        """
        if not chinese_num:
            return 0

        # 如果已经是阿拉伯数字，直接返回
        if chinese_num.isdigit():
            return int(chinese_num)

        # 中文数字映射表
        num_map = {
            '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '百': 100, '千': 1000, '万': 10000
        }

        result = 0
        temp = 0

        for char in chinese_num:
            if char in num_map:
                num = num_map[char]
                if num >= 10:
                    if num == 10 and temp == 0:
                        temp = 1
                    temp *= num
                    if num >= 100:
                        result += temp
                        temp = 0
                else:
                    temp += num
            elif char.isdigit():
                temp = temp * 10 + int(char)

        return result + temp
    
    def split_chapters(self, text: str) -> List[Chapter]:
        """
        将文本分割为章节
        
        Args:
            text: 输入文本
            
        Returns:
            章节列表
        """
        # 标准化换行符
        text = re.sub(r'\r\n', '\n', text)
        
        chapters = []
        chapter_dict = {}  # 用于存储章节号到章节对象的映射
        
        # 查找所有章节标题行
        lines = text.split('\n')
        chapter_indices = []
        
        for i, line in enumerate(lines):
            if re.match(self.chapter_pattern, line):
                chapter_indices.append(i)
        
        if not chapter_indices:
            # 如果没有找到章节标记，将整个文本作为一章
            return [Chapter(
                number=1,
                title="全文",
                content=text,
                word_count=len(text)
            )]
        
        # 分割章节
        for i, idx in enumerate(chapter_indices):
            chapter_title_line = lines[idx]
            next_idx = chapter_indices[i + 1] if i + 1 < len(chapter_indices) else len(lines)
            
            # 提取章节标题
            title_match = re.match(self.chapter_pattern, chapter_title_line)
            if title_match:
                chapter_title = title_match.group(1).strip() if title_match.group(1) else ""
                chapter_number = self.extract_chapter_number(chapter_title_line)
                
                # 获取章节内容（不包括标题行）
                content_lines = lines[idx + 1:next_idx]
                content = '\n'.join(content_lines)
                
                # 检查是否已存在同名章节
                if chapter_number in chapter_dict:
                    # 如果已存在，追加内容到现有章节
                    existing_chapter = chapter_dict[chapter_number]
                    existing_chapter.content += '\n' + content
                    existing_chapter.word_count += len(content)
                else:
                    # 创建新章节对象
                    chapter = Chapter(
                        number=chapter_number,
                        title=chapter_title,
                        content=content,
                        word_count=len(content)
                    )
                    
                    chapters.append(chapter)
                    chapter_dict[chapter_number] = chapter
        
        # 按章节号排序
        chapters.sort(key=lambda x: x.number)
        
        return chapters
    
    def get_text_statistics(self, chapters: List[Chapter]) -> Dict[str, any]:
        """
        获取文本统计信息
        
        Args:
            chapters: 章节列表
            
        Returns:
            统计信息字典
        """
        total_words = sum(chapter.word_count for chapter in chapters)
        avg_words_per_chapter = total_words / len(chapters) if chapters else 0
        
        return {
            "total_chapters": len(chapters),
            "total_words": total_words,
            "avg_words_per_chapter": int(avg_words_per_chapter),
            "first_chapter": chapters[0].number if chapters else 0,
            "last_chapter": chapters[-1].number if chapters else 0
        }
    
    def format_chapters_for_llm(self, chapters: List[Chapter], 
                               start_idx: int = 0, end_idx: Optional[int] = None) -> str:
        """
        将章节格式化为适合LLM处理的文本
        
        Args:
            chapters: 章节列表
            start_idx: 开始索引
            end_idx: 结束索引
            
        Returns:
            格式化后的文本
        """
        if end_idx is None:
            end_idx = len(chapters)
        
        formatted_text = ""
        for i in range(start_idx, min(end_idx, len(chapters))):
            chapter = chapters[i]
            # 处理第0章的特殊情况
            if chapter.number == 0:
                formatted_text += f"\n序章 {chapter.title}\n"
            else:
                formatted_text += f"\n第{chapter.number}章 {chapter.title}\n"
            formatted_text += f"{chapter.content}\n"
            formatted_text += "-" * 50 + "\n"
        
        return formatted_text


# 测试代码
if __name__ == "__main__":
    processor = TextProcessor()
    
    # 测试文本处理
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "../novels/wyft.txt")
    output_path = os.path.join(script_dir, "wyft_output.txt")
    
    # 使用统一的文本读取函数
    test_text = read_text_file(file_path)
    
    chapters = processor.split_chapters(test_text)
    stats = processor.get_text_statistics(chapters)
    
    print("文本统计信息:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 输出处理后的文本
    formatted_text = processor.format_chapters_for_llm(chapters)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(formatted_text)
