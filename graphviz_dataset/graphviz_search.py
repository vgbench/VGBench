import requests
import json
import typing
from keys import GITHUB_TOKEN
import time

# Constants
GITHUB_API_URL = "https://api.github.com"

def get_headers():
    """Returns the headers required for GitHub API requests."""
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    return headers

def get_file_list() -> typing.List[dict]:
    """Fetches the user information from GitHub."""
    results = []
    for i in range(30,33):
        url = f"{GITHUB_API_URL}/search/code?q=language:\"Graphviz (DOT)\"&type=Code&page=%d"%i
        headers = get_headers()
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            results += response.json()['items']
        else:
            response.raise_for_status()
        time.sleep(2)
        print(i)
    return results




def main():
    file_list = get_file_list()
    json.dump(file_list, open("graphviz_file_list_4.json", "w"))
    # print(len(file_list), file_list[0]['path'])
    '''for file in file_list:
        obtain_file_content(file['url'])'''

if __name__ == "__main__":
    main()