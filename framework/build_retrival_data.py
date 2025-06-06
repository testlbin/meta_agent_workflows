import json
import argparse
import os
from tqdm import tqdm
import pandas as pd
from sklearn.utils import shuffle

"""
Build the retrieval dataset for tool matching.
"""

def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="Retrieval dataset builder")
    parser.add_argument('--output_dir', type=str, default="data/test",
                        help='The directory to output the split files')
    parser.add_argument('--query_file', type=str,
                        default="data/instruction/G1_query.json",
                        help='The name of the query file')
    parser.add_argument('--index_file', type=str,
                        default="data/test_query_ids/test_1.json",
                        help='The name of the index file')
    parser.add_argument('--dataset_name', type=str, default="G1", help='The name of the output dataset')
    return parser.parse_args()

def load_json(file_path):
    """
    Load a JSON file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def split_test_set(query_data, test_index_set):
    """
    Split test set according to index set.
    """
    test_set = []
    for index, item in tqdm(enumerate(query_data), desc="Selecting test set"):
        if "query_id" in item:
            index = item["query_id"]
        if index in test_index_set:
            test_set.append(item)
    return test_set

def process_data(data, doc_id_map, query_id_map, documents, pairs):
    """
    Process data to generate document and pair information.

    :param data: input data
    :param doc_id_map: mapping from document to doc_id
    :param query_id_map: mapping from query to query_id
    :param documents: document list
    :param pairs: pair list
    """
    for doc in tqdm(data, desc="Processing data"):
        for api in doc['api_list']:
            document_content = api
            api_identity = [api['tool_name'], api['api_name']]
            # doc_id Assign a unique doc_id for each API
            doc_id = doc_id_map.setdefault(json.dumps(document_content, sort_keys=True), len(doc_id_map) + 1)
            documents.append([doc_id, json.dumps(document_content, ensure_ascii=False)])
            # API Check if the current API is in the relevant APIs
            if api_identity in doc['relevant APIs']:
                query = doc['query']
                if isinstance(query, list):
                    query = query[0]  # Some instances store query as a list
                # query_id Assign a unique query_id for each query
                query_id = query_id_map.setdefault(query, len(query_id_map) + 1)
                pairs.append(([query_id, query], [query_id, 0, doc_id, 1]))

def main():
    args = parse_args()

    # Load query data
    query_data = load_json(args.query_file)
    # Load test set index
    test_index_data = load_json(args.index_file)
    # Convert to set for fast lookup
    test_index_set = set(map(int, test_index_data.keys()))

    # Split test set
    query_test = split_test_set(query_data, test_index_set)

    # Initialize mappings and data structures
    doc_id_map = {}    # Mapping from document to doc_id
    query_id_map = {}  # Mapping from query to query_id
    documents = []     # Document content list
    test_pairs = []    # Test set pairs

    # Process data and generate pairs
    process_data(query_test, doc_id_map, query_id_map, documents, test_pairs)

    # Shuffle pairs
    test_pairs = shuffle(test_pairs, random_state=42)

    # Split into queries and labels
    test_queries, test_labels = zip(*test_pairs)

    # DataFrame Build DataFrames
    documents_df = pd.DataFrame(documents, columns=['docid', 'document_content'])
    test_queries_df = pd.DataFrame(test_queries, columns=['qid', 'query_text'])
    test_labels_df = pd.DataFrame(test_labels, columns=['qid', 'useless', 'docid', 'label'])

    """
    documents_df: Save tool API text information
    test_queries_df: Save query text information
    test_labels_df: Save label information (association between query and tool)
    """

    # Save as .tsv and .txt files
    os.makedirs(args.output_dir, exist_ok=True)
    documents_df.to_csv(os.path.join(args.output_dir, 'corpus.tsv'), sep='\t', index=False)
    test_queries_df.to_csv(os.path.join(args.output_dir, 'test.query.txt'), sep='\t', index=False, header=False)
    test_labels_df.to_csv(os.path.join(args.output_dir, 'qrels.test.tsv'), sep='\t', index=False, header=False)

if __name__ == "__main__":
    main()
    # example:
    # python build_retrival_data.py --output_dir data/test --query_file data/instruction/G1_query.json --index_file data/test_query_ids/test_1.json --dataset_name G1