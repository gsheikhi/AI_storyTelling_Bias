import json
import re
import anthropic
client = anthropic.Anthropic()

def load_pipe(config=None):
    return None

# Function to chat with OpenAI
def generate_response(pipe=None, prompt='', config=None):

    # Simple check for a valid last sentence in the story
    def complete_response(response):
        if re.search(r'The criminal is (\w+)', response):
            return True
        else:
            print(f'Generated story is incomplete! Trying again...')
            return False
        
    if pipe:
        print("Warning: You provided a pipeline for the model, but this model does not use it.")
    
    if prompt == '':
        print("Warning: You provided an empty prompt.")

    messages = config['messages'] # including system prompt and general story prompt
    messages[0]['content'][0]['text'] = prompt
    kwargs = config.copy()
    del kwargs['messages']

    while True:
        response = client.messages.create(
            messages=messages,
            **kwargs
        )
        generated_story = response.content[0].text

        if complete_response(generated_story):
            break
    
    return  generated_story

def main():
    import sys
    from pathlib import Path

    # Add the parent directory to the Python path
    parent_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(parent_root))

    # Load model configuration
    with open('src/config/claude_config.json', 'r') as config_file:
        config = json.load(config_file)
    
    prompt = 'Create a short story.'

    print(f'\nInput: {prompt}')
    print(f'{generate_response(prompt=prompt, config=config)}\n')

if __name__ == "__main__":
    main()