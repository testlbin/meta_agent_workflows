import json
import openai
import re
import argparse
from tqdm import tqdm
from framework.prompt_Template import workflow_Plan_Prompt

client = openai.Client(
    base_url="http://127.0.0.1:30000/v1",
    api_key="EMPTY"
)

def generate_responses(prompts_file, responses_file, output_file_path):
    with open(prompts_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    responses = {}

    for key, value in tqdm(data.items(), desc="Generating responses", total=len(data)):
        try:
            response = client.chat.completions.create(
                model="default",
                messages=[
                    {"role": "system", "content": workflow_Plan_Prompt},
                    {"role": "user", "content": value},
                ],
                temperature=0.6,
                max_tokens=4096,
            )

            message_content = response.choices[0].message.content
            responses[f"{key}_output"] = message_content

        except Exception as e:
            print(f"Error generating response for {key}: {e}")
            responses[f"{key}_output"] = f"Error: {e}"

    with open(responses_file, 'w', encoding='utf-8') as outfile:
        json.dump(responses, outfile, ensure_ascii=False, indent=4)

    print(f"All responses have been saved to {responses_file}")

def process_responses(responses_file, output_file_path):
    explanation_pattern = re.compile(r'<explanation>(.*?)</explanation>', re.DOTALL)
    workflow_pattern = re.compile(r'<workflow>(.*?)</workflow>', re.DOTALL)

    with open(responses_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    processed_data = {}
    for key, value in data.items():
        numbers_prefix = key.split('_')[0]
        new_key = f"{numbers_prefix}_trajectory"

        explanation_content = explanation_pattern.search(value)
        workflow_content = workflow_pattern.search(value)

        processed_data[new_key] = {
            "explanation": explanation_content.group(1).strip() if explanation_content else "",
            "workflow": workflow_content.group(1).strip() if workflow_content else ""
        }

    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(processed_data, file, indent=4)

    print(f"Processed JSON saved to {output_file_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate responses and process workflow data.")

    parser.add_argument('--prompts_file', type=str, required=True, help="Path to the input JSON file containing prompts.")
    parser.add_argument('--responses_file', type=str, required=True, help="Path to save the responses JSON file.")
    parser.add_argument('--output_file', type=str, required=True, help="Path to save the final processed output JSON file.")

    args = parser.parse_args()

    generate_responses(args.prompts_file, args.responses_file, args.responses_file)
    process_responses(args.responses_file, args.output_file)

if __name__ == "__main__":
    main()
