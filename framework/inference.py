import os
import json
import argparse
import sglang as sgl
from tqdm import tqdm
from framework.utils import standardize, change_name
from prompt_Template import json_regex, require

# --- SGL Function for Character Generation ---
@sgl.function
def character_gen(s, name, user):
    s += (
        "You are a workflow node generation assistant. Based on the information provided by the user, you need to generate a JSON for the node. "
        "Please fill in the following config about this workflow node.\n"
    )
    s += "The require is:\n"
    s += require
    s += user
    s += "The constrained regex is:\n"
    s += json_regex + "\n"
    s += "The JSON output is:\n"
    s += sgl.gen("json_output", max_tokens=2048, regex=json_regex)

# --- Functions for HTTP Request Handling ---
def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def save_new_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def update_http_requests(data, updates):
    for item in data:
        workflow_details = item.get('workflow_details', {})
        for key in list(workflow_details.keys()):
            if key in updates:
                workflow_details[key] = updates[key]
    return data

def extract_http_requests(data):
    http_requests = {}
    for item in data:
        workflow_details = item.get('workflow_details', {})
        for key, value in workflow_details.items():
            if key.startswith('HTTP'):
                http_requests[key] = value
    return http_requests

def driver_character_gen(name, user_information):
    state = character_gen.run(name=name, user=user_information)
    result = state.text()
    json_start = result.find('The JSON output is:\n') + 20
    json_str = result[json_start:]
    try:
        json_data = json.loads(json_str)
        return json_data
    except json.JSONDecodeError:
        print(f"Failed to decode JSON for {name}")
        print(json_str)
        return {}

# --- Functions for Tool and API Data Processing ---
def get_white_list(tool_root_dir):
    white_list_dir = os.path.join(tool_root_dir)
    white_list = {}
    for cate in tqdm(os.listdir(white_list_dir)):
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

def contain(candidate_list, white_list):
    output = []
    for cand in candidate_list:
        if cand not in white_list.keys():
            return False
        output.append(white_list[cand])
    return output

def build_tool_description(data_dict, white_list, tool_root_dir):
    origin_tool_names = [standardize(cont["tool_name"]) for cont in data_dict["api_list"]]
    tool_des = contain(origin_tool_names, white_list)
    tool_descriptions = [[cont["standard_tool_name"], cont["description"]] for cont in tool_des]
    return tool_descriptions

def fetch_api_json(query_json, tool_root_dir):
    data_dict = {"api_list": []}
    for item in query_json["api_list"]:
        cate_name = item["category_name"]
        tool_name = standardize(item["tool_name"])
        api_name = change_name(standardize(item["api_name"]))

        tool_json = json.load(open(os.path.join(tool_root_dir, cate_name, tool_name + ".json"), "r", encoding='utf-8'))
        append_flag = False
        api_dict_names = []
        for api_dict in tool_json["api_list"]:
            api_dict_names.append(api_dict["name"])
            pure_api_name = change_name(standardize(api_dict["name"]))
            if pure_api_name != api_name:
                continue
            api_json = {}
            api_json["category_name"] = cate_name
            api_json["api_name"] = api_dict["name"]

            api_json['code_cate'] = item["category_name"]
            api_json['code_tool'] = item["tool_name"]
            api_json['code_api'] = item["api_name"]

            api_json["api_description"] = api_dict["description"]
            api_json["required_parameters"] = api_dict["required_parameters"]
            api_json["optional_parameters"] = api_dict["optional_parameters"]
            api_json["tool_name"] = tool_json["tool_name"]
            data_dict["api_list"].append(api_json)
            append_flag = True
            break
        if not append_flag:
            print(api_name, api_dict_names)
    return data_dict

