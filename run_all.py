import json
import os
import random
import shutil
import csv
import argparse
import logging
import sys
import re
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
    f = open(output_file, args.mode, encoding="utf-8")
    writer = csv.writer(f)
    for idx, c in tqdm(enumerate(code)):
        if idx < cnt: continue
        response = model.ask(input=args.basic_prompt + c)
        first_number = re.search(r'\d+', response)
        if first_number:
            message = first_number.group()
        else:
            message = "No number found"
        writer.writerow([idx, message])
        print('current idx:', idx)
    f.close()

def write_ground_truth(gold, output_path):
    f = open(output_path, "w", encoding="utf-8")
    writer = csv.writer(f)
    cnt = 0
    for g in tqdm(gold):
        writer.writerow([cnt, g])
        cnt = cnt + 1
    f.close()

def remove_comments_and_docstrings(source, lang):
    if lang in ['python']:
        io_obj = StringIO(source)
        out = ""
        prev_toktype = tokenize.INDENT
        last_lineno = -1
        last_col = 0
        for tok in tokenize.generate_tokens(io_obj.readline):
            token_type = tok[0]
            token_string = tok[1]
            start_line, start_col = tok[2]
            end_line, end_col = tok[3]
            ltext = tok[4]
            if start_line > last_lineno:
                last_col = 0
            if start_col > last_col:
                out += (" " * (start_col - last_col))
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
        temp = []
        for x in out.split('\n'):
            if x.strip() != "":
                temp.append(x)
        return '\n'.join(temp)
    elif lang in ['ruby']:
        return source
    else:
        def replacer(match):
            s = match.group(0)
            if s.startswith('/'):
                return " "
            else:
                return s

        pattern = re.compile(
            r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
            re.DOTALL | re.MULTILINE
        )
        temp = []
        for x in re.sub(pattern, replacer, source).split('\n'):
            if x.strip() != "":
                temp.append(x)
        return '\n'.join(temp)

def main():
    prompt5 = """Please generate a comment to describe the functionality of the following code in an imperative mood:"""
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
    parser.add_argument("--basic_prompt", default=f'{prompt5}\n', type=str)
    parser.add_argument("--log_filename", default='log.txt', type=str)
    args = parser.parse_args()

    dir = './{}/{}/{}/'.format(args.language, args.model, args.temperature)
    if os.path.exists(dir) == False:
        os.makedirs(dir)

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s', datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO)
    args.logger = logging.getLogger(__name__)
    log_file_path = os.path.join(os.path.join(dir, args.log_filename))
    fh = logging.FileHandler(log_file_path)
    args.logger.addHandler(fh)
    args.logger.info("Training/evaluation parameters %s", args)
    args.logger.info("\n")

    MODEL_NAME_OR_PATH = {'gpt-4': 'gpt-4-1106-preview',
                          'gpt-3.5': 'gpt-3.5-turbo',
                          'gpt-4o-mini':'gpt-4o-mini',
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
    elif args.model == 'gpt-4o-mini':
        model = GPT(args=args)
    else:
        print('Model not found!')
        sys.exit(1)

    json_folder_path = '../project_cases/json/'

    all_files = os.listdir(json_folder_path)

    json_files = [file for file in all_files if file.endswith('.json')]

    for json_file_name in json_files:
        json_file_path = os.path.join(json_folder_path, json_file_name)

        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

        code = []
        for file_path, elements in data.items():
            file_content = read_file_to_string(file_path)
            print(f"Content of file {file_path}:\n{file_content}\n")
            code.append(remove_comments_and_docstrings(file_content, 'java'))

        print(len(code))

        output_file_name = f'updated_parse_result_{json_file_name}'

        generate_summaries_zero_shot(args, model, code, dir+f'{output_file_name}.csv', 0)

if __name__ == '__main__':
    main()
