import json
import os
import random
import shutil

input_json_dir = 'und_project'
output_root_dir = 'project_cases'

os.makedirs(output_root_dir, exist_ok=True)

json_files = [f for f in os.listdir(input_json_dir) if f.endswith('.json')]

def process_json_file(input_json_path, output_dir, project_name):
    os.makedirs(output_dir, exist_ok=True)

    with open(input_json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    samples = []
    for file_path, content in data.items():
        if 'test' not in file_path.lower() and content['ent2string'] and content['clazz2contents']:
            samples.append((file_path, content))

    if len(samples) < 20:
        raise ValueError(f"Not enough samples in {input_json_path} to select 20.")

    selected_samples = random.sample(samples, 20)

    output_data = {}
    for file_path, content in selected_samples:
        new_path = os.path.join(output_dir, os.path.basename(file_path))

        os.makedirs(os.path.dirname(new_path), exist_ok=True)

        shutil.copy(file_path, new_path)

        output_data[file_path] = content

    output_json_path = os.path.join(output_dir, f'{project_name}.json')
    with open(output_json_path, 'w', encoding='utf-8') as file:
        json.dump(output_data, file, ensure_ascii=False, indent=4)

    print(f'Successfully selected and copied 20 samples to {output_dir}. JSON file generated at {output_json_path}.')

for json_file in json_files:
    input_json_path = os.path.join(input_json_dir, json_file)
    project_name = os.path.splitext(json_file)[0]
    output_dir = os.path.join(output_root_dir, project_name)
    try:
        process_json_file(input_json_path, output_dir, project_name)
    except ValueError as e:
        print(e)
