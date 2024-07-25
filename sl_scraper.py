import os
import re
from typing import List, Dict
import requests
from requests.exceptions import RequestException, Timeout, HTTPError
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import pprint


# urls to scrape data
SL_BASE_URL = "https://www.slgr.gr/en/" # SL = SuperLeague
TEAMS_URL = f"{SL_BASE_URL}teams/"
STATISTICS_URL = f"{SL_BASE_URL}statistics/"
SCHEDULE_URL = f"{SL_BASE_URL}schedule/"

# folder to save the data
DATA_FOLDER = "SuperLeauge_Data"
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
#=====================================  Main Script =================================
# extract the links for each season
years_urls = scrape_years_urls(TEAMS_URL)
pprint.pprint(years_urls)

for year in years_urls:
    team_urls = scrape_team_url(year['url'])
    pprint.pprint(team_urls)