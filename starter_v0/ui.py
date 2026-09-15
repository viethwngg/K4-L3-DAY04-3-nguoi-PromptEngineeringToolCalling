from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
PROVIDER_LABELS = {
    "gemini": "Gemini",
    "openrouter": "OpenRouter",
    "openai": "OpenAI",
    "anthropic": "Anthropic",
}


st.set_page_config(
    page_title="Northstar IT Desk",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
<style>
    :root {
        --lime: #55ef5d;
        --lime-soft: rgba(85, 239, 93, 0.14);
        --lime-line: rgba(85, 239, 93, 0.28);
        --ink: #050706;
        --panel: #111412;
        --panel-2: #1a1e1b;
        --muted: #8b948d;
        --text: #f3f7f4;
    }

    .stApp {
        color: var(--text);
        background:
            radial-gradient(circle at 78% 24%, rgba(0, 93, 27, 0.24), transparent 34%),
            radial-gradient(circle at 46% 92%, rgba(17, 111, 36, 0.17), transparent 30%),
            linear-gradient(135deg, #020403 0%, #050806 54%, #061108 100%);
    }

    [data-testid="stHeader"], #MainMenu, footer {
        display: none;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #191c1a 0%, #111311 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding: 1.25rem 1rem 1rem;
    }

    .block-container {
        max-width: 1040px;
        padding-top: 1.5rem;
        padding-bottom: 7rem;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: .7rem;
        margin: .2rem 0 1.2rem;
        font-weight: 760;
        letter-spacing: -.02em;
    }

    .brand-mark, .assistant-avatar {
        display: inline-grid;
        place-items: center;
        width: 32px;
        height: 32px;
        border-radius: 10px;
        color: #061008;
        background: var(--lime);
        box-shadow: 0 0 24px rgba(85, 239, 93, .18);
        font-weight: 900;
    }

    .sidebar-label {
        color: var(--muted);
        font-size: .72rem;
        font-weight: 700;
        letter-spacing: .09em;
        text-transform: uppercase;
        margin: 1.1rem 0 .45rem;
    }

    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        padding-bottom: 1.1rem;
        border-bottom: 1px solid rgba(255,255,255,.06);
        margin-bottom: 1.4rem;
    }

    .title-wrap h1 {
        font-size: 1.12rem;
        line-height: 1.2;
        margin: 0 0 .35rem;
        letter-spacing: -.02em;
    }

    .title-wrap p {
        color: var(--muted);
        font-size: .82rem;
        margin: 0;
    }

    .badges {
        display: flex;
        justify-content: flex-end;
        flex-wrap: wrap;
        gap: .45rem;
    }

    .badge {
        display: inline-flex;
        align-items: center;
        gap: .4rem;
        padding: .42rem .7rem;
        border: 1px solid var(--lime-line);
        border-radius: 999px;
        color: #a8f7ae;
        background: var(--lime-soft);
        font-size: .72rem;
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        white-space: nowrap;
    }

    .hero {
        margin: 11vh auto 2rem;
        max-width: 650px;
        text-align: center;
    }

    .hero-mark {
        display: inline-grid;
        place-items: center;
        width: 52px;
        height: 52px;
        border-radius: 16px;
        color: #071009;
        background: var(--lime);
        box-shadow: 0 0 45px rgba(85, 239, 93, .18);
        font-size: 1.45rem;
        font-weight: 900;
        margin-bottom: 1rem;
    }

    .hero h2 {
        font-size: clamp(1.7rem, 4vw, 2.55rem);
        margin: 0 0 .65rem;
        letter-spacing: -.045em;
    }

    .hero p {
        color: var(--muted);
        margin: 0 auto;
        max-width: 540px;
        line-height: 1.65;
    }

    [data-testid="stChatMessage"] {
        padding: 1rem 0;
        background: transparent;
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
        line-height: 1.65;
    }

    [data-testid="stChatInput"] {
        border: 1px solid rgba(255,255,255,.12);
        background: rgba(249, 252, 249, .98);
        border-radius: 15px;
        box-shadow: 0 22px 70px rgba(0,0,0,.48);
    }

    [data-testid="stChatInput"] textarea {
        color: #111 !important;
    }

    [data-testid="stChatInput"] button {
        color: #071009;
        background: var(--lime);
        border-radius: 10px;
    }

    [data-testid="stExpander"] {
        background: rgba(13, 34, 17, .72);
        border: 1px solid var(--lime-line);
        border-radius: 13px;
        margin: .45rem 0;
        overflow: hidden;
    }

    .trace-meta {
        display: flex;
        gap: .45rem;
        flex-wrap: wrap;
        margin-bottom: .55rem;
    }

    .trace-chip {
        padding: .25rem .5rem;
        border-radius: 7px;
        color: #b9f8be;
        background: rgba(85,239,93,.1);
        border: 1px solid rgba(85,239,93,.2);
        font-size: .7rem;
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    }

    .empty-note {
        margin-top: 1.25rem;
        color: #7f8981;
        font-size: .74rem;
    }

    .stButton > button, .stDownloadButton > button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,.1);
        background: #242824;
        color: #eef4ef;
        transition: .15s ease;
    }

    .stButton > button:hover, .stDownloadButton > button:hover {
        color: var(--lime);
        border-color: var(--lime-line);
        background: rgba(85,239,93,.08);
    }

    div[data-testid="stSidebar"] div[data-testid="stButton"]:last-of-type button {
        border-color: var(--lime-line);
    }

    @media (max-width: 760px) {
        .block-container { padding: 1rem .8rem 6rem; }
        .topbar { align-items: flex-start; flex-direction: column; }
        .badges { justify-content: flex-start; }
        .hero { margin-top: 7vh; }
    }
    /* Dark composer */
