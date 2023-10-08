import os
from urllib.parse import urlparse
import re
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")
workshop_id = os.getenv("WORKSHOP_FILE_ID")

# Mapping of hostnames to categories
CATEGORY_MAPPING = {
    "patreon.com": "donate",
    "ko-fi.com": "donate",
    "paypal.com": "donate",
    "buymeacoffee.com": "donate",
    "github.com": "github",
    "discord.gg": "discord",
    "crowdin.com": "translation",
    "i.imgur.com": "images",
    "imgur.com": "images",
}

def getplayerdetails(userid):
    # See the docs for this api endpoint: https://partner.steamgames.com/doc/webapi/ISteamUser#GetPlayerSummaries
    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
    # Define the request payload
    payload = {
        "key": api_key,
        "steamids": userid
    }

    # Make the GET request
    response = requests.get(url, params=payload)
    # Check if the request was successful (HTTP status code 200)
    if response.status_code == 200:
        data = response.json()
        if "response" in data and "players" in data["response"]:
            player_data = data["response"]["players"][0]
            return player_data
        else:
            raise ValueError("Player not found.")
    else:
        raise ConnectionError(f"Failed to retrieve Player details. HTTP status code: {response.status_code}")


def getworkshopdetails(workshop_item_id):
    # See the docs for this api endpoint: https://partner.steamgames.com/doc/webapi/ISteamRemoteStorage#GetPublishedFileDetails
    url = f"https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
    # Define the request payload
    payload = {
        "key": api_key,
        "itemcount": 1,
        "publishedfileids[0]": workshop_item_id
    }

    # Make the POST request
    response = requests.post(url, data=payload)
    # Check if the request was successful (HTTP status code 200)
    if response.status_code == 200:
        data = response.json()
        if "response" in data and "publishedfiledetails" in data["response"]:
            workshop_item = data["response"]["publishedfiledetails"][0]
            return workshop_item
        else:
            raise ValueError("Workshop item not found.")
    else:
        raise ConnectionError(f"Failed to retrieve Player details. HTTP status code: {response.status_code}")


def extract_urls(string):
    # Regular expression pattern to match URLs in the string while stopping before ']'
    url_pattern = r'https?://[^\]\[]+'

    # Find all URLs in the string using regular expression
    urls = re.findall(url_pattern, string)

    # Initialize a dictionary to store URLs by hostname
    url_dict = {}

    for url in urls:
        # Parse the URL to get the hostname
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname

        # If the hostname is not already in the dictionary, create a list
        if hostname not in url_dict:
            url_dict[hostname] = []

        # Add the URL to the list of that hostname
        url_dict[hostname].append(url)

    return url_dict


def categorise_urls(dictoflists):
    # Initialize a dictionary to store URLs by category
    categorized_urls = {category: [] for category in set(CATEGORY_MAPPING.values())}

    for category, urls in dictoflists.items():
        for url in urls:
            # Parse the URL to get the hostname (in lowercase)
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname.lower()
            hostname = hostname.replace("www.", "")
            # Check if the lowercase hostname is in the lowercase mapping
            if hostname in CATEGORY_MAPPING:
                category = CATEGORY_MAPPING[hostname]
                categorized_urls[category].append(url)

    return categorized_urls


if __name__ == "__main__":
    workshop_data = getworkshopdetails(workshop_id)
    author_data = getplayerdetails(workshop_data["creator"])
    print(workshop_data["title"], "by", author_data["personaname"])
    workshop_urls = extract_urls(workshop_data["description"])
    categorised_urls = categorise_urls(workshop_urls)
    #print(categorised_urls)
    #print(workshop_data)
    #print(author_data)
