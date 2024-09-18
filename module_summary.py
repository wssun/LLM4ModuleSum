import json
import csv
import os
import re
import shutil


# 去除Java代码中的注释的函数
def remove_comments(java_code):
    pattern = re.compile(r'(\/\*[\s\S]*?\*\/)|(\/\/.*$)', re.MULTILINE)
    return re.sub(pattern, '', java_code)

# 处理指定目录下的所有JSON和CSV文件
def process_files(json_folder, csv_folders, output_folder):
    # 找到所有的JSON文件并排序
    json_files = sorted([os.path.join(json_folder, file) for file in os.listdir(json_folder) if file.endswith('.json')])

    # 检索每个CSV文件夹中的所有CSV文件并排序
    csv_files_per_folder = [
        sorted([os.path.join(csv_folder, file) for file in os.listdir(csv_folder) if file.endswith('.csv')]) for
        csv_folder in csv_folders]

    # 检查每个CSV文件夹中的文件数量是否与JSON文件数量匹配
    if any(len(files) < len(json_files) for files in csv_files_per_folder):
        print("至少一个CSV文件夹中的文件数量少于JSON文件数量，请检查文件夹内容。")
        return

    # 创建输出文件夹
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 处理每个JSON文件
    count=0
    for index, json_path in enumerate(json_files):
        with open(json_path, 'r', encoding='utf-8') as json_file:
            json_data = json.load(json_file)

        # 提取所有Java文件路径
        java_files_paths = [path for path in json_data.keys() if path.endswith('.java')]

        # 读取当前索引的CSV文件中的注释
        comments = [[] for _ in range(4)]
        for i, csv_files in enumerate(csv_files_per_folder):
            csv_file_path = csv_files[index]  # 选择每个文件夹对应的CSV文件
            with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file)
                for row in csv_reader:
                    if len(row) > 1:  # 确保行不为空
                        comments[i].append(row[1])

        # 保存代码和注释到单独的文件
        for idx, file_path in enumerate(java_files_paths):
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as java_file:
                    java_code = java_file.read()
                    cleaned_code = remove_comments(java_code)

                    output_file_path = os.path.join(output_folder, f'file_{count+1}.txt')
                    count+=1
                    with open(output_file_path, 'w', encoding='utf-8') as output_file:
                        output_file.write(f'code: {cleaned_code}\n')
                        for i in range(4):
                            comment = comments[i][idx] if idx < len(comments[i]) else "No comment"
                            output_file.write(f'comment{i + 1}: {comment}\n')

    print(f"代码和注释已分别保存到 {output_folder} 文件夹中")

