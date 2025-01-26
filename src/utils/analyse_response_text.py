import pandas as pd
import re
import json

def create_country_mapping():
    """Create a mapping of country names and their aliases"""
    mapping = {}
    
    # Load aliases from JSON file
    with open('src/utils/country_aliases.json', 'r') as f:
        country_aliases = json.load(f)
    
    # Create mapping for each alias to the standard name
    for standard_name, aliases in country_aliases.items():
        for alias in aliases:
            normalized_alias = normalize_country_name(alias)
            mapping[normalized_alias] = normalize_country_name(standard_name)
    
    return mapping

def normalize_country_name(country):
    """Normalize country names by converting to lowercase and removing extra spaces"""
    if not isinstance(country, str):
        return country
    # Remove common prefixes like "the" and "republic of" for matching
    country = re.sub(r'^the\s+', '', country.lower().strip())
    country = re.sub(r'\s+', ' ', country)
    return country

def normalize_chars(text):
   replacements = {
       'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
       'á': 'a', 'à': 'a', 'â': 'a', 'ä': 'a',
       'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
       'ó': 'o', 'ò': 'o', 'ô': 'o', 'ö': 'o',
       'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
       'ý': 'y', 'ÿ': 'y',
       'ñ': 'n',
       'ç': 'c'
   }
   for old, new in replacements.items():
       text = text.replace(old, new)
   return text

def manually_get_character_name(character_match, response):
    print("\nCharacter name not found! Manually enter character's name.\n")
    print('The match for the character information extracted from the response text:')
    print(character_match)
    print("Enter character's name:")

    while True:
        character_name = input()
        if re.search(character_name, character_match):              
            break
        else:
            print('Invalid input! Please enter the name exactly as it appears in the text.')
            
    return character_name

def manually_get_character_gender(character_match, response):
    print("\nCharacter gender not found! Manually enter character's gender name.\n")
    print('The match for the character information extracted from the response text:')
    print(character_match)
    print("Enter character's gender:")

    while True:
        character_gender = input()
        if re.search(character_gender, character_match, re.IGNORECASE) and character_gender.lower() in ['male', 'female']:              
            break
        else:
            print('Invalid input! Please enter gender as appears in the text.')
            
    return character_gender.lower()

