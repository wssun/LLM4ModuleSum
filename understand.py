import understand
import os
import sys
import subprocess
import pathlib
import argparse

# Parse the Understand project to get the dependencies inside each file
def parse_und_prj(db_path):
    db = understand.open(db_path)

    file2info = {}

    # iterate all files in the project
    for file in db.ents("File"):

        # skip standard library files
        if file.library() == "Standard":
            continue

        print(file.relname())

        # iterate all classes in the file, get the functions and variables
        # TODO - class in class?
        clazz2contents = {}
        for clazz_ref in file.filerefs("define", "class"):
            clazz_ent = clazz_ref.ent()
            clazz2contents[clazz_ent] = {
                'functions':[],
                'variables':[]
            }

            for func_ref in clazz_ent.refs("Define", "function, method"):
                func_ent = func_ref.ent()
                clazz2contents[clazz_ent]['functions'].append(func_ent)

            for var_ref in clazz_ent.refs("Define", "variable"):
                var_ent = var_ref.ent()
                clazz2contents[clazz_ent]['variables'].append(var_ent)

        # map entities to their parent classes
        ent2clazz = {}
        for clazz_ent, contents in clazz2contents.items():
            for func_ent in contents['functions']:
                ent2clazz[func_ent] = clazz_ent
            for var_ent in contents['variables']:
                ent2clazz[var_ent] = clazz_ent

        # map entities to their content strings
        # TODO - add comments
        # TODO - add the type of variables
        ent2string = {}
        for clazz_ent, contents in clazz2contents.items():
            for func_ent in contents['functions']:
                ent2string[func_ent] = func_ent.contents()
            for var_ent in contents['variables']:
                ent2string[var_ent] = var_ent.name()

        # get the dependencies inside the file
        # TODO - other types of dependencies?
        func_func_dependencies = []
        func_var_dependencies = []
        for clazz_ent, contents in clazz2contents.items():
            src_clazz = clazz_ent
            for func_ent in contents['functions']:

                # get the dependencies between functions
                for call_ref in func_ent.refs('call'):
                    ref_ent = call_ref.ent()
                    dst_clazz = ent2clazz.get(ref_ent, None)
                    if dst_clazz is None:
                        # reference to sth outside the file
                        continue
                    func_func_dependencies.append(
                        {
                            'src':func_ent,
                            'dst':ref_ent,
                            'src_clazz':src_clazz,
                            'dst_clazz':dst_clazz,
                        }
                    )

                # get the dependencies between functions and variables
                for var_ref in func_ent.refs('use'):
                    ref_ent = var_ref.ent()
                    dst_clazz = ent2clazz.get(ref_ent, None)
                    if dst_clazz is None:
                        # reference to sth outside the file or local variable
                        continue

                    func_var_dependencies.append(
                        {
                            'src':func_ent,
                            'dst':ref_ent,
                            'src_clazz':src_clazz,
                            'dst_clazz':dst_clazz,
                        }
                    )

                    pass

        # record the dependencies
        file2info[file] = {
            'clazz2contents':clazz2contents,
            'ent2string':ent2string,
            'func_func_dependencies':func_func_dependencies,
            'func_var_dependencies':func_var_dependencies
        }
    db.close()
    return file2info

# Create a new Understand database from the project folder
# @param prj_lang: c++ or java
def create_und_db(prj_path, prj_lang, prj_name = None, und_folder = '.'):
    if not prj_name:
        prj_name = pathlib.Path(prj_path).name
    und_prj_path = os.path.join(und_folder, prj_name + '.und')
    if os.path.exists(und_prj_path):
        print(f'Understand project {und_prj_path} already exists')
        return und_prj_path


    # create the Understand project
    cmd_create = f'und create -db {und_prj_path} -languages {prj_lang}'
    subprocess.run(cmd_create, shell=True)

    # add the project files to the Understand project
    cmd_add = f'und add {prj_path} {und_prj_path}'
    subprocess.run(cmd_add, shell=True)

    # analyze the project
    cmd_analyze = f'und analyze {und_prj_path}'
    subprocess.run(cmd_analyze, shell=True)

    return und_prj_path


'''
Example:
    args.db_path = 'data/projects/hadoop'
    args.prj_lang = 'java'
    args.prj_name = 'hadoop'
    args.und_folder = 'data/und'
'''

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('db_path', type=str, help='The path to the Understand database')
    arg_parser.add_argument('prj_lang', type=str, help='The language of the project (c++ or java)')
    arg_parser.add_argument('prj_name', type=str, help='The name of the project', default=None)
    arg_parser.add_argument('und_folder', type=str, help='The folder to store the Understand database', default='.')
    args = arg_parser.parse_args()
    und_prj_path = create_und_db(args.db_path, args.prj_lang, args.prj_name, args.und_folder)
    parse_result = parse_und_prj(und_prj_path)



