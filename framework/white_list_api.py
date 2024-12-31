import os
import json
import sys
from framework.utils import standardize
from tqdm import tqdm

"""
Function to generate a white list of tools from JSON files in subdirectories.
"""


def get_white_list(tool_root_dir):
    """
    This function takes the root directory of the tool environment,
    reads all JSON files inside the subdirectories, and compiles a
    white list of tools. The white list includes the tool's description
    and the standardized tool name.

    Args:
        tool_root_dir (str): The root directory containing tool JSON files in subdirectories.

    Returns:
        dict: A dictionary where the key is the standardized tool name, and the value
              is a dictionary containing the tool description and original tool name.
    """
    white_list_dir = os.path.join(tool_root_dir)
    white_list = {}

    for cate in tqdm(os.listdir(white_list_dir), desc="Processing Categories"):
        if not os.path.isdir(os.path.join(white_list_dir, cate)):
            continue

        for file in os.listdir(os.path.join(white_list_dir, cate)):
            if not file.endswith(".json"):
                continue

            standard_tool_name = file.split(".")[0]

            with open(os.path.join(white_list_dir, cate, file), encoding='UTF-8') as reader:
                js_data = json.load(reader)

            origin_tool_name = js_data["tool_name"]

            white_list[standardize(origin_tool_name)] = {
                "description": js_data["tool_description"],
                "standard_tool_name": standard_tool_name
            }

    return white_list


def main():
    if len(sys.argv) > 1:
        tool_root_dir = sys.argv[1]
    else:
        tool_root_dir = r"\data\toolenv\tools"

    white_list = get_white_list(tool_root_dir)
    print(white_list)

    path = 'data/white_list.json'

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(white_list, f, ensure_ascii=False, indent=4)

    print(f'White list has been saved to {path}')


if __name__ == "__main__":
    main()
