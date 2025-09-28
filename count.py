import os

def count_lines_in_file(file_path):
    """统计单个文件的行数"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for line in f)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0

class DirectoryNode:
    """目录节点类，用于构建目录树"""
    def __init__(self, path, name):
        self.path = path
        self.name = name
        self.children = []  # 子目录
        self.files = []     # 当前目录下的文件
        self.local_lines = 0  # 当前目录下文件的行数
        self.total_lines = 0  # 当前目录及所有子目录的总行数

def build_directory_tree(start_dir):
    """构建目录树结构"""
    # 创建根节点
    root_node = DirectoryNode(start_dir, os.path.basename(start_dir))
    
    # 使用栈来构建树结构
    stack = [(start_dir, root_node)]
    
    while stack:
        current_dir, current_node = stack.pop()
        
        try:
            items = os.listdir(current_dir)
        except PermissionError:
            continue
            
        # 分离文件和目录
        dirs = []
        files = []
        
        for item in items:
            item_path = os.path.join(current_dir, item)
            if os.path.isdir(item_path):
                dirs.append(item)
            else:
                files.append(item)
        
        # 处理当前目录的文件
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(current_dir, file)
                lines = count_lines_in_file(file_path)
                current_node.files.append((file, lines))
                current_node.local_lines += lines
        
        # 处理子目录
        for dir_name in dirs:
            dir_path = os.path.join(current_dir, dir_name)
            child_node = DirectoryNode(dir_path, dir_name)
            current_node.children.append(child_node)
            stack.append((dir_path, child_node))
    
    return root_node

def calculate_cumulative_lines(node):
    """递归计算每个节点的累加行数"""
    node.total_lines = node.local_lines
    
    for child in node.children:
        calculate_cumulative_lines(child)
        node.total_lines += child.total_lines
    
    return node.total_lines

def print_directory_tree(node, indent=0, is_last=True, prefix=""):
    """递归打印目录树结构"""
    # 计算当前节点的缩进和前缀
    if indent > 0:
        if is_last:
            current_prefix = prefix + "└── "
            next_prefix = prefix + "    "
        else:
            current_prefix = prefix + "├── "
            next_prefix = prefix + "│   "
    else:
        current_prefix = ""
        next_prefix = ""
    
    # 打印当前目录
    if node.total_lines > 0:  # 只显示有代码的目录
        print(f"{current_prefix}{node.name}/ ({node.total_lines} lines)")
    
    # 打印当前目录下的文件
    for i, (file_name, lines) in enumerate(node.files):
        if i == len(node.files) - 1 and not node.children:
            file_prefix = prefix + "    " if indent > 0 else "    "
            print(f"{file_prefix}└── {file_name} ({lines} lines)")
        else:
            file_prefix = prefix + "│   " if indent > 0 else "│   "
            print(f"{file_prefix}├── {file_name} ({lines} lines)")
    
    # 递归打印子目录
    for i, child in enumerate(node.children):
        is_last_child = (i == len(node.children) - 1)
        print_directory_tree(child, indent + 1, is_last_child, next_prefix)

def main():
    # 获取当前工作目录
    current_directory = os.getcwd()
    print(f"Counting lines in .py files starting from: {current_directory}")
    print("=" * 70)
    
    # 构建目录树
    root_node = build_directory_tree(current_directory)
    
    # 计算累加行数
    total_lines = calculate_cumulative_lines(root_node)
    
    # 打印目录树
    print_directory_tree(root_node)
    
    print("=" * 70)
    print(f"Total lines in all .py files: {total_lines}")

if __name__ == "__main__":
    main()