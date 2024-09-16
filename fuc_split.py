import json
import os

def load_json(file_path):
    # 读取JSON文件并加载为Python字典
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def split_functions(data):
    result = {}

    for file_path, content in data.items():
        functions = content['clazz2contents']['class']['functions']
        variables = content['clazz2contents']['class']['variables']
        ent2string = content['ent2string']
        func_func_dependencies = content['func_func_dependencies']
        func_var_dependencies = content['func_var_dependencies']

        # 创建一个字典来存储函数代码块
        func_code_blocks = {}
        for func in functions:
            if func in ent2string:
                func_code_blocks[func] = ent2string[func]
                print(f"已添加函数 {func} 到 func_code_blocks")
            else:
                print(f"警告: 在 ent2string 中未找到函数 {func}")

        # 将变量定义添加到需要它们的函数的开头
        for dep in func_var_dependencies:
            func = dep['src']
            var = dep['dst']
            if var in ent2string:
                var_def = ent2string[var]
                if func in func_code_blocks:
                    func_code_blocks[func] = var_def + "\n" + func_code_blocks[func]
                    print(f"已添加变量 {var} 到函数 {func}")
                else:
                    print(f"警告: 在 func_code_blocks 中未找到函数 {func}")
            else:
                print(f"警告: 在 ent2string 中未找到变量 {var}")

        # 将函数与其路径一起存储
        result[file_path] = func_code_blocks

    return result

def save_to_json(output_path, data):
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"结果已保存到 {output_path}")

def process_directory(input_dir, output_dir):
    # 创建输出目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            input_file_path = os.path.join(input_dir, filename)
            project_name = os.path.splitext(filename)[0]  # 使用文件名（不带扩展名）作为项目名称
            output_file_path = os.path.join(output_dir, f"{project_name}_processed.json")

            print(f"正在处理文件 {input_file_path}...")

            print("正在从输入文件加载数据...")
            data = load_json(input_file_path)
            print("数据加载成功。")

            print("正在拆分函数...")
            result = split_functions(data)
            print("函数拆分成功。")

            print("正在将结果保存到输出文件...")
            save_to_json(output_file_path, result)
            print(f"文件 {filename} 处理完成，结果已保存到 {output_file_path}。")

if __name__ == "__main__":
    input_dir = 'project_cases/json'  # 输入目录路径
    output_dir = 'project_cases/func_split'  # 输出目录路径

    process_directory(input_dir, output_dir)
