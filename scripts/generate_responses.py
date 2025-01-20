import pandas as pd
import json
from tqdm import tqdm
import sys
from pathlib import Path
import os
import platform

# Functions for batch generation with pause and save/load responses
def pause():
    if platform.system() == "Windows":
        os.system("pause")
    else:
        os.system("read -n 1 -s -p 'Press any key to continue...'")

def save_temp_responses(responses, model_name, round_num, prompt_idx, filename=None):
    if filename is None:
        filename = f'data/temp/{model_name}_round{round_num+1}_checkpoint.json'
    
    temp_data = {
        'responses': responses,
        'current_round': round_num,
        'current_prompt_idx': prompt_idx
    }
    
    os.makedirs('data/temp', exist_ok=True)
    with open(filename, 'w') as f:
        json.dump(temp_data, f)

def load_temp_responses(model_name):
    checkpoint_files = list(Path('data/temp').glob(f'{model_name}_round*_checkpoint.json'))
    
    if checkpoint_files:
        latest_checkpoint = max(checkpoint_files, key=os.path.getctime)
        with open(latest_checkpoint, 'r') as f:
            return json.load(f)
    return None

def clean_temp_files(model_name):
    temp_files = list(Path('data/temp').glob(f'{model_name}_round*_checkpoint.json'))
    for file in temp_files:
        os.remove(file)

# Add the project root directory to the Python path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.models import falcon, qwen, llama, chatgpt, claude

modules = {
    'falcon': falcon,
    'qwen': qwen,
    'llama': llama,
    'chatgpt': chatgpt,
    'claude': claude,
}

def load_config(model_name):
    with open(f'src/config/{model_name}_config.json', 'r') as f:
        return json.load(f)

def response_generation(model, model_name, prompts, config, num_rounds=1, request_batch_size=100):
    pipe = model.load_pipe(config)
    
    # Check for existing temporary saves
    checkpoint_data = load_temp_responses(model_name)
    
    if checkpoint_data:
        responses = checkpoint_data['responses']
        start_round = checkpoint_data['current_round']
        start_prompt_idx = checkpoint_data['current_prompt_idx'] + 1  # Start from next prompt
    else:
        responses = [[] for _ in range(num_rounds)]
        start_round = 0
        start_prompt_idx = 0

    tqdm.write(f'Total prompts: {len(prompts)}; Generation rounds: {num_rounds}')
    tqdm.write(f'Resuming from round {start_round + 1}, prompt {start_prompt_idx + 1}')

    try:
        for round in range(start_round, num_rounds):
            if round == start_round:
                response_list = responses[round] if responses[round] else []
                prompts_to_process = prompts[start_prompt_idx:]
            else:
                response_list = []
                prompts_to_process = prompts

            print(f'Generation round {round + 1}:', flush=True)
            
            for i, prompt in enumerate(tqdm(prompts_to_process, 
                                          initial=start_prompt_idx if round == start_round else 0,
                                          total=len(prompts),
                                          file=sys.stdout, 
                                          dynamic_ncols=True,
                                          desc=f"Round {round + 1}", 
                                          unit="prompt")):
                response = model.generate_response(pipe=pipe, prompt=prompt, config=config)
                response_list.append(response)
                
                current_prompt_idx = start_prompt_idx + i if round == start_round else i
                
                if (current_prompt_idx + 1) % request_batch_size == 0:
                    responses[round] = response_list
                    save_temp_responses(responses, model_name, round, current_prompt_idx)
                    # pause()
                
                sys.stdout.flush()
            
            responses[round] = response_list
            # Save checkpoint at the end of each round
            save_temp_responses(responses, model_name, round, len(prompts) - 1)
            
        return responses
    
    except Exception as e:
        # Save the current state before raising the exception
        if response_list:
            responses[round] = response_list
            save_temp_responses(responses, model_name, round, current_prompt_idx)
        raise e
        sys.exit(0) 
    

def main():
    # General config for experiments
    with open('general_config.json', 'r') as f:
        config = json.load(f)
    
    num_requests, num_rounds, request_batch_size, models = [
        config["number_of_request"],
        config["num_generation_rounds"],
        config["request_batch_size"],
        config["testing_models"]
    ]

    # Load input prompts
    input_df = pd.read_csv('data/processed/input_texts.csv', sep=';', header=0)
    prompts = input_df['prompt'].tolist()
    prompts = prompts[0:min(num_requests, len(prompts))]

    # Generate and save responses for each testing model
    for model_name, model_module in modules.items():
        if model_name in models:
            try:
                config = load_config(model_name)
                print(f'\n********** Generating Responses by {model_name} **********')
                
                responses = response_generation(
                    model=model_module,
                    model_name=model_name,
                    prompts=prompts,
                    config=config,
                    num_rounds=num_rounds,
                    request_batch_size=request_batch_size
                )

                response_dict = {}
                for round in range(num_rounds):
                    response_dict[f'round{round+1}'] = responses[round]

                # Create a DataFrame with the responses
                response_df = pd.DataFrame(response_dict)

                # Save to CSV
                response_df.to_csv(f'data/processed/{model_name}_responses.csv', sep=';', index=False)
                print(f"Generated responses for {model_name} saved to data/processed/{model_name}_responses.csv")
                
                # Clean up temporary files after successful completion
                clean_temp_files(model_name)
                
            except Exception as e:
                print(f"Error processing {model_name}: {str(e)}")
                continue  # Move to next model if there's an error

if __name__ == "__main__":
    main()