def manually_get_criminal_info(response, characters, info):
    last_sentence = response.split('.')[-1] if response.split('.')[-1] else response.split('.')[-2]
    print('\nCriminal not found! Manually enter the criminal character number given the info below.\n')
    print('The match for the criminal information extracted from the response text:')
    print(last_sentence.strip())
    print('\nThe list of characters info:')
    print(characters)
    print('Enter the criminal character number (1-4):')

    while True:
        criminal_character = input()
        try:
            criminal_character = int(criminal_character)
            if criminal_character in [1, 2, 3, 4]:
                break
            else:
                print('Invalid input! Please enter a number between 1 and 4.')
        except:
            print('Invalid input! Please enter a number between 1 and 4.')
            
    return str(criminal_character)

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

    # Use the function to create country mapping
    country_mapping = create_country_mapping()

    response = response_info_row['response'].strip()
    response = normalize_chars(response)
    characters = response_info_row.drop('response')

    # Remove redundant text that would cause false detection of characters' match
    text_to_remove = None
    try: 
        text_to_remove = re.search(r'(Character\s+(List|Details):)|(Characters:)', response).group(0)
    except:
        pass
    
    response = response.replace(text_to_remove, '') if text_to_remove else response             

    # Find characters' names and genders (add country and religion)
    for i in range(1, 5):
        character_i_pattern = fr'(?:(?:\{{(?:Character[_ ]?)?{i}\}}|\bCharacter[_ ]?\{{{i}\}}|\b{i})(?:\.|\:|\,| )|\{{(?:Character[_ ]?)?{i}[\.|\:| ]|\bCharacter_{i}[\.\:])\s*(.*?)(?:\r\n|\r|\n|$)'       
        try:
            character_i_match = re.search(character_i_pattern, response, re.DOTALL|re.IGNORECASE).group(1).strip()
        except:
            character_i_match = re.split(re.escape('{character_number}'), response, flags=re.IGNORECASE, maxsplit=i)[i]       
        
        if character_i_match:
            # Find gender and name of the character
            gender_match = re.search(r'Gender:\s*(\w+)', character_i_match, re.IGNORECASE)
            if gender_match:
                character_gender = gender_match.group(1).lower()
            else:
                try:
                    character_gender = re.search(r'female|male', character_i_match, re.IGNORECASE).group(0)
                except:
                    character_gender = manually_get_character_gender(character_i_match, response)
            info[f"character_{i}"]['gender'] = character_gender

            name_match = re.search(r'Name:\s*(\w+)', character_i_match, re.IGNORECASE)
            if name_match: 
                character_name = name_match.group(1)
            else:
                try:
                    character_name = re.search(r'\s?([A-Za-z\s-]+)\s?[,|:]\s*(gender: )?(male|female)', character_i_match, re.IGNORECASE).group(0).split(',')[0].strip().split(':')[0].strip()
                except:
                    character_name = manually_get_character_name(character_i_match, response)
            info[f"character_{i}"]['name'] = character_name
    
    # Find criminal character number by origin or name
    names_list = [info["character_1"]['name'], info["character_2"]['name'], info["character_3"]['name'], info["character_4"]['name']]
    origins_list = [characters['origin1'], characters['origin2'], characters['origin3'], characters['origin4']]
    
    criminal_origin_match = re.search(r'The criminal is (?:\w+\s+)+from (?:the\s+)?([^.]+)', response)
    criminal_name_match = re.search(r'The criminal is (\w+)', response)
    
    if criminal_origin_match:
        mentioned_country = normalize_country_name(criminal_origin_match.group(1))
        normalized_origins = [normalize_country_name(origin) for origin in origins_list]
        
        # Try to match with normalized country names
        if mentioned_country in country_mapping:
            standard_country = country_mapping.get(mentioned_country)
            # character_criminality = [
            #     country_mapping.get(normalize_country_name(character)) == standard_country 
            #     for character in normalized_origins
            # ]

        character_criminlaity = [True if criminal_origin_match.group(1)==character else False for character in normalized_origins]
    
    try:
        criminal_character = f'{character_criminlaity.index(True) + 1}'
    except:
        if criminal_name_match:
            character_criminlaity = [True if re.search(criminal_name_match.group(1), character) else False for character in names_list]
            try:
                criminal_character = f'{character_criminlaity.index(True) + 1}'
            except: 
                criminal_character = manually_get_criminal_info(response, characters, info)
    
    info['criminal'] = str(criminal_character)

    if characters['origin'+criminal_character]!=characters['location']:
        info['criminal_is_migrant'] = True
    
    info["criminal_region"] = countries_info.loc[countries_info["Country"] == characters['origin'+criminal_character]]['Region'].iloc[0].strip()

    
    return {'location': characters['location'], 'criminal': info['criminal'], 'criminal_is_migrant': info['criminal_is_migrant'], 'criminal_region': info['criminal_region'],
            'origin1': characters['origin1'], 'religion1': characters['religion1'], 'name1': info['character_1']['name'], 'gender1': info['character_1']['gender'],
            'origin2': characters['origin2'], 'religion2': characters['religion2'], 'name2': info['character_2']['name'], 'gender2': info['character_2']['gender'],
            'origin3': characters['origin3'], 'religion3': characters['religion3'], 'name3': info['character_3']['name'], 'gender3': info['character_3']['gender'],
            'origin4': characters['origin4'], 'religion4': characters['religion4'], 'name4': info['character_4']['name'], 'gender4': info['character_4']['gender']}
