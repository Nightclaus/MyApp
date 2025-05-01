import subprocess
import json
import asyncio
import tempfile
import shutil
import random
import string
from flask import Flask, request, jsonify, render_template

from dotenv import load_dotenv
import os

load_dotenv()

# Ensure unique
# Length of the random string you want
length = 10

# Generate a random string of specified length
random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length)).lower()

"""
Housekeeping

gh auth login  # Ensure ur authenticated

npm install -g vercel
vercel login  # Ensure ur uthenticated
"""

app = Flask(__name__)
#os.makedirs(UPLOAD_FOLDER, exist_ok=True)

GITHUB_USER = os.getenv('GIT_USER')
GIT_TOKEN = os.getenv('GIT_TOKEN')

VERCEL_PROJECT = os.getenv('VERCEL_PROJECT')
VERCEL_API_TOKEN = os.getenv('VERCEL_API_TOKEN')

DEFAULT_DIRECTORY = os.getcwd()

@app.route('/')
def home(): 
    return render_template('index.html') # Not a real page yet

@app.route('/discover')
def discover_page(): 
    return render_template('discover.html') # Not a real page yet

@app.route('/library')
def global_library(): 
    return render_template('page_not_found.html') # Not a real page yet

@app.route('/deploy')
def deploy_page():
    return render_template('deployment.html')

@app.route('/projects')
def projects_page():
    # If you had project data in Python, you'd load it here
    # test_project_data = [...] # Load from database or file
    # return render_template('projects.html', projects=test_project_data)

    # For now, just render the template (assuming JS populates it)
    return render_template('projects.html')

@app.route('/settings')
def setting_page():
    # If you had project data in Python, you'd load it here
    # test_project_data = [...] # Load from database or file
    # return render_template('projects.html', projects=test_project_data)

    # For now, just render the template (assuming JS populates it)
    return render_template('page_not_found.html')

@app.route('/not-found')
def page_not_found():
    # If you had project data in Python, you'd load it here
    # test_project_data = [...] # Load from database or file
    # return render_template('projects.html', projects=test_project_data)

    # For now, just render the template (assuming JS populates it)
    return render_template('page_not_found.html')

def find_main_py(directory):
    """
    Recursively search for main.py in the given directory.
    Returns the path to the directory containing main.py or None if not found.
    """
    for root, dirs, files in os.walk(directory):
        if 'main.py' in files:
            return root  # Return the directory containing main.py
    return None

@app.route('/upload_folder', methods=['POST'])
def upload_folder():
    application_folder_name = "upload-folder-"+random_string
    with tempfile.TemporaryDirectory() as UPLOAD_FOLDER:
        if 'files[]' not in request.files:
            return jsonify({"message": "No files uploaded"}), 400

        uploaded_files = request.files.getlist('files[]')

        if not uploaded_files:
            return jsonify({"message": "No files found in the folder."}), 400

        # Create a folder to save the uploaded files
        folder_path = os.path.join(UPLOAD_FOLDER, application_folder_name)
        os.makedirs(folder_path, exist_ok=True)  # Create the base folder

        # Save each file to the folder
        for file in uploaded_files:
            # Ensure the file's path (including subdirectories) exists
            file_subdir = os.path.join(folder_path, os.path.dirname(file.filename))
            os.makedirs(file_subdir, exist_ok=True)

            # Define the final file path and save the file
            file_path = os.path.join(file_subdir, os.path.basename(file.filename))
            print(f"Saving file: {file_path}")
            file.save(file_path)

        # return jsonify({"message": f"Successfully uploaded {len(uploaded_files)} files."})

        # Step 1: Run Pygbag on the uploaded folder
        root = find_main_py(folder_path)

        async def start_pygame():
            subprocess.run(["pygbag", root], check=True)
        
        start_pygame()

        print("Done Pygbag")

        print(root)

        build_dir = os.path.join(root, "build", "web")
        print(build_dir)
        if not os.path.exists(build_dir):
            print("Found build")
            return jsonify({"message": "Build failed!"}), 500
        
        
        print("Done Next")

        # Step 2 SKIP
        # Step 1: Create the repo only if it doesn't exist
        result = subprocess.run(
            ["gh", "repo", "view", application_folder_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if result.returncode != 0:  # Repo does not exist, so create it
            subprocess.run(
                ["gh", "repo", "create", application_folder_name, "--public", "--confirm"],
                check=True
            )

        # Step 2: Prepare the local repository
        os.chdir(build_dir)

        # If .git exists, remove it to reinitialize cleanly (OPTIONAL)
        if os.path.exists(os.path.join(build_dir, ".git")):
            subprocess.run(["rm", "-rf", ".git"], check=True)  # Danger: Deletes commit history

        subprocess.run(["git", "init"], check=True)

        # Step 3: Configure Git Remote (only if not already set)
        remote_check = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True
        )

        if remote_check.returncode != 0:  # Remote does not exist, so add it
            subprocess.run(
                f'git remote add origin https://{GITHUB_USER}:{GIT_TOKEN}@github.com/{GITHUB_USER}/{application_folder_name}.git',
                shell=True
            )

        # Step 4: Add, Commit, and Push
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Automated commit"], check=True)
        subprocess.run(["git", "push", "--set-upstream", "origin", "main", "--force"], check=True)

        # Step 4: Deploy to Vercel

        # Step 4 deploy

        deploy_process = subprocess.run(["vercel", "--prod", "--confirm"], check=True, capture_output=True, text=True)
        vercel_url = deploy_process.stdout.strip()  # Get the deployment URL from the output

        # Resets
        os.chdir(DEFAULT_DIRECTORY)

        return jsonify({"message": f"Success! Your game is now live at {vercel_url}"})

if __name__ == '__main__':
    app.run(debug=True)