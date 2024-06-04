import json
import requests
import tqdm
from keys import GITHUB_TOKEN
import time

graphviz_data = json.load(open("graphviz_dataset/graphviz_file_list.json"))

print(len(graphviz_data))

def get_headers():
    """Returns the headers required for GitHub API requests."""
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    return headers

def obtain_github_file_content(url):
    print(url)
    response = requests.get(url)
    if response.status_code == 403:
        return None, None
    file_metadata = response.json()
    caption = file_metadata['name']
    graphviz =  requests.get(file_metadata['download_url'], headers=get_headers()).content.decode()
    return caption, graphviz

# for sample in svg_data:
#     svg = obtain_github_file_content(sample['url'])

results = []

n=len(graphviz_data)

for idx in tqdm.tqdm(range(638, n)):
    graphviz_sample = graphviz_data[idx]
    caption, graphviz = obtain_github_file_content(graphviz_sample['url'])
    if caption == None:
        json.dump(results, open("graphviz_dataset/graphviz_data_%d.json"%idx, "w"))
        break
    if graphviz.isascii():
        results.append({"caption":caption, "code": graphviz})

json.dump(results, open("graphviz_dataset/graphviz_data_final.json", "w"))

