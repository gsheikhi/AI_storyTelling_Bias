import pandas as pd

# Function to create input samples
def generate_story_prompt(text, info):
    if not info.empty:
        # Replace location, countries, religion in the prompt
        text = text.replace('LOC', info['location'])
        text = text.replace('COUNT1', info['origin1']).replace('REL1', info['religion1'])
        text = text.replace('COUNT2', info['origin2']).replace('REL2', info['religion2'])
        text = text.replace('COUNT3', info['origin3']).replace('REL3', info['religion3'])
        text = text.replace('COUNT4', info['origin4']).replace('REL4', info['religion4'])
    
    return text

if __name__ == "__main__":
    generate_story_prompt('', pd.DataFrame())

