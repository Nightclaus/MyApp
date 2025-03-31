import os
import subprocess
import json
import asyncio
from flask import Flask, request, jsonify, render_template

"""
gh auth login  # Ensure you're authenticated

npm install -g vercel
vercel login  # Ensure you're authenticated


"""

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

GITHUB_USER = "nightclaus"
VERCEL_PROJECT = "nightclaus"

VERCEL_API_TOKEN = "R5EESvCWH2UHcROX0lK1H1aC"

@app.route('/')
def home():
    return render_template('index.html')

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
    if 'files[]' not in request.files:
        return jsonify({"message": "No files uploaded"}), 400

    uploaded_files = request.files.getlist('files[]')

    if not uploaded_files:
        return jsonify({"message": "No files found in the folder."}), 400

    # Create a folder to save the uploaded files
    folder_name = "uploaded_folder"
    folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
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

    # Step 2

    # Check if the current directory is a Git repository
    if not os.path.exists(".git"):
        # Initialize the Git repository
        subprocess.run(["git", "init"], check=True)
        
        # Add the remote origin (replace with the appropriate GitHub repository URL)
        remote_url = f"https://github.com/{GITHUB_USER}/{folder_name}.git"
        subprocess.run(["git", "remote", "add", "origin", remote_url], check=True)

    # Ensure we add and commit files before pushing (if not already committed)
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)

    # Now create the GitHub repository and push the changes
    subprocess.run(["gh", "repo", "create", f"{GITHUB_USER}/{folder_name}", "--private", "--source", build_dir, "--remote", "origin"], check=True)

    # Step 3: Push to GitHub
    os.chdir(build_dir)
    subprocess.run(["git", "init"], check=True)
    subprocess.run(["git", "remote", "add", "origin", f"https://github.com/{GITHUB_USER}/{folder_name}.git"], check=True)
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
    subprocess.run(["git", "branch", "-M", "main"], check=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], check=True)


    """
    # Step 4: Deploy to Vercel
    deploy_process = subprocess.run(["vercel", "--prod", "--confirm"], check=True, capture_output=True, text=True)
    vercel_url = deploy_process.stdout.strip()  # Get the deployment URL from the output

    # Step 5: Get the current domain from Vercel project
    vercel_project_url = f"https://api.vercel.com/v6/projects/{VERCEL_PROJECT}/domains"
    response = subprocess.run(
        ["curl", "-H", f"Authorization: Bearer {VERCEL_API_TOKEN}", vercel_project_url],
        capture_output=True,
        text=True
    )

    if response.returncode != 0:
        return jsonify({"message": "Failed to fetch Vercel project domains"}), 500

    domains = json.loads(response.stdout)
    if domains.get("domains"):
        current_domain = domains["domains"][0]["name"]
    else:
        return jsonify({"message": "No domain found for this project!"}), 404

    return jsonify({"message": f"Success! Your game is now live at {current_domain}"})
    """

if __name__ == '__main__':
    app.run(debug=True)