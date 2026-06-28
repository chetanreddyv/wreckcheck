import os
import re
import json
import time
import requests
import traceback
import dotenv
import streamlit as st

# ---- ENV BOOTSTRAP ----
# main.py does dotenv.load_dotenv() at module level. Streamlit may not pick up .env
# unless we load it ourselves BEFORE importing main.
dotenv.load_dotenv()
if "anthropic_api_key" in os.environ and "ANTHROPIC_API_KEY" not in os.environ:
    os.environ["ANTHROPIC_API_KEY"] = os.environ["anthropic_api_key"]

# Set page configuration
st.set_page_config(
    page_title="WreckCheck — Pre-Shipment Code Inspection",
    page_icon="•",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS following industry UI standards (Linear, Vercel style) without global container overrides
custom_css = """
<style>
/* Hide standard Streamlit header, footer, and menu */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Ultra-clean page background & modern typography */
.stApp {
    background-color: #fafbfc !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    color: #0f172a !important;
}

/* Subtle flat dividers */
hr {
    border: none !important;
    height: 1px !important;
    background-color: #f1f5f9 !important;
    margin: 2.5rem 0 !important;
}

/* Custom UI Cards replacing Streamlit border wrappers to eliminate nesting */
.ui-card {
    background-color: #ffffff;
    border: 1px solid rgba(241, 245, 249, 1);
    border-radius: 12px;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.02), 0 1px 2px -1px rgba(0, 0, 0, 0.02);
    padding: 1.25rem;
    transition: all 0.15s ease;
    margin-bottom: 1rem;
}
.ui-card:hover {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04), 0 2px 4px -2px rgba(0, 0, 0, 0.02);
}

/* Resource Pills inside Agent Cards */
.pill {
    background-color: #f1f5f9;
    color: #475569;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 500;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}
.pill-alert {
    background-color: #fef2f2;
    color: #dc2626;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

/* Console Box inside Agent Cards */
.console-box {
    background-color: #f8fafc;
    border: 1px solid #f1f5f9;
    border-radius: 8px;
    padding: 8px 10px;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    font-size: 0.78rem;
    color: #334155;
    line-height: 1.4;
}

/* Metric Containers - Vercel Flat Card Style */
[data-testid="stMetric"] {
    background-color: #ffffff !important;
    border: 1px solid rgba(241, 245, 249, 1) !important;
    padding: 1.25rem 1rem !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.02) !important;
}
[data-testid="stMetricLabel"] {
    color: #64748b !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em !important;
}
[data-testid="stMetricValue"] {
    color: #0f172a !important;
    font-size: 1.25rem !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
}

/* Clean Input Fields */
div[data-baseweb="input"] > div {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    padding: 4px 10px !important;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.02) !important;
}
div[data-baseweb="input"] > div:focus-within {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.08) !important;
}
/* Force input text color to black for visibility */
div[data-baseweb="input"] input {
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    caret-color: #0f172a !important;
    font-size: 0.92rem !important;
}
div[data-baseweb="input"] input::placeholder {
    color: #94a3b8 !important;
    -webkit-text-fill-color: #94a3b8 !important;
}

/* Industry Standard Flat Solid Buttons */
div.stButton > button {
    background: #0f172a !important;
    color: #ffffff !important;
    border: 1px solid transparent !important;
    border-radius: 8px !important;
    padding: 0.65rem 1.25rem !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
    transition: all 0.15s ease !important;
}
div.stButton > button:hover {
    background: #1e293b !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
}
div.stButton > button:disabled {
    background: #f1f5f9 !important;
    color: #94a3b8 !important;
    border-color: transparent !important;
    box-shadow: none !important;
}

/* Minimalist Tabs */
[data-baseweb="tab-list"] {
    background-color: #f8fafc !important;
    border-radius: 8px !important;
    padding: 4px !important;
    gap: 6px !important;
    border: none !important;
}
[data-baseweb="tab"] {
    border-radius: 6px !important;
    padding: 8px 16px !important;
    color: #64748b !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
}
[data-baseweb="tab"][aria-selected="true"] {
    background-color: #ffffff !important;
    color: #0f172a !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.04) !important;
}

/* Status Widget */
[data-testid="stStatusWidget"] {
    background-color: #ffffff !important;
    border: 1px solid #f1f5f9 !important;
    border-radius: 10px !important;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.02) !important;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Helper function to render industry UI standard headers
def render_stage_header(stage_num: int, title: str, subtitle: str = ""):
    sub_html = f'<div style="color: #64748b; font-size: 0.9rem; margin-top: 4px; font-weight: 400;">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div style="margin-top: 1.5rem; margin-bottom: 1.25rem;">
        <div style="color: #2563eb; font-size: 0.75rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 4px;">
            Stage 0{stage_num}
        </div>
        <h2 style="margin: 0; font-size: 1.35rem; color: #0f172a; font-weight: 600; letter-spacing: -0.02em;">{title}</h2>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)

# Helper function to parse and normalize GitHub URLs
def parse_github_url(url_str: str):
    if not url_str or not url_str.strip():
        return None
    url = url_str.strip()
    if url.endswith(".git"):
        url = url[:-4]
    
    ssh_match = re.match(r"^git@github\.com:([^/]+)/([^/]+)$", url)
    if ssh_match:
        return (ssh_match.group(1), ssh_match.group(2))
    
    http_match = re.match(r"^https?://(www\.)?github\.com/([^/]+)/([^/]+)/?.*$", url)
    if http_match:
        return (http_match.group(2), http_match.group(3))
    
    shorthand_match = re.match(r"^([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)$", url)
    if shorthand_match:
        return (shorthand_match.group(1), shorthand_match.group(2))
    
    return None

# Helper function to fetch GitHub REST API metadata
def fetch_repo_data(owner: str, repo: str):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    try:
        response = requests.get(url, headers=headers, timeout=4.0)
        if response.status_code == 200:
            data = response.json()
            pushed_at = data.get("pushed_at", "N/A")
            if pushed_at and len(pushed_at) >= 10:
                pushed_at = pushed_at[:10]
            return {
                "name": data.get("full_name", f"{owner}/{repo}"),
                "language": data.get("language") or "Config/Markdown",
                "stars": f"{data.get('stargazers_count', 0):,}",
                "size_kb": f"{data.get('size', 0):,} KB",
                "branch": data.get("default_branch", "main"),
                "last_push": pushed_at,
                "visibility": "Private" if data.get("private") else "Public",
                "raw": data
            }
    except Exception:
        pass
    
    return {
        "name": f"{owner}/{repo}",
        "language": "Unknown",
        "stars": "N/A",
        "size_kb": "N/A",
        "branch": "main",
        "last_push": "N/A",
        "visibility": "Unknown",
        "raw": {"error": "API call failed or rate-limited"}
    }

# Helper to safely load a workspace JSON file
def _load_workspace_json(filename: str):
    fpath = os.path.join("./workspace", filename)
    if not os.path.exists(fpath):
        return None
    try:
        with open(fpath, "r") as f:
            content = f.read().strip()
        # The agent may output raw text that isn't valid JSON;
        # deepagents.py writes str(res) which may not be valid JSON.
        # Try json.loads first, then fall back to displaying raw text.
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"_raw_text": content}
    except Exception:
        return None

# Helper function to render an agent performance dashboard card
def render_agent_card(placeholder, name: str, role: str, status: str, log_msg: str, timer: str = "0.0s", model: str = "claude-haiku-4-5", tokens: str = "0 tokens", findings: int = 0):
    status_styles = {
        "WAITING": '<span style="background-color: #f1f5f9; color: #64748b; padding: 2px 8px; border-radius: 6px; font-size: 0.72rem; font-weight: 600; letter-spacing: 0.02em;">WAITING</span>',
        "RUNNING": '<span style="background-color: #eff6ff; color: #2563eb; padding: 2px 8px; border-radius: 6px; font-size: 0.72rem; font-weight: 600; letter-spacing: 0.02em;">RUNNING</span>',
        "DONE": '<span style="background-color: #f0fdf4; color: #16a34a; padding: 2px 8px; border-radius: 6px; font-size: 0.72rem; font-weight: 600; letter-spacing: 0.02em;">DONE</span>',
        "ERROR": '<span style="background-color: #fef2f2; color: #dc2626; padding: 2px 8px; border-radius: 6px; font-size: 0.72rem; font-weight: 600; letter-spacing: 0.02em;">ERROR</span>'
    }
    badge = status_styles.get(status, status)
    findings_html = f'<span class="pill-alert">🚨 {findings} Findings</span>' if findings > 0 else '<span class="pill">🛡️ Clean</span>'
    
    placeholder.markdown(f"""
    <div class="ui-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <div>
                <h4 style="margin: 0; font-size: 1.05rem; color: #0f172a; font-weight: 600;">{name}</h4>
            </div>
            <div style="display: flex; gap: 8px; align-items: center;">
                <span style="font-size: 0.78rem; color: #64748b; font-family: ui-monospace, monospace; font-weight: 500;">⏱️ {timer}</span>
                {badge}
            </div>
        </div>
        <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 12px;">{role}</div>
        
        <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px;">
            <span class="pill">🤖 {model}</span>
            <span class="pill">⚡ {tokens}</span>
            {findings_html}
        </div>
        
        <div class="console-box">
            <div style="color: #64748b; font-size: 0.7rem; margin-bottom: 3px; text-transform: uppercase; letter-spacing: 0.05em;">Live Activity Feed</div>
            <div style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 500; color: #0f172a;">> {log_msg}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Initialize session state variables
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False
if "run_completed" not in st.session_state:
    st.session_state.run_completed = False

# --- HEADER SECTION ---
st.markdown("""
<div style="display: flex; align-items: center; gap: 14px; margin-top: 0.5rem; margin-bottom: 1.5rem;">
    <div style="background-color: #ffffff; padding: 10px; border-radius: 10px; display: flex; align-items: center; justify-content: center; border: 1px solid #f1f5f9; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            <polyline points="9 12 11 14 15 10"></polyline>
        </svg>
    </div>
    <div>
        <h1 style="margin: 0; font-size: 1.65rem; color: #0f172a; font-weight: 600; letter-spacing: -0.02em;">WreckCheck</h1>
        <div style="color: #64748b; font-size: 0.9rem;">Pre-shipment code inspection & autonomous architecture verification before your codebase wrecks</div>
    </div>
</div>
""", unsafe_allow_html=True)
st.divider()

# --- STAGE 1: INPUT PANEL ---
render_stage_header(1, "Target Repository", "Enter the target repository URL and product description to scan for enterprise readiness.")

col_input1, col_input2, col_btn = st.columns([2.5, 2.5, 1])

with col_input1:
    st.markdown('<div style="font-size: 0.82rem; font-weight: 500; color: #475569; margin-bottom: 4px;">Repository URL</div>', unsafe_allow_html=True)
    repo_input = st.text_input(
        "Repository URL", 
        key="repo_input_field", 
        placeholder="e.g., https://github.com/streamlit/streamlit or streamlit/streamlit",
        label_visibility="collapsed"
    )

with col_input2:
    st.markdown('<div style="font-size: 0.82rem; font-weight: 500; color: #475569; margin-bottom: 4px;">Product Description</div>', unsafe_allow_html=True)
    desc_input = st.text_input(
        "Product Description",
        key="desc_input_field",
        placeholder="e.g., Enterprise multi-agent AI coding assistant",
        label_visibility="collapsed"
    )

parsed_url = parse_github_url(repo_input)

# Live badge validation as user types
col_msg1, col_msg2 = st.columns([5, 1])
with col_msg1:
    if not repo_input:
        st.markdown('<div style="color: #64748b; font-size: 0.85rem; font-weight: 400; margin-top: 2px;">Enter a repository link above to validate format.</div>', unsafe_allow_html=True)
    elif parsed_url:
        st.markdown(f'<div style="color: #16a34a; font-size: 0.85rem; font-weight: 500; margin-top: 2px;">Valid Format: Normalized to target <code>{parsed_url[0]}/{parsed_url[1]}</code></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color: #dc2626; font-size: 0.85rem; font-weight: 500; margin-top: 2px;">Invalid Format: Please enter a valid HTTP URL, SSH path, or owner/repo shorthand.</div>', unsafe_allow_html=True)

with col_btn:
    analyze_clicked = st.button(
        "Run WreckCheck", 
        type="primary", 
        disabled=(parsed_url is None),
        use_container_width=True
    )

if analyze_clicked and parsed_url:
    st.session_state.analyzed = True
    st.session_state.owner, st.session_state.repo = parsed_url
    st.session_state.target_url = f"https://github.com/{parsed_url[0]}/{parsed_url[1]}"
    st.session_state.description = desc_input.strip() if desc_input and desc_input.strip() else "Enterprise automated software repository"
    st.session_state.run_completed = False
    st.session_state.repo_data = None
    st.session_state.final_report = None
    st.session_state.json_reports = {}
    st.session_state.run_error = None

# --- PROGRESSION PIPELINE (STAGES 2, 3, 4) ---
if st.session_state.analyzed:
    owner = st.session_state.owner
    repo = st.session_state.repo
    
    # --- STAGE 2: INSTANT REPO METRICS BAR ---
    st.divider()
    render_stage_header(2, "Inspection Telemetry", "Instant pre-scan repository metadata extraction.")
    
    if st.session_state.get("repo_data") is None:
        with st.spinner("Fetching pre-inspection repository telemetry (<1s)..."):
            st.session_state.repo_data = fetch_repo_data(owner, repo)
            
    repo_data = st.session_state.repo_data
    
    # Display horizontal stat strip
    m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
    with m1:
        st.metric("Repository", repo_data["name"].split("/")[-1])
    with m2:
        st.metric("Language", repo_data["language"])
    with m3:
        st.metric("Stars", repo_data["stars"])
    with m4:
        st.metric("Size", repo_data["size_kb"])
    with m5:
        st.metric("Default Branch", repo_data["branch"])
    with m6:
        st.metric("Last Push", repo_data["last_push"])
    with m7:
        st.metric("Visibility", repo_data["visibility"])

    # --- STAGE 3: LIVE ORCHESTRATION VIEW ---
    st.divider()
    render_stage_header(3, "Live Verification Pipeline", "Real-time execution telemetry from main.py DeepAgents pipeline.")
    
    agent_info = [
        ("Scout", "Orchestrator Commander & Task Graph Dispatch"),
        ("CodeSentinel", "Enterprise Readiness & Security Leak Auditor"),
        ("ArchitectReview", "Architectural Quality & AST Call Graph Auditor"),
        ("HarnessGuard", "Agent Safety, Cost & Loop Guardrail Sentinel"),
        ("ReadinessScorer", "Enterprise Readiness Synthesis & Final Scoring")
    ]
    
    card_cols_top = st.columns(2)
    card_cols_mid = st.columns(2)
    card_cols_bot = st.columns([1, 1])
    
    placeholders = [
        card_cols_top[0].empty(),
        card_cols_top[1].empty(),
        card_cols_mid[0].empty(),
        card_cols_mid[1].empty(),
        card_cols_bot[0].empty()
    ]
    
    if not st.session_state.run_completed:
        for i in range(5):
            render_agent_card(placeholders[i], *agent_info[i], "WAITING", "Standby for live execution...", "0.0s", "claude-haiku-4-5", "0 tokens", 0)
            
        with st.status("WreckCheck Inspection Active — Executing Live DeepAgents Pipeline...", expanded=True) as status_box:
            st.write("Initialization: Loading .env, hooking into main.py Scout Orchestrator...")
            
            # Show RUNNING state for all agents before the blocking call
            render_agent_card(placeholders[0], *agent_info[0], "RUNNING", "Invoking fetch_repo_files() and spawning sub-agent DAG...", "...", "claude-haiku-4-5", "Active", 0)
            render_agent_card(placeholders[1], *agent_info[1], "RUNNING", "Dispatched: Auditing enterprise readiness & secrets...", "...", "claude-haiku-4-5", "Active", 0)
            render_agent_card(placeholders[2], *agent_info[2], "RUNNING", "Dispatched: Evaluating architecture & structural layering...", "...", "claude-haiku-4-5", "Active", 0)
            render_agent_card(placeholders[3], *agent_info[3], "RUNNING", "Dispatched: Verifying loop controls & safety guardrails...", "...", "claude-haiku-4-5", "Active", 0)
            render_agent_card(placeholders[4], *agent_info[4], "WAITING", "Waiting for upstream sub-agents to complete...", "...", "claude-haiku-4-5", "Pending", 0)
            
            start_t = time.time()
            pipeline_error = None
            final_output = None
            
            try:
                # Pre-validate: check API key is available
                api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("anthropic_api_key")
                if not api_key:
                    raise EnvironmentError(
                        "ANTHROPIC_API_KEY not found in environment. "
                        "Please set it in your .env file as: ANTHROPIC_API_KEY=sk-ant-..."
                    )
                
                # Pre-validate: ensure required modules can be imported
                try:
                    import langchain_anthropic
                except ImportError as ie:
                    raise ImportError(
                        f"Missing dependency: {ie}. Run: pip install langchain-anthropic"
                    )
                
                # Import and run the actual backend pipeline from main.py
                from main import run as run_live_pipeline
                st.write("Pipeline modules loaded. Executing Scout orchestrator...")
                final_output = run_live_pipeline(
                    st.session_state.target_url,
                    st.session_state.description
                )
            except Exception as e:
                pipeline_error = f"{type(e).__name__}: {str(e)}\n\n```\n{traceback.format_exc()}\n```"
                
            elapsed_sec = round(time.time() - start_t, 1)
            st.session_state.elapsed_time = f"{elapsed_sec}s"
            
            # ---- Load workspace outputs regardless of success/failure ----
            # The sub-agents write to workspace/ even if Scout itself errors later
            reports = {}
            for key, fname in [("CodeSentinel", "code_sentinel.json"), ("ArchitectReview", "architect_review.json"), ("HarnessGuard", "harness_guard.json")]:
                loaded = _load_workspace_json(fname)
                if loaded is not None:
                    reports[key] = loaded
            st.session_state.json_reports = reports
            
            # Load the markdown report from workspace (main.py writes it)
            md_path = "./workspace/readiness_report.md"
            if os.path.exists(md_path):
                try:
                    with open(md_path, "r") as f:
                        st.session_state.final_report = f.read()
                except Exception:
                    st.session_state.final_report = final_output
            else:
                st.session_state.final_report = final_output
                
            if pipeline_error:
                st.session_state.run_error = pipeline_error
            
            # ---- Update cards to final state ----
            et = st.session_state.elapsed_time
            if pipeline_error:
                render_agent_card(placeholders[0], *agent_info[0], "ERROR", "Pipeline encountered an error. See output panel for details.", et, "claude-haiku-4-5", "See logs", 0)
            else:
                render_agent_card(placeholders[0], *agent_info[0], "DONE", "Orchestration completed. All sub-agent reports collected.", et, "claude-haiku-4-5", "Completed", 0)
            
            cs_status = "DONE" if "CodeSentinel" in reports else ("ERROR" if pipeline_error else "DONE")
            ar_status = "DONE" if "ArchitectReview" in reports else ("ERROR" if pipeline_error else "DONE")
            hg_status = "DONE" if "HarnessGuard" in reports else ("ERROR" if pipeline_error else "DONE")
            rs_status = "DONE" if st.session_state.final_report else ("ERROR" if pipeline_error else "DONE")
            
            render_agent_card(placeholders[1], *agent_info[1], cs_status, "workspace/code_sentinel.json" if "CodeSentinel" in reports else "No output generated.", et, "claude-haiku-4-5", "Completed", 0)
            render_agent_card(placeholders[2], *agent_info[2], ar_status, "workspace/architect_review.json" if "ArchitectReview" in reports else "No output generated.", et, "claude-haiku-4-5", "Completed", 0)
            render_agent_card(placeholders[3], *agent_info[3], hg_status, "workspace/harness_guard.json" if "HarnessGuard" in reports else "No output generated.", et, "claude-haiku-4-5", "Completed", 0)
            render_agent_card(placeholders[4], *agent_info[4], rs_status, "workspace/readiness_report.md" if st.session_state.final_report else "No report generated.", et, "claude-haiku-4-5", "Completed", 0)
            
            if pipeline_error:
                status_box.update(label=f"WreckCheck Completed with Errors ({et})", state="error", expanded=False)
            else:
                status_box.update(label=f"WreckCheck Complete ({et})", state="complete", expanded=False)
            
            time.sleep(0.3)
            st.session_state.run_completed = True
            st.rerun()
    else:
        # ---- STATIC POST-RUN VIEW ----
        reports = st.session_state.get("json_reports", {})
        elapsed = st.session_state.get("elapsed_time", "N/A")
        run_error = st.session_state.get("run_error")
        
        if run_error:
            st.markdown(f"""
            <div style="background-color: #ffffff; border: 1px solid #fecaca; color: #0f172a; padding: 14px 18px; border-radius: 10px; font-weight: 500; margin-bottom: 16px; display: flex; align-items: center; gap: 10px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>
                <span>WreckCheck encountered an error during execution ({elapsed}). Partial results may be available below.</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background-color: #ffffff; border: 1px solid #f1f5f9; color: #0f172a; padding: 14px 18px; border-radius: 10px; font-weight: 500; margin-bottom: 16px; display: flex; align-items: center; gap: 10px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path><polyline points="9 12 11 14 15 10"></polyline></svg>
                <span>WreckCheck Live Inspection Passed ({elapsed})</span>
            </div>
            """, unsafe_allow_html=True)
        
        cs_status = "DONE" if "CodeSentinel" in reports else "ERROR"
        ar_status = "DONE" if "ArchitectReview" in reports else "ERROR"
        hg_status = "DONE" if "HarnessGuard" in reports else "ERROR"
        rs_status = "DONE" if st.session_state.get("final_report") else "ERROR"
        overall_status = "ERROR" if run_error else "DONE"
        
        render_agent_card(placeholders[0], *agent_info[0], overall_status, "Orchestration completed." if not run_error else "Error during orchestration.", elapsed, "claude-haiku-4-5", "Completed", 0)
        render_agent_card(placeholders[1], *agent_info[1], cs_status, "workspace/code_sentinel.json" if "CodeSentinel" in reports else "No output.", elapsed, "claude-haiku-4-5", "Completed", 0)
        render_agent_card(placeholders[2], *agent_info[2], ar_status, "workspace/architect_review.json" if "ArchitectReview" in reports else "No output.", elapsed, "claude-haiku-4-5", "Completed", 0)
        render_agent_card(placeholders[3], *agent_info[3], hg_status, "workspace/harness_guard.json" if "HarnessGuard" in reports else "No output.", elapsed, "claude-haiku-4-5", "Completed", 0)
        render_agent_card(placeholders[4], *agent_info[4], rs_status, "workspace/readiness_report.md" if st.session_state.get("final_report") else "No report.", elapsed, "claude-haiku-4-5", "Completed", 0)

    # --- STAGE 4: OUTPUT PANEL ---
    st.divider()
    render_stage_header(4, "Inspection Verdict", "Generated markdown report and JSON audit outputs from live DeepAgents pipeline.")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Readiness Report (MD)", "Sub-Agent JSON Reports", "Pipeline Timeline", "Raw Telemetry"])
    
    with tab1:
        st.markdown(f"### Live Readiness Report for `{repo_data['name']}`")
        final_md = st.session_state.get("final_report")
        # Fallback: try reading from disk if session state lost it
        if not final_md and os.path.exists("./workspace/readiness_report.md"):
            try:
                with open("./workspace/readiness_report.md", "r") as f:
                    final_md = f.read()
            except Exception:
                pass
                
        if final_md:
            st.markdown(final_md)
        else:
            st.info("No markdown report was generated. Check the error output or re-run the pipeline.")
            
        # Show error details if present
        run_error = st.session_state.get("run_error")
        if run_error:
            with st.expander("Pipeline Error Details", expanded=False):
                st.markdown(run_error)
            
    with tab2:
        st.markdown("### Generated Sub-Agent JSON Audit Reports")
        reports = st.session_state.get("json_reports", {})
        
        if not reports:
            st.info("No sub-agent JSON reports found in ./workspace/. The pipeline may not have completed.")
        else:
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.markdown("#### CodeSentinel Output")
                if "CodeSentinel" in reports:
                    data = reports["CodeSentinel"]
                    if "_raw_text" in data:
                        st.code(data["_raw_text"], language="json")
                    else:
                        st.json(data)
                else:
                    st.write("No report found at workspace/code_sentinel.json")
                    
                st.markdown("#### HarnessGuard Output")
                if "HarnessGuard" in reports:
                    data = reports["HarnessGuard"]
                    if "_raw_text" in data:
                        st.code(data["_raw_text"], language="json")
                    else:
                        st.json(data)
                else:
                    st.write("No report found at workspace/harness_guard.json")
                    
            with col_r2:
                st.markdown("#### ArchitectReview Output")
                if "ArchitectReview" in reports:
                    data = reports["ArchitectReview"]
                    if "_raw_text" in data:
                        st.code(data["_raw_text"], language="json")
                    else:
                        st.json(data)
                else:
                    st.write("No report found at workspace/architect_review.json")

    with tab3:
        st.markdown("### Asynchronous Pipeline Timeline")
        elapsed = st.session_state.get("elapsed_time", "N/A")
        st.markdown(f"""
        <p style="color: #64748b; font-size: 0.88rem; margin-bottom: 16px;">Total pipeline wall-clock time: <strong>{elapsed}</strong>. CodeSentinel, ArchitectReview, and HarnessGuard execute concurrently via ThreadPoolExecutor.</p>
        <div class="ui-card">
            <div style="margin-bottom: 14px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.82rem; font-weight: 600; color: #334155; margin-bottom: 4px;">
                    <span>Scout (Orchestrator)</span>
                    <span style="font-family: monospace;">Phase 1: Fetch & Dispatch</span>
                </div>
                <div style="background-color: #f1f5f9; height: 16px; border-radius: 8px; width: 100%; position: relative;">
                    <div style="background-color: #3b82f6; height: 100%; width: 20%; border-radius: 8px;"></div>
                </div>
            </div>
            <div style="margin-bottom: 14px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.82rem; font-weight: 600; color: #334155; margin-bottom: 4px;">
                    <span>CodeSentinel (Async)</span>
                    <span style="font-family: monospace;">Parallel Phase</span>
                </div>
                <div style="background-color: #f1f5f9; height: 16px; border-radius: 8px; width: 100%; position: relative;">
                    <div style="background-color: #6366f1; height: 100%; width: 40%; margin-left: 20%; border-radius: 8px;"></div>
                </div>
            </div>
            <div style="margin-bottom: 14px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.82rem; font-weight: 600; color: #334155; margin-bottom: 4px;">
                    <span>ArchitectReview (Async)</span>
                    <span style="font-family: monospace;">Parallel Phase</span>
                </div>
                <div style="background-color: #f1f5f9; height: 16px; border-radius: 8px; width: 100%; position: relative;">
                    <div style="background-color: #8b5cf6; height: 100%; width: 45%; margin-left: 20%; border-radius: 8px;"></div>
                </div>
            </div>
            <div style="margin-bottom: 14px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.82rem; font-weight: 600; color: #334155; margin-bottom: 4px;">
                    <span>HarnessGuard (Async)</span>
                    <span style="font-family: monospace;">Parallel Phase</span>
                </div>
                <div style="background-color: #f1f5f9; height: 16px; border-radius: 8px; width: 100%; position: relative;">
                    <div style="background-color: #ec4899; height: 100%; width: 42%; margin-left: 20%; border-radius: 8px;"></div>
                </div>
            </div>
            <div>
                <div style="display: flex; justify-content: space-between; font-size: 0.82rem; font-weight: 600; color: #334155; margin-bottom: 4px;">
                    <span>ReadinessScorer (Synthesis)</span>
                    <span style="font-family: monospace;">Phase 3: Score & Report</span>
                </div>
                <div style="background-color: #f1f5f9; height: 16px; border-radius: 8px; width: 100%; position: relative;">
                    <div style="background-color: #10b981; height: 100%; width: 25%; margin-left: 65%; border-radius: 8px;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab4:
        st.markdown("### Raw Inspection Telemetry")
        reports = st.session_state.get("json_reports", {})
        st.json({
            "target_url": st.session_state.get("target_url"),
            "description": st.session_state.get("description"),
            "elapsed_time": st.session_state.get("elapsed_time"),
            "pipeline_status": "ERROR" if st.session_state.get("run_error") else "SUCCESS",
            "reports_generated": list(reports.keys()),
            "readiness_report_exists": os.path.exists("./workspace/readiness_report.md"),
            "workspace_files": os.listdir("./workspace") if os.path.exists("./workspace") else []
        })

    st.divider()
    
    # Run Again CTA
    col_reset1, col_reset2, col_reset3 = st.columns([1, 1, 1])
    with col_reset2:
        if st.button("Run Another WreckCheck", type="primary", use_container_width=True):
            for key in ["analyzed", "run_completed", "owner", "repo", "repo_data", "final_report", "json_reports", "elapsed_time", "run_error", "target_url", "description"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
