"""
预处理一部小说，将它逐章节拆分为txt供后续使用
"""
import os
import argparse


from utils.text_processor import TextProcessor
from utils.readtxt import read_text_file


if __name__ == "__main__":
 
    # 创建参数解析器
    parser = argparse.ArgumentParser(description='按编号顺序合并目录中的txt文件')
    parser.add_argument('-i', '--input_path', help='输入文件路径')
    parser.add_argument('-o', '--output_path', help='输出文件路径')    
    args = parser.parse_args()

    processor = TextProcessor()
    test_text = read_text_file(args.input_path)
    chapters = processor.split_chapters(test_text)
    
    # 创建输出目录
    os.makedirs(args.output_path, exist_ok=True)
    
    # 保存每个章节为独立txt文件
    for chapter in chapters:
        # 生成文件名：第X章_标题_X.txt
        chapter_title = f"第{chapter.number}章_{chapter.title.replace(' ', '').replace('　', '')}"
        filename = f"{chapter_title}_{chapter.number}.txt"
        # 清理非法字符
        filename = "".join(c for c in filename if c not in r'\/:*?"<>|')
        
        # 保存文件
        output_file = os.path.join(args.output_path, filename)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"{chapter_title}\n\n{chapter.content}")
        print(f"保存章节: {filename}")
    
    print(f"完成！共保存 {len(chapters)} 个章节文件")
