import json
from openai import OpenAI
client = OpenAI()

# Function to chat with OpenAI
def generate_response(prompt, config):
    messages = config['messages'] # including system prompt and general story prompt
    messages[1]['content'] = prompt
    kwargs = config.copy()
    del kwargs['messages']
    
    response = client.chat.completions.create(
        messages=messages,
        **kwargs
    )
    return response.choices[0].message.content

def main():
    import sys
    from pathlib import Path

    # Add the parent directory to the Python path
    parent_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(parent_root))

    # Load model configuration
    with open('src/config/chatgpt_config.json', 'r') as config_file:
        config = json.load(config_file)
    
    prompt = 'Create a short story.'

    print(f'\nInput: {prompt}')
    print(f'{generate_response(prompt, config)}\n')

if __name__ == "__main__":
    main()