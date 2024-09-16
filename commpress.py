import json
import os
import re

def process_json_file_step1(json_file_path, output_dir):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    result = {}

    for file_path, file_info in data.items():
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            continue

        result_string = ""

        if isinstance(file_info, dict):
            class_info = file_info.get('clazz2contents', {}).get('class', {})
            ent2string = file_info.get('ent2string', {})

            for variable in class_info.get('variables', []):
                if variable in ent2string:
                    result_string += ent2string[variable] + "\n"
                else:
                    print(f"Variable {variable} not found in ent2string.")

            for function in class_info.get('functions', []):
                normalized_function = function.strip()
                if normalized_function in ent2string:
                    func_lines = ent2string[normalized_function].strip().split('\n')
                    if len(func_lines) > 0:
                        first_line = func_lines[0].strip()
                        opening_brace_index = first_line.find('{')
                        if opening_brace_index != -1:
                            function_signature = first_line[:opening_brace_index].strip()
                        else:
                            function_signature = first_line
                        result_string += function_signature + " {\n}\n"
                else:
                    print(f"Function {normalized_function} not found in ent2string.")
        else:
            print(f"Expected dictionary for file_info, but got {type(file_info)}")

        result[file_path] = result_string.strip()

    output_json_path = os.path.join(output_dir, 'compression_' + os.path.basename(json_file_path))
    with open(output_json_path, 'w', encoding='utf-8') as file:
        json.dump(result, file, ensure_ascii=False, indent=4)

def find_class_definition(file_path, class_name):
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
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for file_path, file_info in data.items():
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            continue

        class_name = os.path.splitext(os.path.basename(file_path))[0]

        class_definition = find_class_definition(file_path, class_name)
        if class_definition:
            data[file_path] = class_definition + ' {\n' + file_info + '\n}'

    output_json_path = os.path.join(output_dir, 'updated_' + os.path.basename(json_file_path))
    with open(output_json_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def process_all_json_files(input_dir, intermediate_dir, final_output_dir):
    os.makedirs(intermediate_dir, exist_ok=True)
    os.makedirs(final_output_dir, exist_ok=True)

    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]

    for json_file in json_files:
        json_file_path = os.path.join(input_dir, json_file)
        process_json_file_step1(json_file_path, intermediate_dir)

    intermediate_json_files = [f for f in os.listdir(intermediate_dir) if f.startswith('compression_') and f.endswith('.json')]

    for json_file in intermediate_json_files:
        json_file_path = os.path.join(intermediate_dir, json_file)
        process_json_file_step2(json_file_path, final_output_dir)

if __name__ == "__main__":
    input_json_dir = 'project_cases/json'
    intermediate_dir = 'json/intermediate'
    final_output_dir = 'project_cases/reduced_code'
    process_all_json_files(input_json_dir, intermediate_dir, final_output_dir)
