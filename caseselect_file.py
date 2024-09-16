import json
import os
import random
import shutil

# 定义输入JSON文件所在的目录和输出根目录
input_json_dir = 'und_project'
output_root_dir = 'project_cases'

# 创建输出根目录如果它不存在
os.makedirs(output_root_dir, exist_ok=True)

# 获取目录中所有JSON文件
json_files = [f for f in os.listdir(input_json_dir) if f.endswith('.json')]

# 定义处理每个JSON文件的函数
def process_json_file(input_json_path, output_dir, project_name):
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
    selected_samples = random.sample(samples, 20)

    # 复制文件到指定目录，并生成新的JSON数据
    output_data = {}
    for file_path, content in selected_samples:
        # 计算在目标目录中的新路径
        new_path = os.path.join(output_dir, os.path.basename(file_path))

        # 创建目录如果它不存在
        os.makedirs(os.path.dirname(new_path), exist_ok=True)

        # 复制文件
        shutil.copy(file_path, new_path)

        # 添加到输出数据中
        output_data[file_path] = content

    # 将新的JSON数据写入输出文件
    output_json_path = os.path.join(output_dir, f'{project_name}.json')
    with open(output_json_path, 'w', encoding='utf-8') as file:
        json.dump(output_data, file, ensure_ascii=False, indent=4)

    print(f'Successfully selected and copied 20 samples to {output_dir}. JSON file generated at {output_json_path}.')

# 遍历每个JSON文件并处理
for json_file in json_files:
    input_json_path = os.path.join(input_json_dir, json_file)
    project_name = os.path.splitext(json_file)[0]
    output_dir = os.path.join(output_root_dir, project_name)
    try:
        process_json_file(input_json_path, output_dir, project_name)
    except ValueError as e:
        print(e)
