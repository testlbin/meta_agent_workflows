import requests
from tqdm import tqdm
import pandas as pd
import re
import json
import argparse
from rerank_Template import *

def read_query_file(file_path):
    """
    Read the query file and return a dictionary of queries.
    Args:
        file_path (str): Path to the query file, each line format: qid\tquery
    Returns:
        dict: {qid: query}
    """
    queries = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split('\t')
            qid = parts[0]
            query = parts[1]
            queries[qid] = query
    return queries

def read_corpus_file(file_path):
    """
    Read the corpus file and return a dictionary of workflow contents.
    Args:
        file_path (str): Path to the corpus file, each line format: wocid\tworkflow_content
    Returns:
        dict: {wocid: workflow_content}
    """
    workflows = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split('\t')
            wocid = parts[0]
            workflow_content = parts[1]
            workflows[wocid] = workflow_content
    return workflows

def read_top_file(file_path):
    """
    Read the top retrieval result file and return a mapping from qid to a list of retrieval ids.
    Args:
        file_path (str): Path to the top retrieval result file, each line format: qid\tretrieval_id1,retrieval_id2,...
    Returns:
        dict: {qid: [retrieval_id1, retrieval_id2, ...]}
    """
    top_mappings = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split('\t')
            qid = parts[0]
            retrieval_ids = parts[1].split(',')
            top_mappings[qid] = retrieval_ids
    return top_mappings

def generate_prompts(queries, workflows, tops, template):
    """
    Generate prompt inputs based on queries, workflows, and top retrieval results.
    Args:
        queries (dict): Query dictionary {qid: query}
        workflows (dict): Workflow content dictionary {wocid: workflow_content}
        tops (dict): Top retrieval results {qid: [wocid1, wocid2, ...]}
        template (str): Prompt template
    Returns:
        list: List of prompt inputs, each item is {'query_id': qid, 'input': prompt}
    """
    prompts = []
    for qid, query in queries.items():
        if qid in tops:
            # Build candidate workflows, numbering starts from 1
            candidate_workflows = {idx + 1: workflows[wocid] for idx, wocid in enumerate(tops[qid]) if wocid in workflows}
            # Fill the template
            filled_template = template.format(
                query=query,
                workflow_1=candidate_workflows.get(1, "No workflow available"),
                workflow_2=candidate_workflows.get(2, "No workflow available"),
                workflow_3=candidate_workflows.get(3, "No workflow available"),
                workflow_4=candidate_workflows.get(4, "No workflow available"),
                workflow_5=candidate_workflows.get(5, "No workflow available"),
                workflow_6=candidate_workflows.get(6, "No workflow available"),
                workflow_7=candidate_workflows.get(7, "No workflow available"),
                workflow_8=candidate_workflows.get(8, "No workflow available"),
                workflow_9=candidate_workflows.get(9, "No workflow available"),
                workflow_10=candidate_workflows.get(10, "No workflow available")
            )
            prompts.append({'query_id': qid, 'input': filled_template})
    return prompts

def sglang_inference_and_save(prompts, output_json_path, sglang_url, model_name):
    """
    Use SGLang to perform inference on prompts and save the results as a JSON file.
    Args:
        prompts (list): List of prompt dicts.
        output_json_path (str): Path to save the inference results.
        sglang_url (str): SGLang API URL.
        model_name (str): SGLang model name.
    """
    results = []
    for item in tqdm(prompts, desc="SGLang inference", total=len(prompts)):
        query_id = item['query_id']
        prompt = item['input']
        try:
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": ""},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.0,
                "max_tokens": 1024
            }
            response = requests.post(sglang_url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                output = data["choices"][0]["message"]["content"]
            else:
                output = ""
        except Exception as e:
            print(f"Inference failed: {query_id}, error: {e}")
            output = f"Error: {e}"
        results.append({
            "query_id": query_id,
            "output": output
        })

    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(f"SGLang inference results saved to: {output_json_path}")

def evaluate_accuracy(response_json_path, top_tsv_path):
    """
    Evaluate accuracy based on SGLang inference results and top-k retrieval file.
    Args:
        response_json_path (str): Path to SGLang inference result JSON.
        top_tsv_path (str): Path to top-k retrieval result TSV.
    Returns:
        float: Accuracy value.
    """
    # Load SGLang inference results
    with open(response_json_path, 'r', encoding='utf-8') as file:
        response_data = json.load(file)

    # Extract <numbers> from output for each query_id
    response_dict = {}
    for item in response_data:
        query_id = item["query_id"]
        numbers_match = re.search(r'<numbers>(\d+)</numbers>', item["output"])
        if numbers_match:
            response_dict[query_id] = int(numbers_match.group(1))

    # Load top-k retrieval results
    top_df = pd.read_csv(top_tsv_path, sep='\t')
    top_df['retrieval_ids'] = top_df['retrieval_ids'].apply(lambda x: [int(id) for id in x.split(',')])

    # Calculate accuracy
    def is_correct(row):
        idx = response_dict.get(row['qid'])
        return idx is not None and row['retrieval_ids'][idx - 1] == row['qid']

    top_df['is_correct'] = top_df.apply(is_correct, axis=1)
    accuracy = top_df['is_correct'].mean()
    return accuracy

def parse_args():
    parser = argparse.ArgumentParser(description="Rerank generation and evaluation script")
    parser.add_argument('--query_file', type=str, required=True, help='Path to the query file')
    parser.add_argument('--corpus_file', type=str, required=True, help='Path to the corpus file')
    parser.add_argument('--top_file', type=str, required=True, help='Path to the top-k retrieval result file')
    parser.add_argument('--prompts_json_path', type=str, default='prompts_top10.json', help='Path to save generated prompts')
    parser.add_argument('--output_json_path', type=str, default='rerank_data/sglang_top10.json', help='Path to save SGLang inference results')
    parser.add_argument('--sglang_url', type=str, default='http://127.0.0.1:30000/v1/chat/completions', help='SGLang API URL')
    parser.add_argument('--model_name', type=str, required=True, help='SGLang model name')
    parser.add_argument('--template_type', type=str, default='sglang', choices=['top10'], help='Prompt template type')
    return parser.parse_args()

def main():
    args = parse_args()

    # Select template
    if args.template_type == 'sglang':
        template = rerank_Template_for_SGLang_top10
    else:
        raise ValueError("Unsupported template type.")

    # Step 1: Read data and generate prompts
    queries = read_query_file(args.query_file)
    workflows = read_corpus_file(args.corpus_file)
    tops = read_top_file(args.top_file)
    prompts = generate_prompts(queries, workflows, tops, template)

    # Save prompts to JSON
    with open(args.prompts_json_path, 'w', encoding='utf-8') as f:
        json.dump(prompts, f, ensure_ascii=False, indent=4)
    print(f"Prompts have been saved to '{args.prompts_json_path}'.")

    # Step 2: SGLang inference and save results
    sglang_inference_and_save(prompts, args.output_json_path, args.sglang_url, args.model_name)

    # Step 3: Evaluate accuracy
    accuracy = evaluate_accuracy(args.output_json_path, args.top_file)
    print(f'Accuracy: {accuracy:.2%}')

if __name__ == "__main__":
    main()

"""
Example usage:
python rerank_generation.py \
    --query_file data/query.txt \
    --corpus_file data/corpus.tsv \
    --top_file data/top_10.tsv \
    --prompts_json_path prompts_top10.json \
    --output_json_path rerank_data/sglang_top10.json \
    --sglang_url http://127.0.0.1:30000/v1/chat/completions \
    --model_name path/to/your/model/Llama-3.1-8B-Instruct \
    --template_type sglang
"""
