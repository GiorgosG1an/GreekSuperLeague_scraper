"""
Greek SL Scraper made by GiorgosG1an
email: georgegiannopoulos2@gmail.com
version: 1.0
date: 25/07/2024
"""
import os
import re
from typing import List, Dict
import requests
from requests.exceptions import RequestException, Timeout, HTTPError
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from bs4 import Tag
import pprint
import pandas as pd


# urls to scrape data
SL_BASE_URL = "https://www.slgr.gr/en/" # SL = SuperLeague
TEAMS_URL = f"{SL_BASE_URL}teams/"
STATISTICS_URL = f"{SL_BASE_URL}statistics/"
SCHEDULE_URL = f"{SL_BASE_URL}schedule/"

# folder to save the data
DATA_FOLDER = "SuperLeague_Data"
os.makedirs(DATA_FOLDER, exist_ok=True)



def scrape_years_urls(url: str) -> List[Dict[str,str]]:
    """
    Scrapes the years and corresponding URLs from a given URL.

    Example Output:
    ```txt
    [{'year': '2024-2025', 'url': 'https://www.slgr.gr/en/teams/23/'},
    {'year': '2023-2024', 'url': 'https://www.slgr.gr/en/teams/22/'},
    {'year': '2022-2023', 'url': 'https://www.slgr.gr/en/teams/21/'},
    ...
    ```

    Args:
        url (str): The URL to scrape.

    Returns:
        List[Dict[str,str]]: A list of dictionaries containing the year and URL information.

    Raises:
        Timeout: If a timeout occurs while making the request.
        HTTPError: If an HTTP error occurs while making the request.
        RequestException: If a general request exception occurs while making the request.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Timeout as e:
        print(f"Timeout: {e}")
    except HTTPError as e:
        print(f"HTTP error: {e}")
    except RequestException as e:
        print(f"Request exception: {e}")
    
    soup = BeautifulSoup(response.content, 'html.parser')        
    # Find the <ul> tag with the class 'sub-current'
    sub_current_ul = soup.select('ul.sub-current')
    # print(sub_current_ul[-2])

    # select the appropriate one
    sub_current = sub_current_ul[-2]
    years_urls = []
    
    for a_tag in sub_current.find_all('a'):
        rel_url = a_tag['href']
        year = a_tag.find('li').get_text(strip=True)
        abs_url = urljoin(SL_BASE_URL, rel_url)
        years_urls.append({'year' : year, 
                            'url' : abs_url})
    
    # pprint.pprint(years_links)
    return years_urls

def scrape_team_url(url:str) -> List[Dict[str,str]]:
    """
    Scrapes the team URLs from the given URL.

    Example Output:
    ```txt
    [{'name': 'A.E.K.', 'url': 'https://www.slgr.gr/en/team/1047/'},
    {'name': 'ΑΡΗΣ', 'url': 'https://www.slgr.gr/en/team/1048/'},
    {'name': 'ASTERAS AKTOR', 'url': 'https://www.slgr.gr/en/team/1049/'},
    ...
    ```

    Args:
        url (str): The URL to scrape the team URLs from.

    Returns:
        List[Dict[str,str]]: A list of dictionaries containing the team name and URL.

    Raises:
        Timeout: If a timeout occurs while making the request.
        HTTPError: If an HTTP error occurs while making the request.
        RequestException: If a general request exception occurs while making the request.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Timeout as e:
        print(f"Timeout: {e}")
    except HTTPError as e:
        print(f"HTTP error: {e}")
    except RequestException as e:
        print(f"Request exception: {e}")

    soup = BeautifulSoup(response.content, 'html.parser')
    
    team_cards = soup.select('a.team-card')

    teams_info = []
    for card in team_cards:
        team_rel_url = card['href']
        team_url = urljoin(SL_BASE_URL, team_rel_url)
        team_name = card.select_one('h4').get_text(strip=True)

        teams_info.append({'name' : team_name,
                           'url' : team_url})
    
    return teams_info