def api_json_to_openai_json(api_json, standard_tool_name):
    description_max_length = 256
    templete = {
        "name": "",
        "origin_api_name": "",
        "cate_name": "",
        "code_cate": "",
        "code_tool": "",
        "code_api": "",
        "description": "",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "optional": [],
        }
    }

    map_type = {
        "NUMBER": "integer",
        "STRING": "string",
        "BOOLEAN": "boolean"
    }

    pure_api_name = change_name(standardize(api_json["api_name"]))
    templete["name"] = pure_api_name + f"_for_{standard_tool_name}"
    templete["name"] = templete["name"][-64:]
    templete["origin_api_name"] = pure_api_name + f"_for_{standard_tool_name}"
    templete["cate_name"] = api_json["category_name"]
    templete["code_cate"] = api_json["code_cate"]
    templete["code_tool"] = api_json["code_tool"]
    templete["code_api"] = api_json["code_api"]

    templete["description"] = f"This is the subfunction for tool \"{standard_tool_name}\", you can use this tool."

    if api_json["api_description"].strip() != "":
        tuncated_description = api_json['api_description'].strip().replace(api_json['api_name'], templete['name'])[
                               :description_max_length]
        templete["description"] = templete[
                                      "description"] + f"The description of this function is: \"{tuncated_description}\""

    if "required_parameters" in api_json.keys() and len(api_json["required_parameters"]) > 0:
        for para in api_json["required_parameters"]:
            name = standardize(para["name"])
            name = change_name(name)
            if para["type"] in map_type:
                param_type = map_type[para["type"]]
            else:
                param_type = "string"
            prompt = {
                "type": param_type,
                "description": para["description"][:description_max_length],
            }

            default_value = para['default']
            if len(str(default_value)) != 0:
                prompt = {
                    "type": param_type,
                    "description": para["description"][:description_max_length],
                    "example_value": default_value
                }
            else:
                prompt = {
                    "type": param_type,
                    "description": para["description"][:description_max_length]
                }

            templete["parameters"]["properties"][name] = prompt
            templete["parameters"]["required"].append(name)
        for para in api_json["optional_parameters"]:
            name = standardize(para["name"])
            name = change_name(name)
            if para["type"] in map_type:
                param_type = map_type[para["type"]]
            else:
                param_type = "string"

            default_value = para['default']
            if len(str(default_value)) != 0:
                prompt = {
                    "type": param_type,
                    "description": para["description"][:description_max_length],
                    "example_value": default_value
                }
            else:
                prompt = {
                    "type": param_type,
                    "description": para["description"][:description_max_length]
                }

            templete["parameters"]["properties"][name] = prompt
            templete["parameters"]["optional"].append(name)

    return templete

def process_queries(file_path, output_file, tool_root_dir):
    white_list = get_white_list(tool_root_dir)

    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    processed_data = []

    for item in tqdm(data):
        data_dict = fetch_api_json(item, tool_root_dir)
        tool_descriptions = build_tool_description(data_dict, white_list, tool_root_dir)

        item_result = {
            "query_id": item["query_id"],
            "processed_apis": []
        }

        for k, api_json in enumerate(data_dict["api_list"]):
            if k < len(tool_descriptions):
                standard_tool_name = tool_descriptions[k][0]
                openai_function_json = api_json_to_openai_json(api_json, standard_tool_name)
                item_result["processed_apis"].append(openai_function_json)

        processed_data.append(item_result)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, indent=4)

    print(f"Processed data saved to {output_file}")

# --- Main Function to Combine Both Processes ---
def main_processing(input_file, output_file, query_file, tool_root_dir, sgl_url):
    sgl.set_default_backend(sgl.RuntimeEndpoint(sgl_url))

    data = load_data(input_file)

    http_requests = extract_http_requests(data)
    updates = {}
    for request_name in tqdm(http_requests.keys(), desc="Processing HTTP requests"):
        request_details = http_requests[request_name]
        if not request_details:
            continue
        new_details = driver_character_gen(name=request_name, user_information=request_details)
        updates[request_name] = new_details

    updated_data = update_http_requests(data, updates)

    process_queries(input_file, query_file, tool_root_dir)

    save_new_json(updated_data, output_file)

# --- Argument Parsing and Execution ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process workflow templates, API queries, and generate JSON outputs.")
    parser.add_argument('--input_file', type=str, required=True, help="Path to the input JSON file.")
    parser.add_argument('--output_file', type=str, required=True, help="Path to save the output JSON file.")
    parser.add_argument('--query_file', type=str, required=True, help="Path to save the query JSON file.")
    parser.add_argument('--tool_root_dir', type=str, required=True, help="Root directory of the tool JSON files.")
    parser.add_argument('--sgl_url', type=str, default="http://localhost:30000", help="URL of the SGL backend.")

    args = parser.parse_args()

    main_processing(args.input_file, args.output_file, args.query_file, args.tool_root_dir, args.sgl_url)
