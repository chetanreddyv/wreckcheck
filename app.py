import os
import re
import json
import time
import threading
import traceback
import requests as http_requests
import dotenv
from flask import Flask, render_template, jsonify, request

dotenv.load_dotenv()
if "anthropic_api_key" in os.environ and "ANTHROPIC_API_KEY" not in os.environ:
    os.environ["ANTHROPIC_API_KEY"] = os.environ["anthropic_api_key"]

app = Flask(__name__)

# ---- In-memory pipeline state (single-user) ----
pipeline = {
    "status": "idle",       # idle | running | done | error
    "elapsed": None,
    "error": None,
    "report": None,
    "reports": {},
}
_lock = threading.Lock()


def parse_github_url(url_str):
    if not url_str or not url_str.strip():
        return None
    url = url_str.strip().rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]
    m = re.match(r"^git@github\.com:([^/]+)/([^/]+)$", url)
    if m:
        return m.group(1), m.group(2)
    m = re.match(r"^https?://(www\.)?github\.com/([^/]+)/([^/]+?)(?:/.*)?$", url)
    if m:
        return m.group(2), m.group(3)
    m = re.match(r"^([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)$", url)
    if m:
        return m.group(1), m.group(2)
    return None


def fetch_repo_data(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        r = http_requests.get(url, headers={"Accept": "application/vnd.github.v3+json"}, timeout=4)
        if r.status_code == 200:
            d = r.json()
            pushed = (d.get("pushed_at") or "N/A")[:10]
            return {
                "name": d.get("full_name", f"{owner}/{repo}"),
                "language": d.get("language") or "Config/Markdown",
                "stars": f'{d.get("stargazers_count", 0):,}',
                "size_kb": f'{d.get("size", 0):,} KB',
                "branch": d.get("default_branch", "main"),
                "last_push": pushed,
                "visibility": "Private" if d.get("private") else "Public",
            }
    except Exception:
        pass
    return {"name": f"{owner}/{repo}", "language": "Unknown", "stars": "N/A",
            "size_kb": "N/A", "branch": "main", "last_push": "N/A", "visibility": "Unknown"}


def _run_pipeline(repo_url, description):
    global pipeline
    start = time.time()
    try:
        api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("anthropic_api_key")
        if not api_key:
            raise EnvironmentError("ANTHROPIC_API_KEY not set in environment.")
        from main import run as run_live
        result = run_live(repo_url, description)
        elapsed = round(time.time() - start, 1)

        reports = {}
        for key, fname in [("CodeSentinel", "code_sentinel.json"),
                           ("ArchitectReview", "architect_review.json"),
                           ("HarnessGuard", "harness_guard.json")]:
            fpath = f"./workspace/{fname}"
            if os.path.exists(fpath):
                with open(fpath) as f:
                    reports[key] = f.read()
        md = None
        if os.path.exists("./workspace/readiness_report.md"):
            with open("./workspace/readiness_report.md") as f:
                md = f.read()
        with _lock:
            pipeline.update(status="done", elapsed=f"{elapsed}s", report=md or result, reports=reports, error=None)
    except Exception as e:
        elapsed = round(time.time() - start, 1)
        with _lock:
            pipeline.update(status="error", elapsed=f"{elapsed}s", error=traceback.format_exc(), report=None, reports={})


# ---- Routes ----
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/validate", methods=["POST"])
def validate():
    parsed = parse_github_url(request.json.get("url", ""))
    if parsed:
        return jsonify(valid=True, owner=parsed[0], repo=parsed[1])
    return jsonify(valid=False)


@app.route("/api/repo-info/<owner>/<repo>")
def repo_info(owner, repo):
    return jsonify(fetch_repo_data(owner, repo))


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.json
    url = f"https://github.com/{data['owner']}/{data['repo']}"
    desc = data.get("description") or "Enterprise automated software repository"
    with _lock:
        if pipeline["status"] == "running":
            return jsonify(error="Pipeline already running"), 409
        pipeline.update(status="running", elapsed=None, error=None, report=None, reports={})
    threading.Thread(target=_run_pipeline, args=(url, desc), daemon=True).start()
    return jsonify(status="started")


@app.route("/api/status")
def status():
    with _lock:
        return jsonify(dict(pipeline))


@app.route("/api/reset", methods=["POST"])
def reset():
    with _lock:
        pipeline.update(status="idle", elapsed=None, error=None, report=None, reports={})
    return jsonify(status="reset")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8501, debug=True, use_reloader=False)
