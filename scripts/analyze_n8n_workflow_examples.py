import argparse
import json
from collections import defaultdict
from pathlib import Path


def flatten_parameters(params, parent_key='', sep='.'):
    """
    Flattens a nested dictionary or list into a list of (key, value) tuples.
    Handles nested dictionaries and lists within the parameters.

    Args:
        params: The dictionary or list to flatten.
        parent_key: The base key string for nested keys (used internally).
        sep: The separator to use between nested keys.

    Returns:
        A list of tuples, where each tuple is (flattened_key, value).
        Returns an empty list if params is not a dict or list.
    """
    items = []
    if isinstance(params, dict):
        for k, v in params.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict | list):
                items.extend(flatten_parameters(v, new_key, sep=sep))
            else:
                items.append((new_key, v))
    elif isinstance(params, list):
        for i, v in enumerate(params):
            new_key = f"{parent_key}{sep}[{i}]" if parent_key else f"[{i}]"
            if isinstance(v, dict | list):
                items.extend(flatten_parameters(v, new_key, sep=sep))
            else:
                # Only append if the list item itself isn't directly a primitive
                # Usually, we care more about dicts inside lists
                # Might adjust this if lists of primitives are important
                if isinstance(v, dict | list):
                    items.append((new_key, v))
                # If we want to capture primitive values directly in lists:
                # else:
                #     items.append((new_key, v))

    return items

def generate_markdown_report(all_unique_keys, keys_by_node_type, file_count, node_count):
    """
    Generates a markdown report summarizing the parameter analysis.

    Args:
        all_unique_keys (set): A set of all unique flattened parameter keys found.
        keys_by_node_type (dict): A dictionary mapping node types to sets of keys.
        file_count (int): Number of JSON files processed.
        node_count (int): Total number of nodes processed.

    Returns:
        str: The generated markdown report.
    """
    markdown = []
    markdown.append("# Node Parameter Analysis Report")
    markdown.append(f"\nAnalyzed **{node_count}** nodes across **{file_count}** JSON files.\n")

    # --- Section 1: Overall Unique Keys ---
    markdown.append("## Overall Unique Parameter Keys")
    markdown.append("\nThis section lists all unique parameter keys found across all node types, after flattening nested structures.\n")
    if all_unique_keys:
        sorted_keys = sorted(all_unique_keys)
        for key in sorted_keys:
            markdown.append(f"- `{key}`")
    else:
        markdown.append("No parameter keys found.")
    markdown.append("\n---\n") # Separator

    # --- Section 2: Keys per Node Type ---
    markdown.append("## Parameter Keys per Node Type")
    markdown.append("\nThis section details the unique parameter keys found for each specific node type.\n")

    if keys_by_node_type:
        sorted_node_types = sorted(keys_by_node_type.keys())
        for node_type in sorted_node_types:
            markdown.append(f"\n### Node Type: `{node_type}`")
            keys = sorted(keys_by_node_type[node_type])
            if keys:
                for key in keys:
                    markdown.append(f"- `{key}`")
            else:
                markdown.append("- *No parameters found for this node type.*")
    else:
        markdown.append("No nodes with parameters were found.")

    return "\n".join(markdown)

def analyze_node_parameters(folder_path_str):
    """
    Analyzes JSON files in a folder to understand node parameters.

    Args:
        folder_path_str (str): The path to the folder containing JSON files.
    """
    folder_path = Path(folder_path_str)
    if not folder_path.is_dir():
        print(f"Error: Folder not found at '{folder_path_str}'")
        return

    all_flattened_params = []
    keys_by_node_type = defaultdict(set)
    all_unique_keys = set()
    processed_files = 0
    total_nodes = 0

    print(f"Starting analysis in folder: {folder_path.resolve()}")

    json_files = list(folder_path.glob('*.json'))
    if not json_files:
        print("No JSON files found in the specified folder.")
        return

    for file_path in json_files:
        print(f"Processing file: {file_path.name}...")
        processed_files += 1
        try:
            with open(file_path, encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, dict) and 'nodes' in data and isinstance(data['nodes'], list):
                nodes = data['nodes']
                total_nodes += len(nodes)
                for node in nodes:
                    if isinstance(node, dict):
                        node_type = node.get('type', 'UnknownType')
                        parameters = node.get('parameters')

                        if isinstance(parameters, dict):
                            flattened = flatten_parameters(parameters)
                            all_flattened_params.extend(flattened)
                            node_keys = {key for key, val in flattened}
                            keys_by_node_type[node_type].update(node_keys)
                            all_unique_keys.update(node_keys)
                        elif parameters is not None:
                             print(f"  Warning: Node '{node.get('name', node.get('id'))}' in {file_path.name} has non-dict parameters: {type(parameters)}")
                        # else: node has no parameters key - skip silently
                    else:
                         print(f"  Warning: Found non-dict item in 'nodes' list in {file_path.name}")

            else:
                print(f"  Warning: Skipping file {file_path.name} - Expected a JSON object with a 'nodes' list.")

        except json.JSONDecodeError:
            print(f"  Error: Could not decode JSON from file {file_path.name}.")
        except Exception as e:
            print(f"  Error processing file {file_path.name}: {e}")

    print(f"\nAnalysis complete. Processed {processed_files} files and {total_nodes} nodes.")

    # --- Generate and Save Report ---
    markdown_content = generate_markdown_report(all_unique_keys, keys_by_node_type, processed_files, total_nodes)
    report_path = folder_path / "node_parameter_analysis.md"

    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"Markdown report saved to: {report_path.resolve()}")
    except Exception as e:
        print(f"Error writing markdown report: {e}")

# --- Main Execution ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze n8n node parameters from JSON files in a folder.")
    parser.add_argument("folder", help="Path to the folder containing the n8n JSON workflow files.")
    args = parser.parse_args()

    analyze_node_parameters(args.folder)
