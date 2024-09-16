import json
import os
import re

# 第一部分代码：处理 JSON 文件，提取变量和函数定义

def process_json_file_step1(json_file_path, output_dir):
    # Load JSON data
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    result = {}

    # Iterate through each file in the JSON data
    for file_path, file_info in data.items():
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            continue

        # Initialize the result string for the current file
        result_string = ""

        # Check if file_info is a dictionary
        if isinstance(file_info, dict):
            # Process variables
            class_info = file_info.get('clazz2contents', {}).get('class', {})
            ent2string = file_info.get('ent2string', {})

            for variable in class_info.get('variables', []):
                # Get the variable definition from ent2string
                if variable in ent2string:
                    result_string += ent2string[variable] + "\n"
                else:
                    print(f"Variable {variable} not found in ent2string.")

            # Process functions
            for function in class_info.get('functions', []):
                # Normalize function names
                normalized_function = function.strip()
                # Get the function definition from ent2string
                if normalized_function in ent2string:
                    # Extract function signature (first line) and closing bracket (last line)
                    func_lines = ent2string[normalized_function].strip().split('\n')
                    if len(func_lines) > 0:
                        first_line = func_lines[0].strip()  # Get the first line

                        # Find the index of the opening curly brace '{'
                        opening_brace_index = first_line.find('{')
                        if opening_brace_index != -1:
                            function_signature = first_line[:opening_brace_index].strip()
                        else:
                            function_signature = first_line

                        # Append the function signature with empty curly braces
                        result_string += function_signature + " {\n}\n"
                else:
                    print(f"Function {normalized_function} not found in ent2string.")
        else:
            print(f"Expected dictionary for file_info, but got {type(file_info)}")

        # Store the result string in the result dictionary
        result[file_path] = result_string.strip()

    # Save the updated data to a new JSON file in the output directory
    output_json_path = os.path.join(output_dir, 'compression_' + os.path.basename(json_file_path))
    with open(output_json_path, 'w', encoding='utf-8') as file:
        json.dump(result, file, ensure_ascii=False, indent=4)

# 第二部分代码：读取第一步的结果，找到类定义，并将类定义和第一步的结果合并后保存

def find_class_definition(file_path, class_name):
    """Find the definition of the class in the given file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        in_comment_block = False
        class_definition = ""
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            if stripped_line.startswith("/*"):
                in_comment_block = True
            if in_comment_block:
                if stripped_line.endswith("*/"):
                    in_comment_block = False
                continue
            if stripped_line.startswith("//") or in_comment_block:
                continue
            if stripped_line.startswith("import "):
                continue
            # Using a regex to match the class definition line
            if re.search(r'\bclass\b\s+' + re.escape(class_name) + r'\b', stripped_line):
                class_definition = stripped_line
                if not stripped_line.endswith("{"):
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        brace_index = next_line.find("{")
                        if brace_index != -1:
                            class_definition += " " + next_line[:brace_index].strip()
                            break
                        class_definition += " " + next_line
                        j += 1
                else:
                    brace_index = class_definition.find("{")
                    if brace_index != -1:
                        class_definition = class_definition[:brace_index].strip()
                return class_definition
    return None

def process_json_file_step2(json_file_path, output_dir):
    # Load JSON data
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Iterate through each file in the JSON data
    for file_path, file_info in data.items():
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            continue

        # Find the variable definition in the file
        class_name = os.path.splitext(os.path.basename(file_path))[0]

        class_definition = find_class_definition(file_path, class_name)
        if class_definition:
            data[file_path] = class_definition + ' {\n' + file_info + '\n}'

    output_json_path = os.path.join(output_dir, 'updated_' + os.path.basename(json_file_path))
    with open(output_json_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# 处理所有 JSON 文件

def process_all_json_files(input_dir, intermediate_dir, final_output_dir):
    # Ensure the intermediate and final output directories exist
    os.makedirs(intermediate_dir, exist_ok=True)
    os.makedirs(final_output_dir, exist_ok=True)

    # Get all JSON files in the input directory
    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]

    # Process each JSON file with step 1
    for json_file in json_files:
        json_file_path = os.path.join(input_dir, json_file)
        process_json_file_step1(json_file_path, intermediate_dir)

    # Get all intermediate JSON files
    intermediate_json_files = [f for f in os.listdir(intermediate_dir) if f.startswith('compression_') and f.endswith('.json')]

    # Process each intermediate JSON file with step 2
    for json_file in intermediate_json_files:
        json_file_path = os.path.join(intermediate_dir, json_file)
        process_json_file_step2(json_file_path, final_output_dir)

if __name__ == "__main__":
    input_json_dir = 'project_cases/json'  # 输入 JSON 文件所在的目录
    intermediate_dir = 'json/intermediate'  # 中间结果的目录
    final_output_dir = 'project_cases/reduced_code'  # 最终结果的目录
    process_all_json_files(input_json_dir, intermediate_dir, final_output_dir)
