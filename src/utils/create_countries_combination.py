import pandas as pd
from itertools import combinations
from tqdm import tqdm

def create_filtered_combination(df, num_countries=4):
    n_rows = len(df)
    
    print(f'\nGenerating combinations of {num_countries} countries...')
    combs = list(combinations(range(n_rows), num_countries))
    print(f'{len(combs)} combinations created.')
    
    print('Filtering rows with the same Region or Religion ...')
    filtered_combs = []
    
    for comb in tqdm(combs):
        comb = list(comb)
        regions = df.loc[comb, 'Region'].values
        religions = df.loc[comb, 'Religion'].values
        if len(set(regions)) == 4 and len(set(religions)) == 4:
            filtered_combs.append(comb)
    
    filtered_combs_df = pd.DataFrame(filtered_combs, columns=['Row1', 'Row2', 'Row3', 'Row4'])
    filtered_combs_df = filtered_combs_df.reset_index(drop=True)
    
    print(f'Combinations after filtering = {len(filtered_combs_df)}.')
    
    return filtered_combs_df
