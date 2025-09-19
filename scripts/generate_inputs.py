import pandas as pd
import json
from collections import Counter
import random
import os
import sys
from pathlib import Path

# Add the root directory to the Python path
project_root = Path(__file__).resolve().parents[1]  # Adjust the number based on how deep the script is
sys.path.insert(0, str(project_root))

random.seed(42)

from src.utils.create_countries_combination import create_filtered_combination
from src.utils.create_scenario import generate_story_prompt

def read_general_config(config_file='general_config.json'):
    with open(config_file, 'r') as file:
        config = json.load(file)
    return config

def create_scenario_info(countries_df, info_path='data/processed/input_info.csv'):
    # Create combinations with different regions and religions
    countries_combs = create_filtered_combination(countries_df)

    # Test the frequency of the countries in the set
    combination_list = [countries_df.loc[i,'Country'] for comb in [list(countries_combs.iloc[ind]) for ind in range(len(countries_combs))] for i in comb]
    print(Counter(combination_list))

    # Country set information for each combination scenario (the order is randomized)
    columns = ['Country','Country','Country','Country','Religion','Religion','Religion','Religion','Country'] # columns to read from countries_combs 
    country_indices = [random.sample(list(countries_combs.iloc[ind]),4) + random.sample(list(countries_combs.iloc[ind]),1) for ind in range(len(countries_combs))] # shuffle and add location 
    data = [[countries_df.loc[i,column].strip() for i,column in zip(row[0:4]+row[0:4]+[row[4]],columns)] for row in country_indices]
    info_df = pd.DataFrame(data = data, 
                           columns = ['origin1','origin2','origin3','origin4','religion1','religion2','religion3','religion4','location'])

    # Save scenario info to CSV
    info_df.to_csv(info_path, sep=';', index=False)
    print(f"{len(info_df)} scenarios info saved to {info_path}")

    return info_df

def create_and_save_prompts(config, info_df, text_path='data/processed/input_texts.csv'):
    prompts = [generate_story_prompt(config["base_prompt"], info) for _,info in info_df.iterrows()]
    
    # Create a DataFrame with the prompts
    input_df = pd.DataFrame({'prompt': prompts})

    # Concat with scenario information 
    input_df = pd.concat([input_df, info_df], axis=1)

    # Save prompts to CSV
    input_df.to_csv(text_path, sep=';', index=False)
    print(f"Generated {len(info_df)} prompts and saved to {text_path}")

def main():
    # Load country data
    countries_df = pd.read_csv('data/raw/selected_countries_info.csv', sep=';', header=0)
    
    # Check if the info for scenarios exits
    info_path = 'data/processed/input_info.csv'
    if not os.path.exists(info_path): 
        info_df = create_scenario_info(countries_df, info_path)
    else:
        info_df = pd.read_csv(info_path, sep=';', header=0)

    config = read_general_config()

    create_and_save_prompts(config, info_df)

if __name__ == "__main__":
    main()