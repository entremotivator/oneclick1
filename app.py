import streamlit as st
import requests
import time

st.set_page_config(page_title="Podcast Generator", page_icon="🎙️")

st.title("🎙️ One Click Podcast Generator")

# Sidebar
st.sidebar.title("API Settings")
API_KEY = st.sidebar.text_input("KIE API Key", type="password")

topic = st.text_area("Podcast Topic", "The future of AI and jobs")

if st.button("Generate Podcast"):

    if not API_KEY:
        st.error("Enter API key")
        st.stop()

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # create podcast dialogue
    payload = {
        "model": "elevenlabs/text-to-dialogue-v3",
        "input": {
            "dialogue": [
                {"text": f"Welcome to today's podcast. Today we discuss {topic}.", "voice": "Adam"},
                {"text": f"That's interesting. I think {topic} will dramatically change industries.", "voice": "Rachel"},
                {"text": "Let's explore some real examples and predictions.", "voice": "Adam"},
                {"text": "Absolutely, this topic is shaping the future.", "voice": "Rachel"}
            ],
            "stability": 0.5
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

    # poll result
    status_url = f"https://api.kie.ai/api/v1/jobs/getTask?taskId={task_id}"

    with st.spinner("Generating podcast audio..."):

        for _ in range(30):

            r = requests.get(status_url, headers=headers)
            data = r.json()

            if data["data"]["status"] == "success":

                audio_url = data["data"]["output"]["audioUrl"]

                st.audio(audio_url)

                st.markdown(f"[Download Podcast]({audio_url})")

                break

            time.sleep(3)
