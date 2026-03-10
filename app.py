import streamlit as st
import requests
import time

st.set_page_config(page_title="AI Podcast Studio", page_icon="🎙️", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
    .stApp { background: #0a0a0a; color: #f0f0f0; }
    h1 { font-size: 2.2rem !important; font-weight: 800 !important; letter-spacing: -1px; }
    h3 { font-weight: 700 !important; color: #e8ff3f !important; font-size: 1rem !important; }
    .stButton > button {
        background: #e8ff3f; color: #0a0a0a;
        font-family: 'Space Mono', monospace; font-weight: 700;
        border: none; border-radius: 4px; padding: 0.65rem 2rem;
        font-size: 1rem; width: 100%; transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.82; }
    .stTextArea textarea, .stTextInput input {
        background: #161616 !important; border: 1px solid #2a2a2a !important;
        color: #f0f0f0 !important; border-radius: 4px !important;
        font-family: 'Space Mono', monospace !important; font-size: 0.85rem !important;
    }
    .stSelectbox > div > div {
        background: #161616 !important; border: 1px solid #2a2a2a !important;
        color: #f0f0f0 !important;
    }
    .stSidebar { background: #0e0e0e !important; border-right: 1px solid #1e1e1e; }
    .stSidebar label { color: #888 !important; font-size: 0.82rem !important; }
    .pill {
        display: inline-block; background: #161616; border: 1px solid #2a2a2a;
        color: #e8ff3f; font-family: 'Space Mono', monospace;
        font-size: 0.72rem; padding: 3px 12px; border-radius: 20px; margin-bottom: 1.2rem;
    }
    .script-box {
        background: #111; border: 1px solid #222; border-radius: 6px;
        padding: 1rem 1.2rem; font-family: 'Space Mono', monospace;
        font-size: 0.78rem; line-height: 1.8; color: #aaa;
        max-height: 280px; overflow-y: auto;
    }
    .script-box span.host  { color: #e8ff3f; font-weight: 700; }
    .script-box span.guest { color: #7fefff; font-weight: 700; }
    .divider { border: none; border-top: 1px solid #1e1e1e; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Voice library ──────────────────────────────────────────────────────────────
VOICES = {
    "Adam  (deep, authoritative)":     "TX3LPaxmHKxFdv7VOQHJ",
    "Jessica  (warm, conversational)": "cgSgspJ2msm6clMCkdW9",
    "Charlie  (casual, energetic)":    "IKne3meq5aSn9XLyUdCD",
    "Matilda  (calm, storyteller)":    "XrExE9yKIg1WjnnlVkGX",
}

LANGUAGES = {
    "Auto-detect": "auto",
    "English": "en", "Spanish": "es", "French": "fr", "German": "de",
    "Portuguese": "pt", "Italian": "it", "Japanese": "ja", "Korean": "ko",
    "Mandarin Chinese": "zh", "Hindi": "hi", "Arabic": "ar",
}

FORMATS = {
    "🎙 Interview Podcast": "interview",
    "🗣 Debate / Discussion": "debate",
    "📖 Storytelling Narration": "story",
    "📰 News Briefing": "news",
}

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.markdown("### ⚙️ Configuration")
api_key = st.sidebar.text_input("KIE API Key", type="password", placeholder="sk-...")

st.sidebar.markdown("---")
host_label  = st.sidebar.selectbox("🟡 Host Voice",  list(VOICES.keys()), index=0)
guest_label = st.sidebar.selectbox("🔵 Guest Voice", list(VOICES.keys()), index=1)
host_voice  = VOICES[host_label]
guest_voice = VOICES[guest_label]

lang_label = st.sidebar.selectbox("🌐 Language", list(LANGUAGES.keys()), index=0)
language   = LANGUAGES[lang_label]

stability = st.sidebar.slider(
    "🎚 Voice Stability", 0.0, 1.0, 0.45, 0.05,
    help="Lower = more expressive. Higher = more consistent."
)
st.sidebar.markdown("---")
st.sidebar.markdown("<small style='color:#444'>Powered by KIE · ElevenLabs V3</small>",
                    unsafe_allow_html=True)

# ── Main ───────────────────────────────────────────────────────────────────────
st.markdown('<div class="pill">🎙 AI PODCAST STUDIO</div>', unsafe_allow_html=True)
st.title("One-Click Podcast Generator")
st.markdown(
    "<p style='color:#555; margin-top:-0.6rem; font-size:0.92rem;'>"
    "Type a topic, pick a format, get broadcast-ready audio.</p>",
    unsafe_allow_html=True,
)

topic     = st.text_area("Podcast topic", placeholder="e.g. The future of AI in healthcare", height=80)
fmt_label = st.selectbox("Show format", list(FORMATS.keys()))
fmt       = FORMATS[fmt_label]


# ── Script builder ─────────────────────────────────────────────────────────────
def build_dialogue(topic, fmt, hv, gv):
    """
    Returns list of {text, voice} dicts.
    Uses audio tags, ellipses and dashes per ElevenLabs V3 best practices.
    """
    H, G = hv, gv
    t = topic  # shorthand

    if fmt == "interview":
        lines = [
            (H, f"[excitedly] Welcome back, everyone! Today we're diving deep into {t}. Joining me is our resident expert — great to have you here!"),
            (G, f"[warmly] Great to be here! {t} is something I genuinely get excited about… there's so much happening right now."),
            (H, "So — let's start at the top. Why should our listeners care about this right now?"),
            (G, f"[thoughtfully] Because {t} isn't just a trend… it's fundamentally changing how we think about — well, almost everything."),
            (H, "That's a bold claim! Give me a concrete example."),
            (G, f"[enthusiastically] Sure! Take healthcare — or finance — or education. {t} is already delivering results that would have seemed impossible five years ago."),
            (H, "And where do you see the biggest risks?"),
            (G, "[sighs] Honestly? The risks are real. Regulation hasn't caught up, and most people still don't fully understand what's at stake."),
            (H, f"Last question — what's your advice for someone just getting started with {t}?"),
            (G, "[laughs softly] Start small. Stay curious. And don't be afraid to be wrong — because this field moves fast."),
            (H, "[warmly] Love that. Thanks so much for being here today!"),
        ]
    elif fmt == "debate":
        lines = [
            (H, f"[firmly] Today we're debating {t} — and I'll argue the optimistic case. Ready?"),
            (G, f"[sarcastic] Oh, I'm always ready to challenge optimism! {t} has some serious problems people aren't talking about."),
            (H, "But the data clearly shows progress — you can't ignore that."),
            (G, "Progress for whom, exactly? That's — [pauses] — that's the real question."),
            (H, "[frustrated] You're moving the goalposts. The core benefits are undeniable."),
            (G, "[firmly] I'm not moving anything. I'm saying we need to be honest about tradeoffs."),
            (H, "Fair point. What would you actually change?"),
            (G, "[thoughtfully] More transparency. Better accountability. And — honestly — a slower rollout in high-stakes areas."),
            (H, "[conceding] Okay… I can get behind that. Maybe we're not as far apart as I thought."),
            (G, f"[laughs] We never are. That's the thing about {t} — nuance always wins in the end."),
        ]
    elif fmt == "story":
        lines = [
            (H, f"[softly] Imagine a world where {t} is part of everyday life… where it shapes the choices we make before we even realize it."),
            (G, "[curiously] That world isn't as far away as it sounds, is it?"),
            (H, "Not at all. In fact… it's already beginning. Let me tell you a story."),
            (G, "[whispering] I'm listening."),
            (H, f"It started with a simple question: what if {t} could solve a problem nobody had thought to tackle before?"),
            (G, "[awed] And then what happened?"),
            (H, "Then — [pauses dramatically] — everything changed. Not overnight. But irreversibly."),
            (G, f"[reflectively] Stories like that remind us why {t} matters beyond the headlines."),
            (H, "Exactly. It's never just about technology. It's about people. And what we choose to do with the tools we're given."),
            (G, "[warmly] A perfect note to end on. Thank you for sharing that."),
        ]
    else:  # news
        lines = [
            (H, f"[crisply] Good morning. Here are today's top stories on {t}."),
            (G, f"[professionally] {t} continues to dominate headlines — with three major developments overnight."),
            (H, "First: new research suggests the pace of change is accelerating faster than most experts predicted."),
            (G, "Second: industry leaders are calling for clearer guidelines — and regulators appear ready to respond."),
            (H, f"[seriously] And third: a new report highlights both the promise and the risks of {t} — urging caution without slowing innovation."),
            (G, "Analysts say the next 90 days will be critical in shaping how this evolves."),
            (H, "We'll be watching closely. Stay with us for live updates throughout the day."),
            (G, "[warmly] And if you want to go deeper — full reports are linked below."),
        ]

    return [{"text": text, "voice": voice_id} for voice_id, text in lines]


# ── Live script preview ────────────────────────────────────────────────────────
if topic.strip():
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("### 📝 Script Preview")
    preview = build_dialogue(topic, fmt, host_voice, guest_voice)
    rows = []
    for line in preview:
        role  = "host" if line["voice"] == host_voice else "guest"
        label = "HOST" if role == "host" else "GUEST"
        rows.append(f'<span class="{role}">[{label}]</span> {line["text"]}<br>')
    st.markdown(f'<div class="script-box">{"".join(rows)}</div>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Generate button ────────────────────────────────────────────────────────────
generate = st.button("▶  Generate Podcast Audio")

if generate:
    if not api_key:
        st.error("🔑 Add your KIE API key in the sidebar.")
        st.stop()
    if not topic.strip():
        st.error("✏️ Enter a topic first.")
        st.stop()

    dialogue = build_dialogue(topic, fmt, host_voice, guest_voice)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "elevenlabs/text-to-dialogue-v3",
        "input": {
            "stability": stability,
            "language_code": language,
            "dialogue": dialogue,
        },
    }

    with st.spinner("Submitting to KIE…"):
        try:
            r   = requests.post(
                "https://api.kie.ai/api/v1/jobs/createTask",
                headers=headers, json=payload, timeout=30,
            )
            res = r.json()
        except Exception as e:
            st.error(f"Request failed: {e}")
            st.stop()

    if res.get("code") != 200:
        st.error(f"API error: {res}")
        st.stop()

    task_id = res["data"]["taskId"]
    st.info(f"Task submitted → `{task_id}`")

    status_url = f"https://api.kie.ai/api/v1/jobs/getTask?taskId={task_id}"
    bar = st.progress(0, text="Generating audio…")

    for i in range(60):
        time.sleep(3)
        try:
            r2   = requests.get(status_url, headers=headers, timeout=15)
            data = r2.json()
        except Exception as e:
            st.warning(f"Polling error: {e}")
            continue

        status = data["data"]["status"]
        bar.progress(min((i + 1) / 60, 0.95),
                     text=f"Status: {status} ({(i+1)*3}s elapsed)")

        if status == "success":
            bar.progress(1.0, text="Done!")
            audio_url = data["data"]["output"]["audioUrl"]
            st.success("🎧 Your podcast is ready!")
            st.audio(audio_url)
            st.markdown(
                f"<a href='{audio_url}' target='_blank' "
                f"style='color:#e8ff3f; font-family:monospace; font-size:0.85rem;'>"
                f"⬇ Download MP3</a>",
                unsafe_allow_html=True,
            )
            break

        if status == "failed":
            bar.empty()
            st.error("Generation failed.")
            st.json(data)
            break
    else:
        st.warning("Timed out (3 min). Task may still be processing — check the KIE dashboard.")