.stApp [data-testid="stChatInput"],
.stApp [data-testid="stChatInput"] [data-baseweb="textarea"] {
    background: #171c19 !important;
    border: 1px solid #35443a !important;
    border-radius: 16px !important;
}

.stApp [data-testid="stChatInput"] textarea,
.stApp [data-testid="stChatInput"] textarea:focus {
    background: #171c19 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    opacity: 1 !important;
}

.stApp [data-testid="stChatInput"] textarea::placeholder {
    color: #a6b2aa !important;
    -webkit-text-fill-color: #a6b2aa !important;
    opacity: 1 !important;
}

.stApp [data-testid="stChatInput"]:focus-within {
    border-color: #55ef5d !important;
}

.stApp [data-testid="stChatInput"] button {
    background: #55ef5d !important;
    color: #071009 !important;
}
</style>
""",
    unsafe_allow_html=True,
)


def new_session() -> dict[str, Any]:
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    return {
        "id": stamp,
        "title": "New helpdesk chat",
        "created_at": now_iso(),
        "messages": [],
        "history": [],
        "turns": [],
        "transcript_path": None,
    }


def ensure_state() -> None:
    if "sessions" not in st.session_state:
        session = new_session()
        st.session_state.sessions = {session["id"]: session}
        st.session_state.active_session = session["id"]


def active_session() -> dict[str, Any]:
    return st.session_state.sessions[st.session_state.active_session]


def start_new_chat() -> None:
    session = new_session()
    st.session_state.sessions[session["id"]] = session
    st.session_state.active_session = session["id"]


def transcript_payload(
    session: dict[str, Any],
    *,
    provider_name: str,
    selected_model: str | None,
    artifact: Any,
    system_prompt_path: Path,
    tools_path: Path,
    history_window: int,
    max_tool_rounds: int,
) -> dict[str, Any]:
    return {
        "transcript_id": f"ui_{session['id']}",
        **artifact_version_dict(artifact),
        "provider": provider_name,
        "model": selected_model,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": session["created_at"],
        "updated_at": now_iso(),
        "source": "streamlit_ui",
        "turns": session["turns"],
    }


def render_tool_trace(event: dict[str, Any], index: int) -> None:
    result = event.get("result") or {}
    has_error = isinstance(result, dict) and bool(result.get("error"))
    state_icon = "🔴" if has_error else "🟢"
    tool_name = str(event.get("tool") or "unknown_tool")
    with st.expander(f"{state_icon} Tool trace · {tool_name}", expanded=has_error):
        st.markdown(
            f'<div class="trace-meta"><span class="trace-chip">event {index}</span>'
            f'<span class="trace-chip">{html.escape("error" if has_error else "success")}</span></div>',
            unsafe_allow_html=True,
        )
        left, right = st.columns(2)
        with left:
            st.caption("INPUT ARGUMENTS")
            st.json(event.get("args") or {})
        with right:
            st.caption("TOOL RESULT")
            st.json(result)
        if has_error:
            st.error(f"{result.get('error')}: {result.get('message', 'Tool execution failed')}")


ensure_state()

with st.sidebar:
    st.markdown(
        '<div class="brand"><span class="brand-mark">✦</span><span>Northstar Desk</span></div>',
        unsafe_allow_html=True,
    )
    if st.button("＋  New chat", use_container_width=True, type="primary"):
        start_new_chat()
        st.rerun()

    search = st.text_input("Search chats", placeholder="Search", label_visibility="collapsed")
    st.markdown('<div class="sidebar-label">Recent chats</div>', unsafe_allow_html=True)

    matching_sessions = [
        item
        for item in reversed(list(st.session_state.sessions.values()))
        if search.casefold() in item["title"].casefold()
    ]
    for item in matching_sessions:
        label = f"▱  {item['title'][:27]}"
        if st.button(label, key=f"session_{item['id']}", use_container_width=True):
            st.session_state.active_session = item["id"]
            st.rerun()

    st.markdown('<div class="sidebar-label">Runtime</div>', unsafe_allow_html=True)
    provider_name = st.selectbox(
        "Provider",
        options=list(PROVIDER_LABELS),
        index=0,
        format_func=lambda value: PROVIDER_LABELS[value],
    )
    version = st.text_input("Artifact version", value="v1")
    model_override = st.text_input("Model override", value="", placeholder="Use provider default")

    with st.expander("Advanced settings"):
        history_window = st.slider("History window", 1, 10, 5)
        max_tool_rounds = st.slider("Max tool rounds", 1, 8, 4)

    current_session = active_session()
    if current_session.get("transcript_path"):
        transcript_path = Path(current_session["transcript_path"])
        if transcript_path.exists():
            st.download_button(
                "↓  Download transcript",
                data=transcript_path.read_bytes(),
                file_name=transcript_path.name,
                mime="application/json",
                use_container_width=True,
            )


system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
tools_path = ARTIFACTS_DIR / "tools.yaml"
system_prompt = system_prompt_path.read_text(encoding="utf-8")
tool_declarations = load_tool_declarations(tools_path)
openai_tools = to_openai_tools(tool_declarations)
artifact = build_artifact_version(version, system_prompt_path, tools_path)

try:
    provider = make_provider(provider_name)
    selected_model = model_override.strip() or getattr(provider, "default_model", None)
    runtime_error = None
except Exception as exc:
    provider = None
    selected_model = model_override.strip() or None
    runtime_error = f"{type(exc).__name__}: {exc}"

session = active_session()
safe_title = html.escape(session["title"])
safe_provider = html.escape(PROVIDER_LABELS[provider_name])
safe_artifact = html.escape(artifact.artifact_version)

st.markdown(
    f"""
