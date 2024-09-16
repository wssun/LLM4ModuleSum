import os
import sys
import subprocess
import pathlib
import argparse
import json

os.add_dll_directory("D:\\Program Files\\SciTools\\bin\\pc-win64\\")
import understand

understand.version()

def parse_und_prj(db_path):
    db = understand.open(db_path)

    file2info = {}
    serializable_file2info = {}

    for file in db.ents("File"):
        if file.library() == "Standard":
            continue

        print(file.relname())

        clazz2contents = {}
        serializable_clazz2contents = {}
        for clazz_ref in file.filerefs("define", "class"):
            clazz_ent = clazz_ref.ent()
            clazz2contents[clazz_ent] = {
                'functions': [],
                'variables': []
            }
            serializable_clazz2contents['class'] = {
                'class_name':'',
                'functions': [],
                'variables': []
            }
            serializable_clazz2contents['class']['class_name']=clazz_ent.longname()
            for func_ref in clazz_ent.refs("Define", "function, method"):
                func_ent = func_ref.ent()
                clazz2contents[clazz_ent]['functions'].append(func_ent)
                serializable_clazz2contents['class']['functions'].append(func_ent.longname())

            for var_ref in clazz_ent.refs("Define", "variable"):
                var_ent = var_ref.ent()
                clazz2contents[clazz_ent]['variables'].append(var_ent)
                serializable_clazz2contents['class']['variables'].append(var_ent.longname())

        ent2clazz = {}
        serializable_ent2clazz = {}
        for clazz_ent, contents in clazz2contents.items():
            for func_ent in contents['functions']:
                ent2clazz[func_ent] = clazz_ent
                serializable_ent2clazz[func_ent.longname()] = clazz_ent.longname()
            for var_ent in contents['variables']:
                ent2clazz[var_ent] = clazz_ent
                serializable_ent2clazz[var_ent.longname()] = clazz_ent.longname()

        ent2string = {}
        serializable_ent2string = {}

        for clazz_ent, contents in clazz2contents.items():
            for func_ent in contents['functions']:
                func_content = func_ent.contents()
                func_comment = func_ent.comments("before")
                if func_comment:
                    func_content += " comment:" + func_comment

                ent2string[func_ent] = func_content
                serializable_ent2string[func_ent.longname()] = func_content

            for var_ent in contents['variables']:
                var_name = var_ent.name()
                var_comment = var_ent.comments("before")
                if var_comment:
                    var_name += " comment:" + var_comment
                ent2string[var_ent] = var_name
                serializable_ent2string[var_ent.longname()] = var_name

        func_func_dependencies = []
        serializable_func_func_dependencies = []
        func_var_dependencies = []
        serializable_func_var_dependencies = []
        for clazz_ent, contents in clazz2contents.items():
            src_clazz = clazz_ent
            for func_ent in contents['functions']:
                for call_ref in func_ent.refs('call'):
                    ref_ent = call_ref.ent()
                    dst_clazz = ent2clazz.get(ref_ent, None)
                    if dst_clazz is None:
                        continue
                    func_func_dependencies.append({
                        'src': func_ent,
                        'dst': ref_ent,
                        'src_clazz': src_clazz,
                        'dst_clazz': dst_clazz
                    })
                    serializable_func_func_dependencies.append({
                        'src': func_ent.longname(),
                        'dst': ref_ent.longname(),
                        'src_clazz': src_clazz.longname(),
                        'dst_clazz': dst_clazz.longname()
                    })

                for var_ref in func_ent.refs('use'):
                    ref_ent = var_ref.ent()
                    dst_clazz = ent2clazz.get(ref_ent, None)
                    if dst_clazz is None:
                        continue

                    func_var_dependencies.append({
                        'src': func_ent,
                        'dst': ref_ent,
                        'src_clazz': src_clazz,
                        'dst_clazz': dst_clazz
                    })
                    serializable_func_var_dependencies.append({
                        'src': func_ent.longname(),
                        'dst': ref_ent.longname(),
                        'src_clazz': src_clazz.longname(),
                        'dst_clazz': dst_clazz.longname()
                    })

        file2info[file] = {
            'clazz2contents': clazz2contents,
            'ent2string': ent2string,
            'func_func_dependencies': func_func_dependencies,
            'func_var_dependencies': func_var_dependencies
        }
        serializable_file2info[file.longname()] = {
            'clazz2contents': serializable_clazz2contents,
            'ent2string': serializable_ent2string,
            'func_func_dependencies': serializable_func_func_dependencies,
            'func_var_dependencies': serializable_func_var_dependencies
        }

    db.close()
    return serializable_file2info

def create_und_db(prj_path, prj_lang, prj_name=None, und_folder='.'):
    if not prj_name:
        prj_name = pathlib.Path(prj_path).name
    und_prj_path = os.path.join(und_folder, prj_name + '.und')
    if os.path.exists(und_prj_path):
        print(f'Understand project {und_prj_path} already exists')
        return und_prj_path

    cmd_create = f'und create -db {und_prj_path} -languages {prj_lang}'
    subprocess.run(cmd_create, shell=True)

    cmd_add = f'und add {prj_path} {und_prj_path}'
    subprocess.run(cmd_add, shell=True)

    cmd_analyze = f'und analyze {und_prj_path}'
    subprocess.run(cmd_analyze, shell=True)

    return und_prj_path

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--db_path', type=str, help='The path to the Understand database', default='D:/projects/skywalking-master')
    arg_parser.add_argument('--prj_lang', type=str, help='The language of the project (c++ or java)',default='java')
    arg_parser.add_argument('--prj_name', type=str, help='The name of the project', default='skywalking-master')
    arg_parser.add_argument('--und_folder', type=str, help='The folder to store the Understand database', default='data/und')
    args = arg_parser.parse_args()

    und_prj_path = create_und_db(args.db_path, args.prj_lang, args.prj_name, args.und_folder)

    parse_result = parse_und_prj(und_prj_path)

    with open(f'parse_result_{args.prj_name}.json', 'w', encoding='utf-8') as f:
        json.dump(parse_result, f, ensure_ascii=False, indent=4)
