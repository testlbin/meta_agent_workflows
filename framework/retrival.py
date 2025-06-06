import time
import json
import pandas as pd
import argparse
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm

def parse_args():
    parser = argparse.ArgumentParser(description="Workflow Retrieval Script")
    parser.add_argument('--query_file', type=str, default='retrieve/query.txt', help='Path to the query file')
    parser.add_argument('--corpus_tsv', type=str, default='retrieve/corpus.tsv', help='Path to the corpus TSV file')
    parser.add_argument('--model_path', type=str, default='ToolBench/ToolBench_IR_bert_based_uncased', help='Path to the sentence transformer model')
    parser.add_argument('--output_file', type=str, default='retrieve/retrieval_top5.tsv', help='Path to save the retrieval results')
    parser.add_argument('--top_k', type=int, default=5, help='Number of top results to retrieve')
    return parser.parse_args()

def process_retrieval_document(documents_df):
    """
    Process the input DataFrame to build the IR corpus and mapping from content to tool info.

    Args:
        documents_df (pd.DataFrame): DataFrame containing workflow content.

    Returns:
        tuple: (ir_corpus, corpus2tool)
            ir_corpus (dict): {docid: document_content}
            corpus2tool (dict): {document_content: "category_name\tworkflow_description"}
    """
    ir_corpus = {}
    corpus2tool = {}
    for row in documents_df.itertuples():
        doc = json.loads(row.workflow_content)
        category = doc.get('category_name', '') or ''
        description = doc.get('workflow_description', '') or ''
        doc_content = f"{category}, {description}"
        ir_corpus[row.wocid] = doc_content
        corpus2tool[doc_content] = f"{category}\t{description}"
    return ir_corpus, corpus2tool

class WorkflowRetriever:
    """
    WorkflowRetriever is responsible for loading the corpus, building embeddings,
    and retrieving the most relevant tools for a given query.
    """
    def __init__(self, corpus_tsv_path: str = "", model_path: str = ""):
        """
        Initialize the retriever with corpus and model.

        Args:
            corpus_tsv_path (str): Path to the corpus TSV file.
            model_path (str): Path to the sentence transformer model.
        """
        self.corpus_tsv_path = corpus_tsv_path
        self.model_path = model_path
        self.corpus, self.corpus2tool = self.build_retrieval_corpus()
        self.embedder = self.build_retrieval_embedder()
        self.corpus_embeddings = self.build_corpus_embeddings()

    def build_retrieval_corpus(self):
        """
        Load and process the corpus from TSV file.

        Returns:
            tuple: (corpus, corpus2tool)
        """
        print("Building corpus...")
        documents_df = pd.read_csv(self.corpus_tsv_path, sep='\t')
        corpus, corpus2tool = process_retrieval_document(documents_df)
        corpus_ids = list(corpus.keys())
        corpus_list = [corpus[cid] for cid in corpus_ids]
        return corpus_list, corpus2tool

    def build_retrieval_embedder(self):
        """
        Load the sentence transformer model.

        Returns:
            SentenceTransformer: The loaded model.
        """
        print("Building embedder...")
        embedder = SentenceTransformer(self.model_path)
        return embedder

    def build_corpus_embeddings(self):
        """
        Encode the corpus into embeddings.

        Returns:
            np.ndarray: Corpus embeddings.
        """
        print("Building corpus embeddings with embedder...")
        corpus_embeddings = self.embedder.encode(self.corpus, convert_to_tensor=True)
        return corpus_embeddings

    def retrieving(self, query: str, top_k: int = 5):
        """
        Retrieve the top-k relevant tools for a given query.

        Args:
            query (str): The input query.
            top_k (int): Number of top results to return.

        Returns:
            tuple: (retrieved_tools, retrieved_ids)
                retrieved_tools (list): List of dicts with tool info.
                retrieved_ids (list): List of retrieved document contents.
        """
        print("Retrieving...")
        query_embedding = self.embedder.encode(query, convert_to_tensor=True)
        hits = util.semantic_search(
            query_embedding, self.corpus_embeddings, top_k=5 * top_k, score_function=util.cos_sim
        )
        retrieved_tools = []
        retrieved_ids = []
        for hit in hits[0]:
            doc_content = self.corpus[hit['corpus_id']]
            retrieved_ids.append(doc_content)
            category, description = self.corpus2tool[doc_content].split('\t')
            tool_info = {
                "category": category,
                "workflow_description": description
            }
            retrieved_tools.append(tool_info)
        return retrieved_tools, retrieved_ids

def main():
    args = parse_args()
    query_file_path = args.query_file
    model_path = args.model_path
    corpus_tsv_path = args.corpus_tsv
    output_file_path = args.output_file
    top_k = args.top_k

    # Load queries
    query_df = pd.read_csv(query_file_path, sep='\t', names=['qid', 'query'])

    # Initialize retriever
    retriever = WorkflowRetriever(corpus_tsv_path=corpus_tsv_path, model_path=model_path)

    # Retrieval results
    results = []

    # Process each query and collect retrieval results
    for _, row in tqdm(query_df.iterrows(), total=query_df.shape[0], desc="Processing Queries"):
        _, retrieved_ids = retriever.retrieving(row['query'], top_k=top_k)
        results.append({
            'qid': row['qid'],
            'retrieval_ids': ','.join(map(str, retrieved_ids))
        })

    # Save results to file
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file_path, sep='\t', index=False)

    # Evaluate retrieval accuracy
    results_df = pd.read_csv(output_file_path, sep='\t')

    def is_correct_retrieval(row):
        """
        Check if the query id is in the retrieved ids.

        Args:
            row (pd.Series): Row of the DataFrame.

        Returns:
            bool: True if correct, False otherwise.
        """
        retrieval_ids = list(map(str, row['retrieval_ids'].split(',')))
        return str(row['qid']) in retrieval_ids

    results_df['is_correct'] = results_df.apply(is_correct_retrieval, axis=1)
    accuracy = results_df['is_correct'].mean()
    print(f"Retrieval Accuracy: {accuracy:.2%}")

if __name__ == "__main__":
    main()
    # python Retrival.py --query_file retrieve/query.txt --corpus_tsv retrieve/corpus.tsv --model_path ToolBench/ToolBench_IR_bert_based_uncased --output_file retrieve/retrieval_top5.tsv --top_k 5