# 定义处理每个JSON文件的函数
def process_json_file(input_json_path, output_dir, project_name, strip_str = None):
    # 创建输出目录如果它不存在
    os.makedirs(output_dir, exist_ok=True)

    # 读取输入JSON文件
    with open(input_json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 提取所有满足条件的样本
    samples = []
    for file_path, content in data.items():
        if 'test' not in file_path.lower() and content['ent2string'] and content['clazz2contents']:
            samples.append((file_path, content))

    # 确保样本数量大于或等于20
    if len(samples) < 20:
        raise ValueError(f"Not enough samples in {input_json_path} to select 20.")

    # 随机挑选20个样本
    selected_samples = samples

    # 复制文件到指定目录，并生成新的JSON数据
    output_data = {}
    for file_path, content in selected_samples:
        if strip_str:
            file_path = file_path.removeprefix(strip_str)
        # 计算在目标目录中的新路径
        new_path = os.path.join(output_dir, os.path.basename(file_path))

        # 创建目录如果它不存在
        os.makedirs(os.path.dirname(new_path), exist_ok=True)

        # # 复制文件
        # shutil.copy(file_path, new_path)

        # 添加到输出数据中
        output_data[file_path] = content

    # 将新的JSON数据写入输出文件
    output_json_path = os.path.join(output_dir, f'{project_name}.json')
    with open(output_json_path, 'w', encoding='utf-8') as file:
        json.dump(output_data, file, ensure_ascii=False, indent=4)

    print(f'Successfully selected and copied 20 samples to {output_dir}. JSON file generated at {output_json_path}.')

from varsearch import process_all_json_files as process_all_json_files_varsearch
from yasuo import process_all_json_files as process_all_json_files_yasuo
from hmevl import remove_comments

def jsons2full_codes(json_folder, output_folder):
    os.makedirs(json_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    
    result = {}
    
    for f in os.listdir(json_folder):
        with open(f'{json_folder}/{f}', 'r', encoding='utf-8') as file:
            data = json.load(file)
        for file_path, content in data.items():
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as source_file:
                    file_data = source_file.read()
                cleaned_code = remove_comments(file_data)
                result[file_path] = cleaned_code
        with open(f'{output_folder}/{f}', 'w', encoding='utf-8') as file:
            json.dump(result, file, ensure_ascii=False, indent=4)
    
    pass

def get_module_codes(json_prj2selected_main_module2files, json_folder):
    with open(json_prj2selected_main_module2files, 'r', encoding='utf-8') as files:
        prj2selected_main_module2files = json.load(files)
    
    full_code_jsons = os.listdir(json_folder)
    prj2main_module2file2full_code = {}
    for prj, selected_main_module2file in prj2selected_main_module2files.items():
        full_code_json = [f for f in full_code_jsons if prj in f][0]
        full_code_json = f'{json_folder}/{full_code_json}'
        with open(full_code_json, 'r', encoding='utf-8') as file:
            full_code_data = json.load(file)
        full_code_data = {k.replace('\\', '/'): v for k, v in full_code_data.items()}
        for main_module, files in selected_main_module2file.items():
            prj2main_module2file2full_code.setdefault(prj, {}).setdefault(main_module, {})
            for file in files:
                if file in full_code_data:
                    file_rel_path = file.removeprefix(f'projects/{prj}/')
                    prj2main_module2file2full_code[prj][main_module][file_rel_path] = full_code_data[file]
            pass
    with open('data/prj2main_module2file2full_code.json', 'w', encoding='utf-8') as file:
        json.dump(prj2main_module2file2full_code, file, ensure_ascii=False, indent=4)
    pass

def get_module_codes_compressed(json_prj2selected_main_module2files, json_folder):
    with open(json_prj2selected_main_module2files, 'r', encoding='utf-8') as files:
        prj2selected_main_module2files = json.load(files)
    compressed_code_jsons = os.listdir(json_folder)
    prj2main_module2file2compressed_code = {}
    for prj, selected_main_module2file in prj2selected_main_module2files.items():
        compressed_code_json = [f for f in compressed_code_jsons if prj in f][0]
        compressed_code_json = f'{json_folder}/{compressed_code_json}'
        with open(compressed_code_json, 'r', encoding='utf-8') as file:
            compressed_code_data = json.load(file)
        compressed_code_data = {k.replace('\\', '/'): v for k, v in compressed_code_data.items()}
        for main_module, files in selected_main_module2file.items():
            prj2main_module2file2compressed_code.setdefault(prj, {}).setdefault(main_module, {})
            for file in files:
                if file not in compressed_code_data:
                    continue
                if not os.path.exists(file):
                    print(f'File not found: {file}')
                    continue
                with open(file, 'r', encoding='utf-8') as source_file:
                    file_code = source_file.read()
                file_code = remove_comments(file_code)
                
                package_pattern = r'^\s*package\s+[\w\.]+;\s*$'
                package_statement = re.search(package_pattern, file_code, re.MULTILINE)
                package_statement = package_statement.group() if package_statement else ''
                package_statement = package_statement.strip()
                
                import_pattern = r'^\s*import\s+[\w\.\*]+;\s*$'
                import_statements = re.findall(import_pattern, file_code, re.MULTILINE)
                import_statements = [statement.strip() for statement in import_statements]
                
                compressed_code_body = compressed_code_data[file]
                
                compressed_code_final = package_statement + '\n\n' + '\n'.join(import_statements) + '\n\n' + compressed_code_body
                file_rel_path = file.removeprefix(f'projects/{prj}/')
                prj2main_module2file2compressed_code[prj][main_module][file_rel_path] = compressed_code_final
            pass
    with open('data/prj2main_module2file2compressed_code.json', 'w', encoding='utf-8') as file:
        json.dump(prj2main_module2file2compressed_code, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    
    if True:
        os.makedirs('data/json_tmp', exist_ok=True)
        for f in os.listdir('und_project'):
            prj_name = f.rsplit('.',1)[0][13:]
            process_json_file(f'und_project/{f}', 'data/json_tmp', prj_name, strip_str=f'D:\\')
    if True:
        process_all_json_files_varsearch('data/json_tmp', 'data/json_base')
        
    if True:
        process_all_json_files_yasuo('data/json_base', 'data/json_intermidiate', 'data/json_compressed_code')

    if True:
        jsons2full_codes('data/json_base', 'data/json_full_codes')
    
    if True:
        get_module_codes('data/prj2selected_main_module2file.json', 'data/json_full_codes')
        
    if True:
        get_module_codes_compressed('data/prj2selected_main_module2file.json', 'data/json_compressed_code')
    pass