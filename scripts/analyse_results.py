import pandas as pd
import os
import sys
from pathlib import Path
import json

# Add the root directory to the Python path
project_root = Path(__file__).resolve().parents[1]  # Adjust the number based on how deep the script is
sys.path.insert(0, str(project_root))

from src.utils.analyse_response_text import extract_criminal_info
from src.utils.compute_statistics import compute_responses_statistics

def analyze_model_responses(model_name, info_df):

    responses_path = f'data/processed/{model_name}_responses.csv'

    if os.path.exists(responses_path):
        responses_df = pd.read_csv(responses_path, sep=';', header=0) 
    else:
        print(f'\nERROR: Model reponses file "{responses_path}" does not exist\n')
        os._exit(0)
    
    criminal_info = {}
    for round, col in enumerate(list(responses_df.columns)):
        if col == f'round{round+1}':
            # Extract criminal information from responses and input information
            round_responses = pd.concat([responses_df[col], info_df.iloc[0:len(responses_df)]], axis=1)
            round_responses.rename(columns={col: 'response'}, inplace=True)
            criminal_info[col]= round_responses.apply(extract_criminal_info, axis=1, result_type='expand')
        else:
            print(f'ERROR: The column names of responses file ({responses_path}) does not match the predefined format.')
    
    # Calculate statistics
    statistics = compute_responses_statistics(criminal_info)
    
    # Create a DataFrame with the statistics
    stats_df = pd.DataFrame(statistics)
    
    # Save to CSV
    stats_df.to_csv(f'data/results/{model_name}_results.csv', index=False)
    print(f"Generated statistics for {model_name} and saved to data/results/{model_name}_results.csv")

def main():
    info_df = pd.read_csv('data/processed/input_info.csv', sep=';', header=0) # input character info

    with open('general_config.json', 'r') as f:
        config = json.load(f)
    models = config["testing_models"]
    
    for model in models:
        analyze_model_responses(model, info_df)

if __name__ == "__main__":
    main()