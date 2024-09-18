import json
import os
from llm_yiran.openai_models import GPTModel
from llm_yiran.settings import GPT_4_MODEL
import pandas as pd

import tiktoken
import copy
from io import StringIO
import tokenize
import re
import random
import pickle
import csv

gpt_encoder = tiktoken.encoding_for_model(GPT_4_MODEL)

def get_prompt_fullcode(json_prj2main_module2file2full_code):
    prompt_base = "Please generate a concise comment to describe the functionality of the following module in an imperative mood."
    with open(json_prj2main_module2file2full_code, 'r', encoding='utf-8') as file:
        prj2main_module2file2full_code = json.load(file)
    
    prj2main_module2prompt = {}
    for prj, main_module2file2full_code in prj2main_module2file2full_code.items():
        for main_module, file2full_code in main_module2file2full_code.items():
            prompt = f'{prompt_base}'
            # prompt += f'\n\nModule Name: {main_module}'
            prompt = f'Module Name: {main_module}'
            prompt += f'\n\nCode Files in Module:'
            for file, full_code in file2full_code.items():
                prompt += f'\n\nFile: {file}\nContent:{full_code}'
            prj2main_module2prompt.setdefault(prj, {})[main_module] = prompt
    all_prompts = [prompt for prj, main_module2prompt in prj2main_module2prompt.items() for main_module, prompt in main_module2prompt.items()]
    all_prompts = sorted(all_prompts, key=lambda x: len(x))
    prompt_lens = [len(prompt) for prj, main_module2prompt in prj2main_module2prompt.items() for main_module, prompt in main_module2prompt.items()]
    
    with open('data/prj2main_module2prompt_full_code.json', 'w', encoding='utf-8') as file:
        json.dump(prj2main_module2prompt, file, ensure_ascii=False, indent=4)
    
def get_prompt_compressed_code(json_prj2main_module2file2compressed_code):
    prompt_base = "Please generate a concise comment to describe the functionality of the following module in an imperative mood."
    with open(json_prj2main_module2file2compressed_code, 'r', encoding='utf-8') as file:
        prj2main_module2file2compressed_code = json.load(file)
    prj2main_module2prompt = {}
    for prj, main_module2file2compressed_code in prj2main_module2file2compressed_code.items():
        for main_module, file2compressed_code in main_module2file2compressed_code.items():
            prompt = f'{prompt_base}'
            # prompt += f'\n\nModule Name: {main_module}'
            prompt = f'Module Name: {main_module}'
            prompt += f'\n\nCode Files in Module:'
            for file, compressed_code in file2compressed_code.items():
                prompt += f'\n\nFile: {file}\nContent:\n{compressed_code}'
            prj2main_module2prompt.setdefault(prj, {})[main_module] = prompt
    all_prompts = [prompt for prj, main_module2prompt in prj2main_module2prompt.items() for main_module, prompt in main_module2prompt.items()]
    prompt_lens = [len(prompt) for prj, main_module2prompt in prj2main_module2prompt.items() for main_module, prompt in main_module2prompt.items()]
    prompt_lens = sorted(prompt_lens)
    with open('data/prj2main_module2prompt_compressed_code.json', 'w', encoding='utf-8') as file:
        json.dump(prj2main_module2prompt, file, ensure_ascii=False, indent=4)
    pass

def get_prompt_summary(json_prj2main_module2file2full_code, summary_base_path):
    prompt_base = "Please generate a concise comment to describe the functionality of the following module in an imperative mood."
    with open(json_prj2main_module2file2full_code, 'r', encoding='utf-8') as file:
        prj2main_module2file2full_code = json.load(file)
    prj2main_module2prompt = {}
    for prj, main_module2file2full_code in prj2main_module2file2full_code.items():
        for main_module, file2full_code in main_module2file2full_code.items():
            prompt = f'{prompt_base}'
            # prompt += f'\n\nModule Name: {main_module}'
            prompt = f'Module Name: {main_module}'
            prompt += f'\n\nCode Files in Module:'
            for file, full_code in file2full_code.items():
                summary_path = os.path.join(summary_base_path, prj, file)
                try:
                    with open(summary_path, 'r', encoding='utf-8') as f:
                        summary = f.read()
                    prompt += f'\n\nFile: {file}\nSummary: {summary}'
                except Exception as e:
                    print(f'Error in reading summary file {summary_path}: {e}')
                    # prompt += f'\n\nFile: {file}\nSummary: None\n'
            prj2main_module2prompt.setdefault(prj, {})[main_module] = prompt
            
    all_prompts = [prompt for prj, main_module2prompt in prj2main_module2prompt.items() for main_module, prompt in main_module2prompt.items()]
    all_prompts = sorted(all_prompts, key=lambda x: len(x))
    prompt_lens = [len(prompt) for prj, main_module2prompt in prj2main_module2prompt.items() for main_module, prompt in main_module2prompt.items()]
    with open('data/prj2main_module2prompt_summary.json', 'w', encoding='utf-8') as file:
        json.dump(prj2main_module2prompt, file, ensure_ascii=False, indent=4)
    pass