def scrape_team_data(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Timeout as e:
        print(f"Timeout: {e}")
    except HTTPError as e:
        print(f"HTTP error: {e}")
    except RequestException as e:
        print(f"Request exception: {e}")

    soup = BeautifulSoup(response.content, 'html.parser')

    team_name = soup.select('div.container.fix-font-size.vertical-center')
    
    if team_name:
        team_name = team_name[0].get_text(strip=True)
        # print(team_name)
    else:
        team_name = None
    # change the url from team info to team stats
    url = url.replace('info','teamStats')
    # print(url)
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Timeout as e:
        print(f"Timeout: {e}")
    except HTTPError as e:
        print(f"HTTP error: {e}")
    except RequestException as e:
        print(f"Request exception: {e}")

    soup = BeautifulSoup(response.content, 'html.parser')
    team_position = soup.select('div.team-stats-wrapper')

    stats_dict = {}

    for position in team_position:
        position_div = position.find('div', class_='position')
        position_val = position.find('div', class_='bold position-value')
        if position_div and position_val:
            stat_name = position_div.get_text(strip=True)
            stat_value = position_val.get_text(strip=True)
            stats_dict[stat_name] = stat_value
        else:
            print("Expected divs not found in one of the stat rows.")
            continue

        points_div = position.find('div', class_='points')
        points_val = position.find('div', class_='bold points-value')
        if points_div and points_val:
            stat_name = points_div.get_text(strip=True)
            stat_value = points_val.get_text(strip=True)
            stats_dict[stat_name] = stat_value
        else:
            print("Expected divs not found in one of the stat rows.")
            continue
        
        games_div = position.find('div', class_='games')
        games_val = position.find('div', class_='bold games-value')

        if games_div and games_val:
            stat_name = games_div.get_text(strip=True)
            stat_value = games_val.get_text(strip=True)
            stats_dict[stat_name] = stat_value
        else:
            print("Expected divs not found in one of the stat rows.")
            continue
    stats_dict['team'] = team_name
    team_stats = soup.select('div.total-stats-content div.row-team-info')
    
    for stat in team_stats:
        bold_div = stat.find('div', class_='bold')
        text_right_div = stat.find('div', class_='text-right')

        if bold_div and text_right_div:
            stat_name = bold_div.get_text(strip=True)
            stat_value = text_right_div.get_text(strip=True)
            stats_dict[stat_name] = stat_value
        else:
            print("Expected divs not found in one of the stat rows.")
            continue
    
    return stats_dict

#=====================================  Main Script =================================
# extract the links for each season
years_urls = scrape_years_urls(TEAMS_URL)
pprint.pprint(years_urls)

i = 1
for year in years_urls:
    if i != 1 :
        team_urls = scrape_team_url(year['url'])
        # create folders for each year
        subdirectory = os.path.join(DATA_FOLDER, year['year'])
        os.makedirs(subdirectory, exist_ok=True)
        all_teams_data = []
        for team in team_urls:
            team_data = scrape_team_data(team['url'])
            team_data['season'] = year['year']
            all_teams_data.append(team_data)
         # Create a DataFrame for the year
        
        df = pd.DataFrame(all_teams_data)
        df.drop_duplicates()
        # Save the DataFrame to a CSV file
        print(df)
        csv_file = os.path.join(subdirectory, f"team_stats_{year['year']}.csv")
        df.to_csv(csv_file, index=False)
        print(f"Saved data for {year['year']} to {csv_file}")
        
    i += 1

# List to hold DataFrames
dataframes = []

# Iterate through each year folder in the data folder
for year_folder in os.listdir(DATA_FOLDER):
    year_path = os.path.join(DATA_FOLDER, year_folder)
    
    if os.path.isdir(year_path):
        # Iterate through each CSV file in the year folder
        for csv_file in os.listdir(year_path):
            if csv_file.endswith('.csv'):
                csv_path = os.path.join(year_path, csv_file)
                
                # Read the CSV file into a DataFrame
                df = pd.read_csv(csv_path)
                
                # Append the DataFrame to the list
                dataframes.append(df)

# Concatenate all DataFrames into a single DataFrame
combined_df = pd.concat(dataframes, ignore_index=True)

# Define the path for the combined CSV file
combined_csv_path = os.path.join(DATA_FOLDER, 'combined_team_stats.csv')

# Save the combined DataFrame to a CSV file
combined_df.to_csv(combined_csv_path, index=False)

print(f"Combined CSV saved to {combined_csv_path}")