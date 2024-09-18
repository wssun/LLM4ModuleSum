import csv
import argparse
import json
import logging
import os
import re
import sys
from io import StringIO
import tokenize
from tqdm import tqdm
from model import GPT, StarChat, CodeLLAMA


def read_file_to_string(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
        return file_content
    except Exception as e:
        return str(e)

def generate_summaries_zero_shot(args, model, code, output_file, cnt=0):
    args.logger.info('zero-shot prompt...')
    with open(output_file, args.mode, encoding="utf-8") as f:
        writer = csv.writer(f)
        for idx, c in tqdm(enumerate(code)):
            if idx < cnt:
                continue
            message = model.ask(input=args.basic_prompt + c)
            writer.writerow([idx, message])
            print('current idx:', idx)

def write_ground_truth(gold, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        cnt = 0
        for g in tqdm(gold):
            writer.writerow([cnt, g])
            cnt += 1

def remove_comments_and_docstrings(source, lang):
    if lang in ['python']:
        io_obj = StringIO(source)
        out = ""
        prev_toktype = tokenize.INDENT
        last_lineno = -1
        last_col = 0
        for tok in tokenize.generate_tokens(io_obj.readline):
            token_type, token_string, (start_line, start_col), (end_line, end_col), _ = tok
            if start_line > last_lineno:
                last_col = 0
            if start_col > last_col:
                out += " " * (start_col - last_col)
            if token_type == tokenize.COMMENT:
                pass
            elif token_type == tokenize.STRING:
                if prev_toktype != tokenize.INDENT:
                    if prev_toktype != tokenize.NEWLINE:
                        if start_col > 0:
                            out += token_string
            else:
                out += token_string
            prev_toktype = token_type
            last_col = end_col
            last_lineno = end_line
        temp = [x for x in out.split('\n') if x.strip()]
        return '\n'.join(temp)
    else:
        def replacer(match):
            s = match.group(0)
            return " " if s.startswith('/') else s

        pattern = re.compile(r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"', re.DOTALL | re.MULTILINE)
        temp = [x for x in re.sub(pattern, replacer, source).split('\n') if x.strip()]
        return '\n'.join(temp)

def main():
    prompt5 = """Please generate a comment to describe the functionality of the following reduced code in an imperative mood:"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_file", default="", type=str)
    parser.add_argument("--language", default="java", type=str)
    parser.add_argument("--model", default="gpt-4", type=str)
    parser.add_argument("--mode", default="w", type=str, help="append(a) or write(w)")
    parser.add_argument("--openai_key", default='', type=str)
    parser.add_argument("--max_new_tokens", default=4096, type=int)
    parser.add_argument("--temperature", default=0, type=float)
    parser.add_argument("--write_groundtruth", default=True, type=bool)
    parser.add_argument("--top_k", default=50, type=int)
    parser.add_argument("--top_p", default=0.5, type=float)
    parser.add_argument("--basic_prompt", default=f'{prompt5}:\n', type=str)
    parser.add_argument("--log_filename", default='log.txt', type=str)
    args = parser.parse_args()

    dir = './{}/{}/{}/'.format(args.language, args.model, args.temperature)
    if not os.path.exists(dir):
        os.makedirs(dir)

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s', datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO)
    args.logger = logging.getLogger(__name__)
    log_file_path = os.path.join(dir, args.log_filename)
    fh = logging.FileHandler(log_file_path)
    args.logger.addHandler(fh)
    args.logger.info("Training/evaluation parameters %s", args)

    MODEL_NAME_OR_PATH = {'gpt-4': 'gpt-4-1106-preview',
                          'gpt-3.5': 'gpt-3.5-turbo',
                          'starchat': '/home/jspi/data/mmp/starchat/starchat',
                          'codellama': '/home/david/MY/codellama/CodeLlama-7b-Instruct-hf'}
    args.model_name_or_path = MODEL_NAME_OR_PATH[args.model]
    if args.model == 'gpt-4':
        model = GPT(args=args)
    elif args.model == 'gpt-3.5':
        model = GPT(args=args)
    elif args.model == 'starchat':
        model = StarChat(args=args)
    elif args.model == 'codellama':
        model = CodeLLAMA(args=args)
    else:
        print('Model not found!')
        sys.exit(1)

    target_folder = '../project_cases/reduced_code'

    json_files = [file for file in os.listdir(target_folder) if file.endswith('.json')]

    for json_file_name in json_files:
        json_file_path = os.path.join(target_folder, json_file_name)

        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

        code = []
        for file_path, elements in data.items():
            code.append(elements)

        print(f"Processed {len(code)} elements from {json_file_name}")

        project_name = json_file_name.split('.')[0]
        output_csv_file = os.path.join('../result/file-level/GPT4/method2_reduced', f"{project_name}.csv")

        generate_summaries_zero_shot(args, model, code, output_csv_file, 0)

    print("CSV files generated successfully!")

if __name__ == '__main__':
    main()
