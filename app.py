import streamlit as st
import requests
import time
import json

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
        font-size: 0.78rem; line-height: 1.9; color: #aaa;
        max-height: 300px; overflow-y: auto;
    }
    .script-box span.host  { color: #e8ff3f; font-weight: 700; }
    .script-box span.guest { color: #7fefff; font-weight: 700; }
    .info-box {
        background: #111827; border: 1px solid #1f2937; border-radius: 6px;
        padding: 0.8rem 1rem; font-family: 'Space Mono', monospace;
        font-size: 0.78rem; color: #6b7280; margin-bottom: 1rem;
    }
    .divider { border: none; border-top: 1px solid #1e1e1e; margin: 1.5rem 0; }
    .state-badge {
        display: inline-block; padding: 2px 10px; border-radius: 20px;
        font-family: 'Space Mono', monospace; font-size: 0.75rem; font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
KIE_BASE        = "https://api.kie.ai/api/v1"
CREATE_URL      = f"{KIE_BASE}/jobs/createTask"
POLL_URL        = f"{KIE_BASE}/jobs/recordInfo"   # ← correct endpoint
POLL_INTERVAL   = 5    # seconds between polls
MAX_POLLS       = 72   # 72 × 5s = 6 minutes max

VOICES = {
    "Adam  (deep, authoritative)":     "TX3LPaxmHKxFdv7VOQHJ",
    "Jessica  (warm, conversational)": "cgSgspJ2msm6clMCkdW9",
    "Charlie  (casual, energetic)":    "IKne3meq5aSn9XLyUdCD",
    "Matilda  (calm, storyteller)":    "XrExE9yKIg1WjnnlVkGX",
}

LANGUAGES = {
    "Auto-detect": "auto", "English": "en", "Spanish": "es",
    "French": "fr", "German": "de", "Portuguese": "pt",
    "Italian": "it", "Japanese": "ja", "Korean": "ko",
    "Mandarin Chinese": "zh", "Hindi": "hi", "Arabic": "ar",
}

FORMATS = {
    "🎙 Interview Podcast":    "interview",
    "🗣 Debate / Discussion":  "debate",
    "📖 Storytelling":         "story",
    "📰 News Briefing":        "news",
}

EPISODE_LENGTHS = {
    "Short (~60 sec)":   6,
    "Medium (~2 min)":  10,
    "Long (~4 min)":    18,
}

# ── Script builder ─────────────────────────────────────────────────────────────
def build_dialogue(topic, fmt, hv, gv, n_turns):
    H, G = hv, gv
    t = topic

    pools = {
        "interview": [
            (H, f"[excitedly] Welcome back, everyone! Today we're exploring {t}. Joining me is our resident expert — great to have you!"),
            (G, f"[warmly] Great to be here! {t} is something I genuinely get excited about… there's so much happening right now."),
            (H, "Why should our listeners care about this right now?"),
            (G, f"[thoughtfully] Because {t} isn't just a trend… it's fundamentally reshaping entire industries."),
            (H, "Give me a concrete example."),
            (G, f"[enthusiastically] Take healthcare — or finance — or education. {t} is delivering results nobody imagined five years ago."),
            (H, "What are the biggest risks?"),
            (G, "[sighs] Honestly? Regulation hasn't caught up — and most people still don't fully grasp what's at stake."),
            (H, "Who's leading the charge right now?"),
            (G, "[curiously] A mix of scrappy startups and a few legacy players who finally woke up. It's a fascinating race."),
            (H, "Where do you see this in five years?"),
            (G, "[awed] Completely mainstream. What feels cutting-edge today will feel obvious — maybe even quaint — by then."),
            (H, f"Last question — advice for someone just getting started with {t}?"),
            (G, "[laughs softly] Start small. Stay curious. Don't be afraid to be wrong — this field moves fast."),
            (H, "[warmly] Perfect. Thank you so much for being here today!"),
            (G, "My pleasure. Can't wait to do this again."),
            (H, "And that's a wrap for today's show — we'll see you next time!"),
        ],
        "debate": [
            (H, f"[firmly] Today we're debating {t} — I'll argue the optimistic case. Ready?"),
            (G, f"[sarcastic] Always ready to challenge optimism! {t} has serious problems nobody's talking about."),
            (H, "The data clearly shows progress — you can't ignore that."),
            (G, "Progress for whom, exactly? That's — [pauses] — that's the real question."),
            (H, "[frustrated] You're moving the goalposts. The core benefits are undeniable."),
            (G, "[firmly] I'm not moving anything. I'm saying we need to be honest about tradeoffs."),
            (H, "Name one tradeoff you'd actually fix."),
            (G, "[thoughtfully] More transparency. Better accountability. Slower rollout in high-stakes areas."),
            (H, "Slower rollout means people miss out on life-changing benefits. That's a cost too."),
            (G, "Fair — but moving too fast and breaking things has costs no one wants to admit."),
            (H, "[conceding] Okay… maybe we're not as far apart as I thought."),
            (G, f"[laughs] We never are. Nuance always wins when it comes to {t}."),
            (H, "So — common ground: move fast, but with eyes open."),
            (G, "Exactly. Eyes wide open."),
            (H, "A rare moment of agreement on this show — tune in next week for round two!"),
        ],
        "story": [
            (H, f"[softly] Imagine a world where {t} is part of everyday life… shaping choices before we even realize it."),
            (G, "[curiously] That world isn't as far away as it sounds, is it?"),
            (H, "Not at all. In fact… it's already beginning."),
            (G, "[whispering] Tell me everything."),
            (H, f"It started with a simple question: what if {t} could solve a problem nobody had thought to tackle before?"),
            (G, "[awed] And then what happened?"),
            (H, "Then — [pauses dramatically] — everything changed. Not overnight. But irreversibly."),
            (G, "Who drove that change?"),
            (H, "A small team. Underfunded, underestimated… and absolutely relentless."),
            (G, "[reflectively] The best stories always start that way, don't they?"),
            (H, "Every single time. And the beautiful thing? This story isn't over."),
            (G, "[warmly] It's barely begun."),
            (H, "So if you're listening — wondering whether you have a role to play in this — you do."),
            (G, "Everyone does. That's the whole point."),
            (H, "[softly] And that… is where we leave you tonight."),
        ],
        "news": [
            (H, f"[crisply] Good morning. Here are today's top stories on {t}."),
            (G, f"[professionally] {t} continues to dominate headlines — with three major developments overnight."),
            (H, "First: new research suggests the pace of change is accelerating faster than experts predicted."),
            (G, "Second: industry leaders are calling for clearer guidelines — and regulators appear ready to respond."),
            (H, f"[seriously] Third: a new report highlights both the promise and the risks of {t} — urging caution without slowing innovation."),
            (G, "We spoke to three analysts this morning. All three used the same word: pivotal."),
            (H, "What's driving that urgency?"),
            (G, "Investment is up — but so is scrutiny. The honeymoon phase may be ending."),
            (H, "Does that mean a slowdown?"),
            (G, "[firmly] Not a slowdown. A maturation. There's a difference."),
            (H, "Analysts say the next 90 days will be critical. We'll be watching closely."),
            (G, "[warmly] Stay with us for live updates throughout the day. Full reports are linked below."),
            (H, "I'm your host — thanks for starting your morning with us."),
        ],
    }

    lines = pools[fmt][:n_turns]
    return [{"text": text, "voice": voice_id} for voice_id, text in lines]


# ── Polling helper ─────────────────────────────────────────────────────────────
def poll_task(task_id, headers, bar, status_text):
    """
    Polls /api/v1/jobs/recordInfo until state == 'success' or 'fail'.
    Returns (audio_url, raw_data) or raises on failure.
    """
    for i in range(MAX_POLLS):
        time.sleep(POLL_INTERVAL)
        try:
            r    = requests.get(POLL_URL, params={"taskId": task_id},
                                headers=headers, timeout=15)
            data = r.json()
        except Exception as e:
            status_text.warning(f"Polling error (retry {i+1}): {e}")
            continue

        inner = data.get("data") or {}
        state = inner.get("state", "unknown")          # waiting|queuing|generating|success|fail
        elapsed = (i + 1) * POLL_INTERVAL

        pct = min((i + 1) / MAX_POLLS, 0.95)
        bar.progress(pct, text=f"⏳ State: **{state}** — {elapsed}s elapsed")

        if state == "success":
            bar.progress(1.0, text="✅ Done!")
            # resultJson is a JSON-encoded string
            result_raw = inner.get("resultJson", "{}")
            try:
                result = json.loads(result_raw) if isinstance(result_raw, str) else result_raw
            except Exception:
                result = {}
            # Try common key patterns
            audio_url = (
                result.get("audioUrl")
                or result.get("audio_url")
                or result.get("url")
                or (result.get("resultUrls") or [None])[0]
            )
            return audio_url, data

        if state == "fail":
            return None, data

    return None, {"timeout": True}


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

length_label = st.sidebar.selectbox("⏱ Episode Length", list(EPISODE_LENGTHS.keys()), index=1)
n_turns      = EPISODE_LENGTHS[length_label]

st.sidebar.markdown("---")
st.sidebar.markdown("<small style='color:#444'>Powered by KIE · ElevenLabs V3<br>Poll endpoint: /jobs/recordInfo</small>",
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

# ── Script preview ─────────────────────────────────────────────────────────────
if topic.strip():
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("### 📝 Script Preview")
    preview = build_dialogue(topic, fmt, host_voice, guest_voice, n_turns)
    rows = []
    for line in preview:
        role  = "host" if line["voice"] == host_voice else "guest"
        label = "HOST" if role == "host" else "GUEST"
        rows.append(f'<span class="{role}">[{label}]</span> {line["text"]}<br>')
    st.markdown(f'<div class="script-box">{"".join(rows)}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="info-box">🎙 {len(preview)} lines · {length_label} · '
        f'language: {lang_label} · stability: {stability}</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Generate ───────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    generate = st.button("▶  Generate Podcast Audio")
with col2:
    show_debug = st.checkbox("Debug", value=False)

if generate:
    if not api_key:
        st.error("🔑 Add your KIE API key in the sidebar.")
        st.stop()
    if not topic.strip():
        st.error("✏️ Enter a topic first.")
        st.stop()

    dialogue = build_dialogue(topic, fmt, host_voice, guest_voice, n_turns)
    headers  = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload  = {
        "model": "elevenlabs/text-to-dialogue-v3",
        "input": {
            "stability":     stability,
            "language_code": language,
            "dialogue":      dialogue,
        },
    }

    # ── Step 1: Create task ────────────────────────────────────────────────────
    with st.spinner("Submitting task to KIE…"):
        try:
            r   = requests.post(CREATE_URL, headers=headers, json=payload, timeout=30)
            res = r.json()
        except Exception as e:
            st.error(f"Request failed: {e}")
            st.stop()

    if show_debug:
        with st.expander("createTask response", expanded=True):
            st.json(res)

    if res.get("code") != 200:
        st.error(f"API error {res.get('code')}: {res.get('msg') or res}")
        st.stop()

    task_id = res["data"]["taskId"]
    st.info(f"Task created → `{task_id}`")

    # ── Step 2: Poll recordInfo ────────────────────────────────────────────────
    bar         = st.progress(0, text="Waiting for generation to start…")
    status_text = st.empty()

    audio_url, raw = poll_task(task_id, headers, bar, status_text)

    if show_debug:
        with st.expander("Last poll response", expanded=False):
            st.json(raw)

    # ── Step 3: Result ─────────────────────────────────────────────────────────
    if audio_url:
        st.success("🎧 Your podcast is ready!")
        st.audio(audio_url)
        cost = (raw.get("data") or {}).get("costTime")
        if cost:
            st.caption(f"Generated in {cost/1000:.1f}s")
        st.markdown(
            f"<a href='{audio_url}' target='_blank' "
            f"style='color:#e8ff3f; font-family:monospace; font-size:0.85rem;'>"
            f"⬇ Download MP3</a>",
            unsafe_allow_html=True,
        )
    elif raw.get("timeout"):
        st.warning(
            f"⏰ Timed out after {MAX_POLLS * POLL_INTERVAL // 60} min. "
            f"Your task `{task_id}` may still be running — check the KIE dashboard."
        )
    else:
        inner  = raw.get("data") or {}
        errmsg = inner.get("failMsg") or "Unknown error"
        st.error(f"Generation failed: {errmsg}")
        if show_debug:
            st.json(raw)
