import os
import requests

username = os.getenv('GIT_USER')
token = os.getenv('GIT_TOKEN')
api_url = f'https://api.github.com/users/{username}/repos'

if not username or not token:
    raise EnvironmentError("GIT_USER and GIT_TOKEN must be set in the environment variables.")

headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json'
}

# Step 1: Get all repositories
response = requests.get(api_url, headers=headers)
if response.status_code != 200:
    raise Exception(f"Failed to fetch repos: {response.status_code} {response.text}")

repos = response.json()

# Step 2: Filter and delete matching repos
for repo in repos:
    repo_name = repo['name']
    if "upload-folder" in repo_name:
        delete_url = f"https://api.github.com/repos/{username}/{repo_name}"
        del_response = requests.delete(delete_url, headers=headers)
        if del_response.status_code == 204:
            print(f"Deleted repository: {repo_name}")
        else:
            print(f"Failed to delete {repo_name}: {del_response.status_code} {del_response.text}")