<div class="topbar">
    <div class="title-wrap">
        <h1>{safe_title}</h1>
        <p>Internal IT support · evidence-first answers</p>
    </div>
    <div class="badges">
        <span class="badge">● {safe_provider}</span>
        <span class="badge">{safe_artifact}</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

if runtime_error:
    st.error(f"Provider initialization failed: {runtime_error}")

if not session["messages"]:
    st.markdown(
        """
<div class="hero">
    <div class="hero-mark">✦</div>
    <h2>How can IT help today?</h2>
    <p>Check service health, inspect a company device, find approved guidance,
    or prepare a support ticket with a complete tool trace.</p>
    <div class="empty-note">Try: “Kiểm tra trạng thái VPN production.”</div>
</div>
""",
        unsafe_allow_html=True,
    )

for message in session["messages"]:
    avatar = "👤" if message["role"] == "user" else "🤖"

    with st.chat_message(message["role"], avatar=avatar):
        raw = message["content"]

        if message["role"] == "assistant":
            try:
                payload = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                payload = None

            if isinstance(payload, dict) and isinstance(payload.get("reply"), str):
                st.markdown(payload["reply"])

                evidence = payload.get("evidence_ids")
                if isinstance(evidence, list) and evidence:
                    st.caption("Nguồn: " + ", ".join(map(str, evidence)))

                with st.expander("Response metadata"):
                    st.json(payload)
            else:
                st.markdown(raw)
        else:
            st.markdown(raw)

        for index, event in enumerate(message.get("tool_events") or [], start=1):
            render_tool_trace(event, index)

user_text = st.chat_input("Message Northstar IT Desk…")
if user_text:
    if provider is None:
        st.error("The provider is not ready. Check the runtime settings and `.env`.")
        st.stop()

    if not session["messages"]:
        session["title"] = user_text.strip()[:42] or "New helpdesk chat"

    session["messages"].append({"role": "user", "content": user_text})
    turn_index = len(session["turns"]) + 1
    turn_record: dict[str, Any] = {
        "turn_index": turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(session["history"], history_window),
        {"role": "user", "content": user_text},
    ]

    try:
        with st.spinner("Checking the service desk…"):
            result = run_model_tool_loop(
                provider=provider,
                messages=messages,
                tools=openai_tools,
                model=model_override.strip() or None,
                max_tool_rounds=max_tool_rounds,
            )
        assistant_text = result.get("assistant_text") or "No response was returned."
        turn_record.update(result)
        session["messages"].append(
            {
                "role": "assistant",
                "content": assistant_text,
                "tool_events": result.get("tool_events") or [],
                "status": result.get("status"),
            }
        )
        session["history"].extend(
            [
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": assistant_text},
            ]
        )
    except Exception as exc:
        error_text = f"{type(exc).__name__}: {exc}"
        turn_record.update({"status": "provider_error", "error": error_text})
        session["messages"].append(
            {
                "role": "assistant",
                "content": f"⚠️ **Provider error**\n\n`{error_text}`",
                "tool_events": [],
                "status": "provider_error",
            }
        )

    turn_record["ended_at"] = now_iso()
    session["turns"].append(turn_record)
    transcript_path = TRANSCRIPTS_DIR / (
        f"ui_{safe_slug(version)}_{safe_slug(provider_name)}_{session['id']}.transcript.json"
    )
    payload = transcript_payload(
        session,
        provider_name=provider_name,
        selected_model=selected_model,
        artifact=artifact,
        system_prompt_path=system_prompt_path,
        tools_path=tools_path,
        history_window=history_window,
        max_tool_rounds=max_tool_rounds,
    )
    write_transcript(transcript_path, payload)
    session["transcript_path"] = str(transcript_path)
    st.rerun()
