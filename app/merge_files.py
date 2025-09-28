import os
import re

def merge_files_by_number(input_dir: str, output_file: str = "merged_output.txt", show_name: bool = False) -> None:
    """
    按编号顺序合并目录中的所有txt文件
    
    Args:
        input_dir: 输入目录路径
        output_file: 输出文件名（默认为merged_output.txt）
        show_name: 是否在合并时显示文件名（默认为False）
    """
    # 获取目录中所有的txt文件
    files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]
    
    # 按文件名中的数字排序
    def extract_number(filename):
        # 专门提取后缀数字
        match = re.search(r'_(\d+)\.txt$', filename)
        return int(match.group(1)) if match else 0
    
    files.sort(key=extract_number)
    
    # 合并文件
    merged_count = 0
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for filename in files:
            filepath = os.path.join(input_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as infile:
                content = infile.read().strip()  # 去除首尾空白
                if content:  # 只写入非空内容

                    if show_name:
                        # ✅ 新增：写入文件名 + 分隔线
                        outfile.write("\n\n"+"-" * len(filename))  # 分隔线长度匹配文件名
                        outfile.write(f"{filename}\n\n")
                    else:
                        outfile.write('\n\n')  # 每个文件后加两个换行，确保明显分隔
                    
                    outfile.write(content)
                    
                    merged_count += 1
    
    print(f"已处理 {len(files)} 个文件，实际合并了 {merged_count} 个非空文件到 {output_file}")
    print(f"章节范围: 第{extract_number(files[0])}章 到 第{extract_number(files[-1])}章")

def main():
    import sys
    import argparse
    
    # 创建参数解析器
    parser = argparse.ArgumentParser(description='按编号顺序合并目录中的txt文件')
    parser.add_argument('input_dir',  help='输入目录路径')
    parser.add_argument('-o', '--output',help='输出文件名')
    parser.add_argument('--show_name', action='store_true', help='合并文件时是否显示文件名')    
    args = parser.parse_args()
    
    # 检查输入目录是否存在
    if not os.path.exists(args.input_dir):
        print(f"错误: 目录 '{args.input_dir}' 不存在")
        sys.exit(1)
    
    merge_files_by_number(args.input_dir, args.output, args.show_name)

if __name__ == "__main__":
    main()