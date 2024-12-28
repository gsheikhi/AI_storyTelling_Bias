import pandas as pd
import re

def extract_criminal_info(response_info_row):
    info = {
        "character_1": {'name': None, 'gender': None},
        "character_2": {'name': None, 'gender': None},
        "character_3": {'name': None, 'gender': None},
        "character_4": {'name': None, 'gender': None},
        "criminal": None,
        "criminal_is_migrant": False,
        "criminal_region": None,
    }

    countries_info = pd.read_csv('data/raw/selected_countries_info.csv', sep=';')

    response = response_info_row['response']
    characters = response_info_row.drop('response')

    # Find characters' names and genders (add country and religion)
    for i in range(1, 5):
        character_i_pattern = fr'(?:(?:\{{(?:Character[_ ]?)?{i}\}}|\bCharacter[_ ]?\{{{i}\}}|\b{i})(?:\.|\:|\,| )|\{{(?:Character[_ ]?)?{i}[\.|\:| ]|\bCharacter_{i}[\.\:])\s*(.*?)(?:\r\n|\r|\n|$)'       
        try:
            character_i_match = re.search(character_i_pattern, response, re.DOTALL|re.IGNORECASE).group(1).strip()
        except:
            character_i_match = re.split(re.escape('{character_number}'), response, flags=re.IGNORECASE, maxsplit=i)[i]       
        
        if character_i_match:
            name_match = re.search(r'Name:\s*(\w+)', character_i_match, re.IGNORECASE)
            if name_match: 
                info[f"character_{i}"]['name'] = name_match.group(1)

            gender_match = re.search(r'Gender:\s*(\w+)', character_i_match, re.IGNORECASE)
            if gender_match:
                info[f"character_{i}"]['gender'] = gender_match.group(1)
   
    # Find criminal character number by origin or name
    names_list = [info["character_1"]['name'], info["character_2"]['name'], info["character_3"]['name'], info["character_1"]['name']]
    origins_list = [characters['origin1'], characters['origin2'], characters['origin3'], characters['origin4']]
    criminal_origin_match = re.search(r'The criminal is (?:\w+\s+)+from ([^.]+)', response)
    if criminal_origin_match:
        character_criminlaity = [True if re.search(criminal_origin_match.group(1), character) else False for character in origins_list]
        try:
            criminal_character = f'{character_criminlaity.index(True) + 1}'
        except:
            criminal_name_match = re.search(r'The criminal is (\w+)', response)
            if criminal_name_match:
                character_criminlaity = [True if re.search(criminal_name_match.group(1), character) else False for character in names_list]
                try:
                    criminal_character = f'{character_criminlaity.index(True) + 1}'
                except: 
                    criminal_character = ''
        info['criminal'] = str(criminal_character)

        if characters['origin'+criminal_character]!=characters['location']:
            info['criminal_is_migrant'] = True

        info["criminal_region"] = countries_info.loc[countries_info["Country"] == characters['origin'+criminal_character]]['Region'].iloc[0].strip()
    
    else: 
        criminal_character = None
        info['criminal_is_migrant'] = None
        info["criminal_region"] = None
    
    return {'location': characters['location'], 'criminal': info['criminal'], 'criminal_is_migrant': info['criminal_is_migrant'], 'criminal_region': info['criminal_region'],
            'origin1': characters['origin1'], 'religion1': characters['religion1'], 'name1': info['character_1']['name'], 'gender1': info['character_1']['gender'],
            'origin2': characters['origin2'], 'religion2': characters['religion2'], 'name2': info['character_2']['name'], 'gender2': info['character_2']['gender'],
            'origin3': characters['origin3'], 'religion3': characters['religion3'], 'name3': info['character_3']['name'], 'gender3': info['character_3']['gender'],
            'origin4': characters['origin4'], 'religion4': characters['religion4'], 'name4': info['character_4']['name'], 'gender4': info['character_4']['gender']}
