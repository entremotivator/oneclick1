import streamlit as st
import requests
import time

st.set_page_config(page_title="AI Podcast Generator", page_icon="🎙️")

st.title("🎙️ One-Click AI Podcast Generator")

# -------------------
# Sidebar
# -------------------

st.sidebar.header("API Settings")

api_key = st.sidebar.text_input(
    "KIE API Key",
    type="password"
)

voice_host = st.sidebar.selectbox(
    "Host Voice",
    {
        "Adam": "TX3LPaxmHKxFdv7VOQHJ"
    }
)

voice_guest = st.sidebar.selectbox(
    "Guest Voice",
    {
        "Jessica": "cgSgspJ2msm6clMCkdW9"
    }
)

# -------------------
# Input
# -------------------

topic = st.text_area(
    "Podcast Topic",
    placeholder="Example: The future of artificial intelligence"
)

generate = st.button("Generate Podcast")

# -------------------
# Generate
# -------------------

if generate:

    if not api_key:
        st.error("Enter API key")
        st.stop()

    if not topic:
        st.error("Enter a topic")
        st.stop()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    dialogue = [
        {
            "text": f"[excitedly] Welcome to today's podcast. Our topic is {topic}.",
            "voice": voice_host
        },
        {
            "text": f"[curious] That's a fascinating topic! {topic} is changing so many industries.",
            "voice": voice_guest
        },
        {
            "text": "Why do you think it's becoming so important right now?",
            "voice": voice_host
        },
        {
            "text": f"I think it's because {topic} is accelerating innovation everywhere.",
            "voice": voice_guest
        },
        {
            "text": "What should people expect in the future?",
            "voice": voice_host
        },
        {
            "text": "Honestly, we're just at the beginning of a huge transformation.",
            "voice": voice_guest
        }
    ]

    payload = {
        "model": "elevenlabs/text-to-dialogue-v3",
        "input": {
            "stability": 0.5,
            "language_code": "auto",
            "dialogue": dialogue
        }
    }

    with st.spinner("Creating audio task..."):

        r = requests.post(
            "https://api.kie.ai/api/v1/jobs/createTask",
            headers=headers,
            json=payload
        )

        res = r.json()

        if res["code"] != 200:
            st.error(res)
            st.stop()

        task_id = res["data"]["taskId"]

    st.success(f"Task Created: {task_id}")

    status_url = f"https://api.kie.ai/api/v1/jobs/getTask?taskId={task_id}"

    with st.spinner("Generating podcast..."):

        for i in range(40):

            r = requests.get(status_url, headers=headers)
            data = r.json()

            status = data["data"]["status"]

            if status == "success":

                audio_url = data["data"]["output"]["audioUrl"]

                st.success("Podcast Ready!")

                st.audio(audio_url)

                st.markdown(f"Download Podcast: {audio_url}")

                break

            if status == "failed":

                st.error("Generation failed")
                st.write(data)
                break

            time.sleep(3)
