import networkx as nx
import community.community_louvain as community_louvain
import json
import os


def read_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def build_graph(details):
    G = nx.Graph()

    if 'clazz2contents' in details and 'class' in details['clazz2contents']:
        clazz = details['clazz2contents']['class']

        functions = clazz.get('functions', [])
        variables = clazz.get('variables', [])

        for func in functions:
            G.add_node(func)

        for var in variables:
            G.add_node(var)

        for dep in details.get('func_func_dependencies', []):
            G.add_edge(dep['src'], dep['dst'])

        for dep in details.get('func_var_dependencies', []):
            G.add_edge(dep['src'], dep['dst'])

    return G


def detect_communities(G):
    partition = community_louvain.best_partition(G)
    return partition


def extract_code_from_partition(details, partition):
    communities = {}
    ent2string = details.get('ent2string', {})

    for node, community in partition.items():
        if community not in communities:
            communities[community] = []
        communities[community].append(node)

    community_codes = {}
    for community, nodes in communities.items():
        code_snippets = [ent2string[node] for node in nodes if node in ent2string]
        community_codes[community] = organize_code_snippets(code_snippets)

    return community_codes


def organize_code_snippets(code_snippets):
    variables = []
    functions = []
    for snippet in code_snippets:
        lines = snippet.strip().split("\n")
        if any("{" in line for line in lines):
            functions.append(snippet)
        else:
            variables.append(snippet)
    return "\n".join(variables + [""] + functions)


def save_communities_as_json(filepath, all_community_codes):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(all_community_codes, f, ensure_ascii=False, indent=4)


def print_communities(file, partition):
    communities = {}
    for node, community in partition.items():
        if community not in communities:
            communities[community] = []
        communities[community].append(node)

    print(f"File: {file}")
    for community, nodes in communities.items():
        print(f"  Community {community}:")
        for node in nodes:
            print(f"    - {node}")

    return len(communities)


def compute_average_community_count(partition_counts):
    if not partition_counts:
        return 0
    return sum(partition_counts) / len(partition_counts)


def process_all_json_files(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]

    partition_counts = []
    all_community_codes = {}

    for json_file in json_files:
        json_file_path = os.path.join(input_dir, json_file)
        data = read_json(json_file_path)

        for file, details in data.items():
            G = build_graph(details)

            if len(G.nodes) > 0:
                partition = detect_communities(G)

                community_count = print_communities(file, partition)
                partition_counts.append(community_count)

                community_codes = extract_code_from_partition(details, partition)

                all_community_codes[file] = community_codes
            else:
                print(f"File: {file} contains no valid nodes.")

        output_json_path = os.path.join(output_dir, 'communities_' + json_file)
        print(f"Saving community codes to: {output_json_path}")
        save_communities_as_json(output_json_path, all_community_codes)

        all_community_codes = {}

    average_community_count = compute_average_community_count(partition_counts)
    print(f"Average number of communities: {average_community_count:.2f}")


if __name__ == "__main__":
    input_json_dir = 'project_cases/processed'
    output_dir = 'project_cases/community'
    process_all_json_files(input_json_dir, output_dir)
