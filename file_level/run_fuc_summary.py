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
            message = model.ask(input=c + args.basic_prompt)
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
    prompt5 = """Please generate a concise comment in an imperative mood to describe the functionality of the class code based on the summaries provided above."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_file", default="", type=str)
    parser.add_argument("--language", default="java", type=str)
    parser.add_argument("--model", default="gpt-3.5", type=str)
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

    target_folder = '../result/file-level/GPT4/method4_function/json_result'

    json_files = [f for f in os.listdir(target_folder) if f.endswith('.json')]

    for json_filename in json_files:
        json_file_path = os.path.join(target_folder, json_filename)

        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

        code = []

        for file_path, communities in data.items():
            community_code = []
            classname = file_path.split("\\")[-1].replace(".java", "")
            community_code.append(
                f'To facilitate better summarization, the class {classname} has been divided into several functions. Here are the names of these functions and their summaries:')

            counter = 1
            for elements in communities:
                community_code.append(f"function {counter}: {elements['summary']}\n")
                counter += 1

            code.append("\n".join(community_code))

        print(f'Processed {len(code)} functions across all files.')
        print(code)

        output_csv_path = os.path.join('../result/file-level/GPT4/method4_function/final_result',
                                       f'{os.path.splitext(json_filename)[0]}_zero_shot.csv')

        generate_summaries_zero_shot(args, model, code, output_csv_path, 0)
        print(f'Summaries generated and saved to {output_csv_path}')

if __name__ == '__main__':
    main()
