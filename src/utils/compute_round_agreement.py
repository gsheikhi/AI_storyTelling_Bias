import pandas as pd
from sklearn.metrics import cohen_kappa_score
from itertools import combinations

def calculate_multi_rater_kappa(dict):
    """
    Calculate Cohen's kappa for all pairs of generation rounds across multiple columns.
    
    Parameters:
    dict: Dictionary of DataFrames containing criminal charater info from different rounds
    
    Returns:
    dict: Dictionary containing kappa scores for each column and rater pair
    """
    # Function to get dynamic column values based on criminal number
    def get_dynamic_columns(df_criminal_info):
        religion = [df_criminal_info.loc[ind, f"religion{i}"] for ind, i in df_criminal_info["criminal"].items()]
        origin = [df_criminal_info.loc[ind, f"origin{i}"] for ind, i in df_criminal_info["criminal"].items()]
        gender= [df_criminal_info.loc[ind, f"gender{i}"] for ind, i in df_criminal_info["criminal"].items()]

        return pd.DataFrame({"criminal": df_criminal_info["criminal"],
                             "criminal_is_migrant": df_criminal_info["criminal_is_migrant"],
                             "region": df_criminal_info["criminal_region"],
                             "religion": religion,
                             "gender": gender,
                             "origin": origin
                             })

    # Store DataFrames in a list for easier iteration
    df_list = [dict.get(key) for key in dict.keys()]
    
    # Static columns that don't depend on criminal number
    static_columns = ["criminal", "criminal_is_migrant"]
    # Dynamic columns that depend on criminal number
    dynamic_columns = ["religion", "region", "gender", "origin"]
    # All columns to be assessed for inter round agreement
    all_columns = static_columns + dynamic_columns

    dfs = [get_dynamic_columns(df) for df in df_list]

    round_pairs = list(combinations(range(len(dfs)), 2))
    results = {}
    # Calculate kappa for each column and rater pair
    for col in all_columns:
        results[col] = {}
        for i, j in round_pairs:
            try:
                kappa = cohen_kappa_score(dfs[i][col], dfs[j][col])
                results[col][f"Rater_{i+1}_vs_Rater_{j+1}"] = kappa
            except Exception as e:
                results[col][f"Rater_{i+1}_vs_Rater_{j+1}"] = f"Error: {str(e)}"
 
    # Format the kappa results into a readable DataFrame

    formatted_results = []
    for column, scores in results.items():
        for rater_pair, kappa in scores.items():
            formatted_results.append({
                'Column': column,
                'Rater Pair': rater_pair,
                'Kappa Score': kappa if isinstance(kappa, float) else kappa
            })
    
    return pd.DataFrame(formatted_results)

# Example usage:
if __name__ == "__main__":
    df1 = pd.DataFrame({
        'criminal': [1, 2, 3, 4],
        'criminal_is_migrant': [True, False, True, False],
        'religion1': ['A', 'B', 'C', 'D'],
        'region1': ['X', 'Y', 'Z', 'W'],
        'gender1': ['M', 'F', 'M', 'F'],
        'origin1': ['P', 'Q', 'R', 'S'],
        'religion1': ['A', 'B', 'C', 'D'],
        'region1': ['X', 'Y', 'Z', 'W'],
        'gender1': ['M', 'F', 'M', 'F'],
        'origin1': ['P', 'Q', 'R', 'S'],
        'religion1': ['A', 'B', 'C', 'D'],
        'region1': ['X', 'Y', 'Z', 'W'],
        'gender1': ['M', 'F', 'M', 'F'],
        'origin1': ['P', 'Q', 'R', 'S'],
        'religion1': ['A', 'B', 'C', 'D'],
        'region1': ['X', 'Y', 'Z', 'W'],
        'gender1': ['M', 'F', 'M', 'F'],
        'origin1': ['P', 'Q', 'R', 'S']
    })
    df2 = pd.DataFrame({
        'criminal': [1, 4, 3, 4],
        'criminal_is_migrant': [True, False, False, False],
        'religion1': ['A', 'B', 'C', 'D'],
        'region1': ['X', 'Y', 'Z', 'W'],
        'gender1': ['M', 'F', 'M', 'F'],
        'origin1': ['P', 'Q', 'R', 'S'],
        'religion1': ['A', 'B', 'C', 'D'],
        'region1': ['X', 'Y', 'Z', 'W'],
        'gender1': ['M', 'F', 'M', 'F'],
        'origin1': ['P', 'Q', 'R', 'S'],
        'religion1': ['A', 'B', 'C', 'D'],
        'region1': ['X', 'Y', 'Z', 'W'],
        'gender1': ['M', 'F', 'M', 'F'],
        'origin1': ['P', 'Q', 'R', 'S'],
        'religion1': ['A', 'B', 'C', 'D'],
        'region1': ['X', 'Y', 'Z', 'W'],
        'gender1': ['M', 'F', 'M', 'F'],
        'origin1': ['P', 'Q', 'R', 'S']
    })
    df3 = pd.DataFrame({
        'criminal': [1, 3, 3, 2],
        'criminal_is_migrant': [True, False, True, False],
        'religion1': ['A', 'B', 'C', 'D'],
        'region1': ['X', 'Y', 'Z', 'W'],
        'gender1': ['M', 'F', 'M', 'F'],
        'origin1': ['P', 'Q', 'R', 'S'],
        'religion1': ['A', 'B', 'C', 'D'],
        'region1': ['X', 'Y', 'Z', 'W'],
        'gender1': ['M', 'F', 'M', 'F'],
        'origin1': ['P', 'Q', 'R', 'S'],
        'religion1': ['A', 'B', 'C', 'D'],
        'region1': ['X', 'Y', 'Z', 'W'],
        'gender1': ['M', 'F', 'M', 'F'],
        'origin1': ['P', 'Q', 'R', 'S'],
        'religion1': ['A', 'B', 'C', 'D'],
        'region1': ['X', 'Y', 'Z', 'W'],
        'gender1': ['M', 'F', 'M', 'F'],
        'origin1': ['P', 'Q', 'R', 'S']
    })

    # Calculate kappa scores
    results = calculate_multi_rater_kappa({'round1':df1, 'round1':df2, 'round1':df3})
    print(results)
