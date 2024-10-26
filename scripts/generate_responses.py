import pandas as pd
import json
from tqdm import tqdm
import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).resolve().parents[1]  # Adjust the number based on how deep the script is
sys.path.insert(0, str(project_root))

from src.models import chatgpt, claude, gemini

modules = {
        'chatgpt': chatgpt,
        'claude': claude,
        'gemini': gemini
    }

def load_config(model_name):
    with open(f'src/config/{model_name}_config.json', 'r') as f:
        return json.load(f)

def response_generation(model, prompts, config, num_rounds=1):
    responses = [[] for _ in range(num_rounds)]  # responses for all rounds and prompts
    tqdm.write(f'Total prompts: {len(prompts)}; Generation rounds: {num_rounds}.')
    for round in range(num_rounds):
        response_list = []  # response list for one round
        print(f'Generation round {round+1}:', flush=True)
        
        for prompt in tqdm(prompts, file=sys.stdout, dynamic_ncols=True,
                           desc=f"Round {round+1}", unit="prompt"):
            response = model.generate_response(prompt, config)
            response_list.append(response)
            sys.stdout.flush()
        
        responses[round] = response_list
    return responses

def main():
    # General config for experiments
    with open('general_config.json', 'r') as f:
        config = json.load(f)
    num_requests, num_rounds, models = [config["number_of_request"], 
                                        config["num_generation_rounds"],
                                        config["testing_models"]]

    # Load input prompts
    input_df = pd.read_csv('data/processed/input_texts.csv', sep=';', header=0)
    prompts = input_df['prompt'].tolist()
    prompts = prompts[0:min(num_requests, len(prompts))] # select as many as num_request prompts

    # Generate and save responses for each testing model
    for model_name, model_module in modules.items():
        if model_name in models:
            config = load_config(model_name)
            print(f'\n********** Generating Responses by {model_name} **********')
            responses = response_generation(model_module, prompts, config, num_rounds)

            response_dict ={} # initialize response dictionary
            for round in range(num_rounds):
                response_dict[f'round{round+1}'] = responses[round] # generated response for each round
            
            # Create a DataFrame with the responses
            response_df = pd.DataFrame(response_dict)

            # Save to CSV
            response_df.to_csv(f'data/processed/{model_name}_responses.csv', sep=';', index=False)
            print(f"Generated responses for {model_name} saved to data/results/{model_name}_responses.csv")

if __name__ == "__main__":
    main()