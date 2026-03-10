import streamlit as st
import requests
import time

st.set_page_config(page_title="AI Podcast Generator", page_icon="🎙️", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Syne', sans-serif;
    }
    .stApp {
        background: #0d0d0d;
        color: #f0f0f0;
    }
    h1 { font-size: 2.2rem !important; font-weight: 800 !important; letter-spacing: -1px; }
    .stButton > button {
        background: #e8ff3f;
        color: #0d0d0d;
        font-family: 'Space Mono', monospace;
        font-weight: 700;
        border: none;
        border-radius: 4px;
        padding: 0.6rem 2rem;
        font-size: 1rem;
        width: 100%;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.85; }
    .stTextArea textarea, .stTextInput input, .stSelectbox select {
        background: #1a1a1a !important;
        border: 1px solid #333 !important;
        color: #f0f0f0 !important;
        border-radius: 4px !important;
        font-family: 'Space Mono', monospace !important;
    }
    .stSidebar { background: #111 !important; }
    .stSidebar label { color: #aaa !important; font-size: 0.85rem; }
    .tag {
        display: inline-block;
        background: #1e1e1e;
        border: 1px solid #333;
        color: #e8ff3f;
        font-family: 'Space Mono', monospace;
        font-size: 0.75rem;
        padding: 2px 10px;
        border-radius: 20px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────
st.sidebar.markdown("### ⚙️ Settings")

api_key = st.sidebar.text_input("KIE API Key", type="password", placeholder="sk-...")

VOICES = {
    "Adam  (deep, authoritative)": "TX3LPaxmHKxFdv7VOQHJ",
    "Jessica  (warm, conversational)": "cgSgspJ2msm6clMCkdW9",
}

host_label  = st.sidebar.selectbox("Host Voice",  list(VOICES.keys()), index=0)
guest_label = st.sidebar.selectbox("Guest Voice", list(VOICES.keys()), index=1)
host_voice  = VOICES[host_label]
guest_voice = VOICES[guest_label]

stability = st.sidebar.slider("Voice Stability", 0.0, 1.0, 0.5, 0.05)

st.sidebar.markdown("---")
st.sidebar.markdown("<small style='color:#555'>Powered by KIE · ElevenLabs v3</small>", unsafe_allow_html=True)

# ── Main ─────────────────────────────────────────────────
st.markdown('<div class="tag">🎙 AI PODCAST STUDIO</div>', unsafe_allow_html=True)
st.title("One-Click Podcast Generator")
st.markdown("<p style='color:#777; margin-top:-0.5rem;'>Type a topic → get a ready-to-share podcast clip.</p>", unsafe_allow_html=True)

topic = st.text_area(
    "What's the podcast about?",
    placeholder="e.g. The future of artificial intelligence in healthcare",
    height=100,
)

generate = st.button("▶  Generate Podcast")

# ── Logic ─────────────────────────────────────────────────
if generate:
    if not api_key:
        st.error("🔑 Add your KIE API key in the sidebar.")
        st.stop()
    if not topic.strip():
        st.error("✏️ Enter a topic first.")
        st.stop()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    dialogue = [
        {"text": f"[excitedly] Welcome to today's show! Our topic: {topic}.", "voice": host_voice},
        {"text": f"[curious] Fascinating choice! {topic} is reshaping so many industries.", "voice": guest_voice},
        {"text": "Why is it becoming so important right now?", "voice": host_voice},
        {"text": f"Because {topic} is accelerating innovation at an unprecedented pace.", "voice": guest_voice},
        {"text": "What should our listeners expect in the near future?", "voice": host_voice},
        {"text": "[thoughtfully] Honestly, we're only at the beginning of a massive transformation.", "voice": guest_voice},
        {"text": "Any advice for people who want to stay ahead of the curve?", "voice": host_voice},
        {"text": "Stay curious, keep learning, and don't be afraid to experiment. That's the key.", "voice": guest_voice},
    ]

    payload = {
        "model": "elevenlabs/text-to-dialogue-v3",
        "input": {
            "stability": stability,
            "language_code": "auto",
            "dialogue": dialogue,
        },
    }

    with st.spinner("Creating task…"):
        r = requests.post(
            "https://api.kie.ai/api/v1/jobs/createTask",
            headers=headers,
            json=payload,
            timeout=30,
        )
        res = r.json()

    if res.get("code") != 200:
        st.error(f"API error: {res}")
        st.stop()

    task_id = res["data"]["taskId"]
    st.info(f"Task ID: `{task_id}`")

    status_url = f"https://api.kie.ai/api/v1/jobs/getTask?taskId={task_id}"
    progress = st.progress(0, text="Generating audio…")

    for i in range(40):
        time.sleep(3)
        r2 = requests.get(status_url, headers=headers, timeout=15)
        data = r2.json()
        status = data["data"]["status"]
        progress.progress(min((i + 1) / 40, 0.95), text=f"Status: {status} ({(i+1)*3}s)")

        if status == "success":
            progress.progress(1.0, text="Done!")
            audio_url = data["data"]["output"]["audioUrl"]

            st.success("🎧 Your podcast is ready!")
            st.audio(audio_url)
            st.markdown(
                f"<a href='{audio_url}' target='_blank' style='color:#e8ff3f; font-family:monospace;'>⬇ Download audio</a>",
                unsafe_allow_html=True,
            )
            break

        if status == "failed":
            progress.empty()
            st.error("Generation failed.")
            st.json(data)
            break
    else:
        st.warning("Timed out waiting for audio. Check the task ID manually.")
