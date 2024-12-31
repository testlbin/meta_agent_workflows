import os
import json
import re
import argparse
from tqdm import tqdm
from prompt_Template import workflow_Plan_Prompt
from .utils import extract_successful_finish_trajectories


def process_files(directory, output_file):
    """
    Processes all JSON files in a specified directory, extracts successful dialogue trajectories that meet certain conditions, and generates prompts based on the template.

    Args:
        directory (str): The directory path that contains the input JSON files
        output_file (str): The path to the output JSON file for saving the generated prompts

    Returns:
        None
    """
    answers = {}
    prompts = []
    pattern = re.compile(r"(\d+)_trajectory")
    n = 0

    for filename in tqdm(os.listdir(directory), desc="Processing JSON files"):
        match = pattern.match(filename)
        if match:
            number = int(match.group(1))
            file_path = os.path.join(directory, filename)

            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                    if data.get("win") is not True:
                        print(f"Skipping file {filename}, 'win' is not true")
                        continue

                    if "answer_generation" in data and "train_messages" in data["answer_generation"]:
                        filtered_messages = [
                            [message for message in train_message if message.get("role") != "system"]
                            for train_message in data["answer_generation"]["train_messages"]
                        ]
                        filtered_messages = [msg for msg in filtered_messages if msg]
                        data["answer_generation"]["train_messages"] = filtered_messages

                        successful_trajectories = extract_successful_finish_trajectories(data["answer_generation"])

                        if successful_trajectories:
                            answers[f"{number}_trajectory"] = {
                                "final_answer": data["answer_generation"]["final_answer"],
                                "message": successful_trajectories,
                                "query": data["answer_generation"]["query"]
                            }

                            filled_prompt = workflow_Plan_Prompt.format(content=data["answer_generation"])
                            prompt_entry = {
                                "trajectory_index": number,
                                "input": filled_prompt
                            }
                            prompts.append(prompt_entry)
                            n += 1
                        else:
                            print(f"No successful trajectory in {filename}")
                    else:
                        print(f"Key 'answer_generation' or 'train_messages' not found in {filename}")
            except json.JSONDecodeError:
                print(f"Error decoding JSON in file {filename}")
            except Exception as e:
                print(f"An error occurred with file {filename}: {e}")

    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(prompts, outfile, ensure_ascii=False, indent=4)

    print(f"All prompts have been saved to {output_file}. {n} prompts generated.")


def main():
    parser = argparse.ArgumentParser(description="Process JSON files and generate workflow prompts.")
    parser.add_argument('directory', type=str, help="Directory containing input JSON files")
    parser.add_argument('output_file', type=str, help="Output file path to save the generated prompts")

    args = parser.parse_args()

    process_files(args.directory, args.output_file)


if __name__ == "__main__":
    main()
