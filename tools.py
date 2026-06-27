import requests
import os
import json
from langchain_core.tools import tool

@tool
def fetch_repo_files(repo_url: str) -> str:
    """
    Fetches key files from a public GitHub repo via raw API.
    Returns concatenated file contents as a single string.
    """
    # Convert https://github.com/user/repo → raw API calls
    if repo_url.endswith(".git"):
        repo_url = repo_url[:-4]
    base = repo_url.replace("https://github.com/", "https://api.github.com/repos/")
    headers = {"Accept": "application/vnd.github.v3+json"}
    target_files = ["README.md", "SKILL.md", "main.py", "app.py",
                    "requirements.txt", "package.json", ".env.example"]
    contents = []
    for f in target_files:
        try:
            r = requests.get(f"{base}/contents/{f}", headers=headers, timeout=5)
            if r.status_code == 200:
                import base64
                data = r.json()
                decoded = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
                contents.append(f"=== {f} ===\n{decoded}")
            else:
                contents.append(f"=== {f} ===\nNOT FOUND (HTTP {r.status_code})")
        except Exception as e:
            contents.append(f"=== {f} ===\nERROR: {str(e)}")
    result = "\n\n".join(contents)
    os.makedirs("./workspace", exist_ok=True)
    with open("./workspace/repo_contents.txt", "w") as out:
        out.write(result)
    return result

@tool
def read_file(path: str) -> str:
    """Read a file from the shared workspace."""
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@tool
def write_file(path: str, content: str) -> str:
    """Write content to the shared workspace."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return f"Written to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@tool
def search_files(query: str, directory: str = ".") -> str:
    """Search for a string in files within a directory."""
    results = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.py', '.md', '.txt', '.json', '.js', '.ts')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', errors='ignore') as f:
                        if query in f.read():
                            results.append(filepath)
                except Exception:
                    pass
    return "\n".join(results) if results else "No matches found."
