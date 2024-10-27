import pandas as pd
from collections import Counter
# from scipy.stats import pearsonr # colls correlation and p-value

def compute_responses_statistics(criminal_info_dict, country_info_path = 'data/raw/selected_countries_info.csv'):
    country_info_df = pd.read_csv(country_info_path, sep=';')
    list_countries = country_info_df['Country']
    list_regions = country_info_df['Region'].unique()
    list_religions = country_info_df['Religion'].unique()

    rounds = criminal_info_dict.keys()

    immigrant_stats_df = pd.DataFrame(columns=[f'{round}_{name}' for round in rounds for name in ['total','criminal','percentage']],index=['immigrant'])
    gender_stats_df = pd.DataFrame(columns=[f'{round}_{name}' for round in rounds for name in ['total','criminal','percentage']],index=['Female','Male'])
    country_stats_df = pd.DataFrame(columns=[f'{round}_{name}' for round in rounds for name in ['total','criminal','percentage']],index=list_countries)
    region_stats_df = pd.DataFrame(columns=[f'{round}_{name}' for round in rounds for name in ['total','criminal','percentage']],index=list_regions)
    religion_stats_df = pd.DataFrame(columns=[f'{round}_{name}' for round in rounds for name in ['total','criminal','percentage']],index=list_religions)

    for round in rounds:
        df = criminal_info_dict[round]
        n_records = len(df) # number of scenarios

        immigrant_count = 3 * n_records # 3 out of 4 characters are immigrants, 4 characters in each scenario
        gender_count = Counter(list(df.loc[:,['gender1','gender2', 'gender3','gender4']].stack()))
        country_count = Counter(list(df.loc[:,['origin1','origin2', 'origin3','origin4']].stack()))
        region_count = {region:0 for region in list_regions}
        for country in country_count.keys():
            region = country_info_df.loc[(country_info_df['Country'] == country),'Region']
            region_count[region.iloc[0]] = country_count[country]
        religion_count = {religion:0 for religion in list_religions}
        for country in country_count.keys():
            religion = country_info_df.loc[(country_info_df['Country'] == country),'Religion']
            religion_count[religion.iloc[0]] = country_count[country]

        criminal_immigrant_count = sum(df.criminal_is_migrant)
        criminal_gender_count = Counter([df.loc[i, f'gender{ch}'] for i,ch in zip(range(n_records),df['criminal'])])
        criminal_country_count = Counter([df.loc[i, f'origin{ch}'] for i,ch in zip(range(n_records),df['criminal'])])
        criminal_region_count = {region:0 for region in list_regions}
        for country in criminal_country_count.keys():
            region = country_info_df.loc[(country_info_df['Country'] == country),'Region']
            criminal_region_count[region.iloc[0]] = criminal_country_count[country]
        criminal_religion_count = {religion:0 for religion in list_religions}
        for country in criminal_country_count.keys():
            religion = country_info_df.loc[(country_info_df['Country'] == country),'Religion']
            criminal_religion_count[religion.iloc[0]] = criminal_country_count[country]

        immigrant_stats_df.loc['immigrant',f'{round}_total'] = immigrant_count
        immigrant_stats_df.loc['immigrant',f'{round}_criminal'] = criminal_immigrant_count
        immigrant_stats_df.loc['immigrant',f'{round}_percentage'] = 100 * criminal_immigrant_count/immigrant_count
        gender_stats_df[f'{round}_total'] = gender_count
        gender_stats_df[f'{round}_criminal'] = criminal_gender_count
        gender_stats_df[f'{round}_percentage'] = 100 * gender_stats_df[f'{round}_criminal']/gender_stats_df[f'{round}_total']
        country_stats_df[f'{round}_total'] = country_count
        country_stats_df[f'{round}_criminal'] = criminal_country_count
        country_stats_df[f'{round}_percentage'] = 100 * country_stats_df[f'{round}_criminal']/country_stats_df[f'{round}_total']
        country_stats_df.fillna(0, inplace=True)
        region_stats_df[f'{round}_total'] = region_count
        region_stats_df[f'{round}_criminal'] = criminal_region_count
        region_stats_df[f'{round}_percentage'] = 100 * region_stats_df[f'{round}_criminal']/region_stats_df[f'{round}_total']
        religion_stats_df[f'{round}_total'] = religion_count
        religion_stats_df[f'{round}_criminal'] = criminal_religion_count
        religion_stats_df[f'{round}_percentage'] = 100 * religion_stats_df[f'{round}_criminal']/religion_stats_df[f'{round}_total']

    return {'immigrant_stats': immigrant_stats_df,
            'gender_stats': gender_stats_df,
            'country_stats': country_stats_df,
            'region_stats': region_stats_df,
            'religion_stats': religion_stats_df}