import streamlit as st
import requests
import time

st.set_page_config(page_title="AI Podcast Generator", page_icon="🎙️", layout="centered")

st.title("🎙️ One-Click AI Podcast Generator")
st.write("Create a short AI podcast conversation instantly using KIE AI")

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("🔑 API Settings")

API_KEY = st.sidebar.text_input(
    "KIE AI API Key",
    type="password",
)

host1 = st.sidebar.selectbox(
    "Host 1 Voice",
    ["Adam", "James", "Brian", "Chris"]
)

host2 = st.sidebar.selectbox(
    "Host 2 Voice",
    ["Jessica", "Amy", "Laura", "Charlotte"]
)

# -----------------------------
# Main UI
# -----------------------------
topic = st.text_area(
    "Podcast Topic",
    placeholder="Example: The future of AI and how it will impact jobs",
)

generate = st.button("🎧 Generate Podcast")

# -----------------------------
# Generate Podcast
# -----------------------------
if generate:

    if not API_KEY:
        st.error("Please enter your API key in the sidebar")
        st.stop()

    if not topic:
        st.error("Please enter a podcast topic")
        st.stop()

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    dialogue = [
        {"text": f"Welcome everyone to today's podcast. Today we're discussing {topic}.", "voice": host1},
        {"text": f"I'm excited about this topic. {topic} is changing the world rapidly.", "voice": host2},
        {"text": "Let's start with the big question. Why does this matter right now?", "voice": host1},
        {"text": f"Great question. {topic} is affecting businesses, technology, and everyday life.", "voice": host2},
        {"text": "Can you give some real world examples?", "voice": host1},
        {"text": f"Sure. We're already seeing major industries adopt solutions related to {topic}.", "voice": host2},
        {"text": "That's fascinating. It sounds like we're just getting started.", "voice": host1},
        {"text": "Absolutely. The next few years will be incredibly interesting.", "voice": host2}
    ]

    payload = {
        "model": "elevenlabs/text-to-dialogue-v3",
        "input": {
            "dialogue": dialogue,
            "stability": 0.5
        }
    }

    with st.spinner("🚀 Creating podcast task..."):

        response = requests.post(
            "https://api.kie.ai/api/v1/jobs/createTask",
            headers=headers,
            json=payload
        )

        data = response.json()

        if data.get("code") != 200:
            st.error(data)
            st.stop()

        task_id = data["data"]["taskId"]

    st.success(f"Task Created: {task_id}")

    status_url = f"https://api.kie.ai/api/v1/jobs/getTask?taskId={task_id}"

    progress = st.progress(0)

    with st.spinner("🎙 Generating podcast audio..."):

        for i in range(40):

            r = requests.get(status_url, headers=headers)
            result = r.json()

            status = result["data"]["status"]

            progress.progress((i+1)/40)

            if status == "success":

                audio_url = result["data"]["output"]["audioUrl"]

                st.success("✅ Podcast Ready!")

                st.audio(audio_url)

                st.markdown(f"⬇️ [Download Podcast]({audio_url})")

                break

            elif status == "failed":

                st.error("Generation failed")
                st.write(result)
                break

            time.sleep(3)

        else:
            st.warning("Still processing. Try again in a moment.")
