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

def save_dataframes_to_excel(dataframes_dict, filepath):
    try:
        if os.path.exists(filepath):
            mode = 'a'  # append mode if file exists
            with pd.ExcelWriter(filepath, engine='openpyxl', mode=mode) as writer:
                # First remove existing sheets
                book = writer.book
                for sheet in book.sheetnames:
                    del book[sheet]
                # Then write new sheets
                for sheet_name, df in dataframes_dict.items():
                    df.to_excel(writer, sheet_name=sheet_name)
        else:
            mode = 'w'  # write mode if file doesn't exist
            with pd.ExcelWriter(filepath, engine='openpyxl', mode=mode) as writer:
                for sheet_name, df in dataframes_dict.items():
                    df.to_excel(writer, sheet_name=sheet_name)
        
        print(f"Successfully saved to {filepath}")
        
    except Exception as e:
        print(f"Error saving Excel file: {str(e)}")

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
            criminal_info[col] = round_responses.apply(extract_criminal_info, axis=1, result_type='expand')
            criminal_info_file = f'data/results/charactersANDcriminal_info/extracted_info_{model_name}_{col}.csv'
            (criminal_info[col]).to_csv(criminal_info_file, index=False)
        else:
            print(f'ERROR: The column names of responses file ({responses_path}) does not match the predefined format.')
    
    # Calculate statistics
    statistics_dict = compute_responses_statistics(criminal_info)

    # Save model statistics in Excel Sheets
    file_path = f'data/results/statistics_{model_name}.xlsx'
    save_dataframes_to_excel(statistics_dict,filepath=file_path)

def main():
    info_df = pd.read_csv('data/processed/input_info.csv', sep=';', header=0) # input character info

    with open('general_config.json', 'r') as f:
        config = json.load(f)
    models = config["testing_models"]
    
    for model in models:
        response_file = f'data/processed/{model}_responses.csv'
        print('Reading response file ' + response_file + '...')
        if Path(response_file).is_file():
            analyze_model_responses(model, info_df)
        else:
            print('ERROR: Response file for {model} does not exist.')

if __name__ == "__main__":
    main()