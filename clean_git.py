import requests
from dotenv import load_dotenv
import os

load_dotenv()
# Replace with your GitHub username and personal access token
username = os.getenv('GIT_USER')
token = os.getenv('GIT_TOKEN')  # Expired, make new one here: https://github.com/settings/tokens

# GitHub API URL to get user repositories
api_url = f'https://api.github.com/users/{username}/repos'

# Fetch all repositories
response = requests.get(api_url, auth=(username, token))

if response.status_code == 200:
    repos = response.json()

    # Filter repositories with 'upload-folder-' in the name
    repos_to_delete = [repo['name'] for repo in repos if 'uploaded_folder' in repo['name']]

    if not repos_to_delete:
        print("No repositories with 'upload-folder-' found.")
    else:
        # Delete each repository
        for repo in repos_to_delete:
            repo_url = f'https://api.github.com/repos/{username}/{repo}'
            delete_response = requests.delete(repo_url, auth=(username, token))

            if delete_response.status_code == 204:
                print(f"Repository '{repo}' deleted successfully.")
            else:
                print(f"Failed to delete repository '{repo}': {delete_response.status_code} - {delete_response.text}")
else:
    print(f"Error fetching repositories: {response.status_code} - {response.text}")