def summary_file_for_module_summary(json_prj2main_module2file2full_code):
    
    save_base_path = 'result/summary_for_module_summary/'
    
    system_prompt = """"""
    prompt5 = """Please generate a concise comment to describe the functionality of the following code in an imperative mood:"""+'\n'
    with open(json_prj2main_module2file2full_code, 'r', encoding='utf-8') as file:
        prj2main_module2file2full_code = json.load(file)
        
    model = GPTModel(model=GPT_4_MODEL, record_usage=True, use_cache=True)
    # total_files = sum([len(file2full_code) for main_module2file2full_code in prj2main_module2file2full_code.values() for file2full_code in main_module2file2full_code.values()])
    # prj2main_module2file_cnt = {prj: {main_module: len(file2full_code) for main_module, file2full_code in main_module2file2full_code.items()} for prj, main_module2file2full_code in prj2main_module2file2full_code.items()}
    
    file_cnt = 0
    for prj, main_module2file2full_code in prj2main_module2file2full_code.items():
        for main_module, file2full_code in main_module2file2full_code.items():
            for file, full_code in file2full_code.items():
                code = full_code
                messages = []
                messages.append({'role': 'system', 'content': system_prompt})
                messages.append({'role': 'user', 'content': prompt5+code})
                try:
                    result = model.ask(messages, seed=0)
                    save_path = os.path.join(save_base_path, prj, file)
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    with open(save_path, 'w', encoding='utf-8') as file:
                        file.write(result)
                    file_cnt += 1
                    print(f'Generated comment for {file_cnt} files, total price: {model.static_gpt_price}')
                except Exception as e:
                    print(f'Error in generating comment for {prj}/{file}: {e}')
                    
                pass
    pass
    
    
    pass

def summary_module(json_prj2main_module2prompt_code, save_base_path):
    with open(json_prj2main_module2prompt_code, 'r', encoding='utf-8') as file:
        prj2main_module2prompt = json.load(file)
    for prj, main_module2prompt in prj2main_module2prompt.items():
        module2result = {}
        for main_module, prompt in main_module2prompt.items():
            model = GPTModel(model=GPT_4_MODEL, record_usage=True, use_cache=True)
            messages = []
            # no system prompt for module level summary
            messages.append({'role': 'user', 'content': prompt})
            try:
                tokens = len(gpt_encoder.encode(prompt))
                print(tokens)
                result = model.ask(messages, seed=0)
                module2result[main_module] = result
                print(f'Generated comment for {prj}/{main_module}, total price: {model.static_gpt_price}')
            except Exception as e:
                print(f'Error in generating comment for {prj}/{main_module}: {e}')
                module2result[main_module] = None
            pass
        os.makedirs(save_base_path, exist_ok=True)
        with open(os.path.join(save_base_path, prj+'.json'), 'w', encoding='utf-8') as file:
            json.dump(module2result, file, ensure_ascii=False, indent=4)
        pass
    
    pass

if __name__ == '__main__':
    get_prompt_fullcode('data/prj2main_module2file2full_code.json')
    get_prompt_compressed_code('data/prj2main_module2file2compressed_code.json')
    summary_file_for_module_summary('data/prj2main_module2file2full_code.json')
    get_prompt_summary('data/prj2main_module2file2full_code.json', 'result/summary_for_module_summary/')
    summary_module('data/prj2main_module2prompt_full_code.json', 'result/module_level/GPT4/method1_all/')
    summary_module('data/prj2main_module2prompt_compressed_code.json', 'result/module_level/GPT4/method2_reduced/')
    summary_module('data/prj2main_module2prompt_summary.json', 'result/module_level/GPT4/method3_summary/')
    pass
