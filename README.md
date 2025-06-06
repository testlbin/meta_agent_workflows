# Meta Agent Workflow
This is repo of paper 'Meta Agent Workflows: Streamlining Tool Usage in LLMs through Workflow Construction, Retrieval, and Refinement'.

## Dify & SGLang

For Dify deployment, you can follow the official tutorial: [Dify GitHub](https://github.com/langgenius/dify)

For SGLang, follow the official tutorial: [SGLang Installation Guide](https://sgl-project.github.io/start/install.html)

## Data

ToolBench Data: [ToolBench GitHub Repository](https://github.com/OpenBMB/ToolBench?tab=readme-ov-file#data)

## Start SGLang

To start SGLang, run the following command:

```bash
python -m sglang.launch_server --model-path path/to/your/model/Llama-3.1-8B-Instruct --port 30000
```

## Meta-Workflow


To extract the trajectory from ToolBench data, place the ToolBench data in the `data` folder and then run the following command:

```bash
python framework/planning_prompt.py ./data/to/toolbench ./data/to/extract_trajectories.json
```


To extract the tool api information:
```bash
python framework/white_list_api.py
```

Inference Planning Data:

```bash
python framework/planning.py \
--prompts_file data/to/extract_trajectories.json \
--responses_file data/to/responses_extract_trajectories.json \
--output_file data/to/query.json
```

Workflow Generation:

```bash
python framework/inference.py \
--input_file data/to/planning.json \
--output_file data/to/workflow.json \
--tool_root_dir 'data/toolenv/tools' \
--sgl_url http://127.0.0.1:30000
```


## Retrieval and Rerank

### 1. Build Retrieval Data

This script prepares the raw query and API data into a structured format suitable for retrieval.

```bash
python framework/build_retrival_data.py \
    --output_dir data/test \
    --query_file data/instruction/G1_query.json \
    --index_file data/test_query_ids/test.json \
    --dataset_name G1
```
Tip: To quickly validate the workflow on a smaller scale, you can select a subset of query IDs and save them in a JSON file `(e.g., test.json)`. This allows for faster experimentation without processing the full dataset. For the expected format, please refer to the `framework/build_retrival_data.py`.

### 2. Retrieval

This script loads a pre-trained sentence transformer model, builds embeddings for the corpus, and then retrieves the top-k most relevant workflow descriptions for a given set of queries based on semantic similarity.

```bash
python framework/retrival.py \
    --query_file retrieve/query.txt \
    --corpus_tsv retrieve/corpus.tsv \
    --model_path ToolBench/ToolBench_IR_bert_based_uncased \
    --output_file retrieve/retrieval_top10.tsv \
    --top_k 10
```

### 3. Rerank and Evaluation

This script generates prompts (`framework/rerank_Template.py`) for a LLM based on queries and their top-k retrieved workflows. It then sends these prompts to an SGLang API for inference (reranking) and finally evaluates the accuracy of the reranked results.

```bash
python framework/rerank_generation.py \
    --query_file data/query.txt \
    --corpus_file data/corpus.tsv \
    --top_file data/top_10.tsv \
    --prompts_json_path prompts_top10.json \
    --output_json_path rerank_data/sglang_top10.json \
    --sglang_url http://127.0.0.1:30000/v1/chat/completions \
    --model_name path/to/your/model/Llama-3.1-8B-Instruct \
    --template_type sglang
```


# Acknowledgment
We would like to thank the authors of [StableToolbench (Guo et al., 2024)](https://aclanthology.org/2024.findings-acl.664/) for providing a solid foundation for our tool learning evaluation framework. We also gratefully acknowledge [Dify](https://github.com/langgenius/dify) for offering an intuitive and powerful platform for workflow construction, [SGLang](https://sgl-project.github.io/start/install.html) for providing efficient LLM inference services that greatly facilitated our experimental pipeline.

# Citation
```bibtex
@inproceedings{tan2025meta,
  title={Meta-Agent-Workflow: Streamlining Tool Usage in LLMs through Workflow Construction, Retrieval, and Refinement},
  author={Tan, Xiaoyu and Li, Bin and Qiu, Xihe and Qu, Chao and Chu, Wei and Xu, Yinghui and Qi, Yuan},
  booktitle={Companion Proceedings of the ACM on Web Conference 2025},
  pages={458--467},
  year={2025}
}
```
