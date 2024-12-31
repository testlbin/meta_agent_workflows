import json
import re

def extract_successful_finish_trajectories(data):
    """
    Extract dialogue trajectories that meet the condition.

    Args:
        data (dict): JSON data dictionary containing all dialogue information.

    Returns:
        list: List of successful dialogue trajectories that meet the condition.
    """
    successful_trajectories = []
    for dialogue in data.get("train_messages", []):
        for message in dialogue:
            function_call = message.get("function_call", {})
            if function_call.get("name") == "Finish":
                arguments_str = function_call.get("arguments", "{}")
                try:
                    arguments = json.loads(arguments_str)
                    if arguments.get("return_type") == "give_answer":
                        successful_trajectories.append(dialogue)
                except json.JSONDecodeError:
                    print(f"Error decoding arguments in function_call for message: {message}")
    return successful_trajectories


def standardize(string):
    """
    Standardize the given string by removing non-alphanumeric characters
    and converting it to lowercase. Also ensures there are no consecutive
    underscores or leading/trailing underscores, and prepends 'get_' if the
    string starts with a number.

    Args:
        string (str): The string to standardize.

    Returns:
        str: The standardized string.
    """
    res = re.compile("[^\\u4e00-\\u9fa5^a-z^A-Z^0-9^_]")
    string = res.sub("_", string)
    string = re.sub(r"(_)\1+", "_", string).lower()
    while True:
        if len(string) == 0:
            return string
        if string[0] == "_":
            string = string[1:]
        else:
            break
    while True:
        if len(string) == 0:
            return string
        if string[-1] == "_":
            string = string[:-1]
        else:
            break
    if string[0].isdigit():
        string = "get_" + string
    return string


def change_name(name):
    """
    Change reserved keywords or names to avoid conflicts in the standardized
    names by prefixing them with 'is_'.

    Args:
        name (str): The name to change.

    Returns:
        str: The changed name if it is in the reserved list, otherwise the original name.
    """
    change_list = ["from", "class", "return", "false", "true", "id", "and"]
    if name in change_list:
        name = "is_" + name
    return name


def standardize_category(category):
    """
    Standardize the category string by replacing spaces, commas, and slashes
    with underscores, and ensuring no consecutive underscores.

    Args:
        category (str): The category string to standardize.

    Returns:
        str: The standardized category string.
    """
    save_category = category.replace(" ", "_").replace(",", "_").replace("/", "_")
    while " " in save_category or "," in save_category:
        save_category = save_category.replace(" ", "_").replace(",", "_")
    save_category = save_category.replace("__", "_")
    return save_category


def process_retrieval_ducoment(documents_df):
    """
    Process the documents dataframe to create two dictionaries:
    1. A dictionary mapping docid to concatenated document details.
    2. A dictionary mapping the concatenated document details to a tab-separated string of category, tool, and API names.

    Args:
        documents_df (DataFrame): DataFrame containing document information.

    Returns:
        tuple: Two dictionaries:
            - ir_corpus: Mapping of docid to concatenated document details.
            - corpus2tool: Mapping of concatenated document details to category, tool, and API names.
    """
    ir_corpus = {}
    corpus2tool = {}
    for row in documents_df.itertuples():
        doc = json.loads(row.document_content)
        ir_corpus[row.docid] = (doc.get('category_name', '') or '') + ', ' + \
                               (doc.get('tool_name', '') or '') + ', ' + \
                               (doc.get('api_name', '') or '') + ', ' + \
                               (doc.get('api_description', '') or '') + \
                               ', required_params: ' + json.dumps(doc.get('required_parameters', '')) + \
                               ', optional_params: ' + json.dumps(doc.get('optional_parameters', '')) + \
                               ', return_schema: ' + json.dumps(doc.get('template_response', ''))
        corpus2tool[(doc.get('category_name', '') or '') + ', ' + \
                    (doc.get('tool_name', '') or '') + ', ' + \
                    (doc.get('api_name', '') or '') + ', ' + \
                    (doc.get('api_description', '') or '') + \
                    ', required_params: ' + json.dumps(doc.get('required_parameters', '')) + \
                    ', optional_params: ' + json.dumps(doc.get('optional_parameters', '')) + \
                    ', return_schema: ' + json.dumps(doc.get('template_response', ''))] = doc['category_name'] + '\t' + \
                                                                                          doc['tool_name'] + '\t' + doc[
                                                                                              'api_name']
    return ir_corpus, corpus2tool
