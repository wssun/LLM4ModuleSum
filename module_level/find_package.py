import os
import pandas as pd
import re
import json
import random
from tqdm import tqdm

def find_package():
    prj2file2package = {}
    for prj in os.listdir('projects/'):
        with open(f'data/json_tmp/{prj}.json', 'r', encoding='utf-8') as f:
            und_data = json.load(f)
        files_in_understand = set(k.removeprefix('D:\\') for k in und_data.keys())
        file2package = {}
        for root, dirs, files in tqdm(os.walk(f'projects\\{prj}'), desc=prj):
            for file in files:
                if not file.endswith('.java'):
                    continue
                if f'{root}\\{file}' not in files_in_understand:
                    continue
                with open(f'{root}/{file}', 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line.startswith('package '):
                            continue
                        res = re.search(r'package\s(\S+)\s{0,};', line)
                        if not res:
                            continue
                        package = res.group(1)
                        
                        filepath = f'{root}/{file}'.replace('\\', '/')
                        
                        file2package[filepath] = package
                        break
        prj2file2package[prj] = file2package
        
        pass
    with open('data/prj2file2package.json', 'w', encoding='utf-8') as f:
        json.dump(prj2file2package, f, ensure_ascii=False, indent=4)
    pass

def split_module():
    with open('data/prj2file2package.json', 'r', encoding='utf-8') as f:
        prj2file2package = json.load(f)

    # remove tests
    for prj, file2package in prj2file2package.items():
        prj2file2package[prj] = {f:p for f, p in file2package.items() if 'test' not in p.lower() and 'test' not in f.lower()}
    
    prj2main_module2file = {}
    for prj, file2package in prj2file2package.items():
        curr_level = 1
        remaining_files = list(file2package.keys())
        while True:
            module2file = {}
            for file in remaining_files:
                package = file2package[file]
                module = '.'.join(package.split('.')[:curr_level])
                module2file.setdefault(module, []).append(file)
            max_module = max(module2file.items(), key=lambda x: len(x[1]))[0]
            max_pct = len(module2file[max_module]) / len(remaining_files)
            if max_pct < 0.75:
                break
            curr_level += 1
            remaining_files = module2file[max_module]
        module2file = {m:fs for m, fs in module2file.items() if len(fs) > 1}
        prj2main_module2file[prj] = module2file
        
    prj2main_module2file_cnt = {}
    for prj, main_module2file in prj2main_module2file.items():
        main_module2file_cnt = {}
        for main_module, files in main_module2file.items():
            main_module2file_cnt[main_module] = len(files)
        prj2main_module2file_cnt[prj] = main_module2file_cnt
    
    all_main_module2file_cnt = {}
    for main_module2file_cnt in prj2main_module2file_cnt.values():
        for main_module, cnt in main_module2file_cnt.items():
            all_main_module2file_cnt[main_module] = cnt
            
    # import seaborn as sns
    # import matplotlib.pyplot as plt
    # sns.histplot(all_main_module2file_cnt.values(), log_scale=True)
    # plt.show()
    
    random.seed(1)
    prj2selected_main_module2file = {}
    for prj, main_module2file in prj2main_module2file.items():
        selected_main_modules = random.sample(list(main_module2file.keys()), 5)
        prj2selected_main_module2file[prj] = {m: main_module2file[m] for m in selected_main_modules}
        pass
    
    prj2selected_main_module2file_cnt = {}
    for prj, main_module2file in prj2selected_main_module2file.items():
        main_module2file_cnt = {}
        for main_module, files in main_module2file.items():
            main_module2file_cnt[main_module] = len(files)
        prj2selected_main_module2file_cnt[prj] = main_module2file_cnt
    
    selected_module2file_cnt = {}
    for main_module2file_cnt in prj2selected_main_module2file_cnt.values():
        for main_module, cnt in main_module2file_cnt.items():
            selected_module2file_cnt[main_module] = cnt
    import seaborn as sns
    import matplotlib.pyplot as plt
    sns.histplot(selected_module2file_cnt.values(), log_scale=True)
    plt.show()
    # dump to csv with pandas
    df = pd.DataFrame(selected_module2file_cnt.items(), columns=['module', 'file_cnt'])
    df.to_csv('data/selected_module_sizes.csv', index=False)
    
    with open('data/prj2selected_main_module2file.json', 'w', encoding='utf-8') as f:
        json.dump(prj2selected_main_module2file, f)
    pass

    
if __name__ == '__main__':
    find_package()
    split_module()
