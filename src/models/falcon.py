import os
hf_access_token = os.environ['HF_ACCESS_TOKEN']

from huggingface_hub import login
login(token=hf_access_token)

import torch
from transformers import pipeline
import json
import re

def load_pipe(config):
    model_id = config['model']

    return pipeline(
        "text-generation",
        model=model_id,
        model_kwargs={"torch_dtype": torch.bfloat16,
                  "low_cpu_mem_usage": True,
                  },
        device_map="auto",
    )

# Function to chat with falcon
def generate_response(pipe=None, prompt='', config=None):

    # Simple check for a valid last sentence in the story
    def complete_response(response):
        if re.search(r'The criminal is (\w+)', response):
            return True
        else:
            print(f'Generated story is incomplete! Trying again...')
            return False

    if not pipe:
        print("Error: You did not provide a pipeline for the model.")
        SystemExit(0)
    
    messages = config['messages'] 
    messages[1]['content'] = prompt # including system prompt and general story prompt
    kwargs = config.copy()
    del kwargs['messages']
    del kwargs['model']


    while True: # Loop until a valid story is generated
        response = pipe(
            messages,
            eos_token_id=pipe.tokenizer.eos_token_id,
            **kwargs,
        )

        generated_story = response[0]["generated_text"][-1]['content']
        
        if complete_response(generated_story):
            break

    return generated_story

def main():

    import sys
    from pathlib import Path

    # Add the parent directory to the Python path
    parent_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(parent_root))

    # Load model configuration
    with open('src/config/falcon_config.json', 'r') as config_file:
        config = json.load(config_file)
    
    prompt = 'Create a short story.'


    print(f'\nInput: {prompt}')
    print(f'{generate_response(pipe = load_pipe(config), prompt=prompt, config=config)}\n')

if __name__ == "__main__":
    main()
