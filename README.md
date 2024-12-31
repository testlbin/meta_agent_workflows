# Meta Agent Workflow
This is repo of paper 'Meta Agent Workflows: Streamlining Tool Usage in LLMs through Workflow Construction, Retrieval, and Refinement'.

# Start

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

### Meta-Workflow


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


## Retrieval

building...

