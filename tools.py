import requests
import os
import json

def fetch_repo_files(repo_url: str) -> str:
    """
    Fetches key files from a public GitHub repo via raw API.
    Returns concatenated file contents as a single string.
    """
    # Convert https://github.com/user/repo → raw API calls
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
        except:
            contents.append(f"=== {f} ===\nNOT FOUND")
    result = "\n\n".join(contents)
    os.makedirs("./workspace", exist_ok=True)
    with open("./workspace/repo_contents.txt", "w") as out:
        out.write(result)
    return result

def read_file(path: str) -> str:
    """Read a file from the shared workspace."""
    with open(path, "r") as f:
        return f.read()

def write_file(path: str, content: str) -> str:
    """Write content to the shared workspace."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    return f"Written to {path}"
