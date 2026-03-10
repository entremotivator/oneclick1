import streamlit as st
import requests
import base64

st.set_page_config(page_title="One-Click Podcast Generator", page_icon="🎙️")

st.title("🎙️ One-Click Podcast Generator")
st.write("Generate a 2-speaker podcast instantly using KIE AI Dialogue API")

# Sidebar for API key
st.sidebar.header("🔑 API Settings")
api_key = st.sidebar.text_input("KIE AI API Key", type="password")

# Podcast input
topic = st.text_area(
    "Podcast Topic / Script",
    placeholder="Example: Discuss the future of AI and how it will change jobs..."
)

generate = st.button("🎧 Generate Podcast")

if generate:
    if not api_key:
        st.error("Please enter your API key in the sidebar")
    elif not topic:
        st.error("Please enter a podcast topic or script")
    else:
        with st.spinner("Generating podcast..."):

            url = "https://api.kie.ai/api/v1/elevenlabs/text-to-dialogue-v3"

            payload = {
                "text": topic,
                "voice_1": "Rachel",
                "voice_2": "Adam",
                "model_id": "eleven_multilingual_v2"
            }

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers)

            if response.status_code != 200:
                st.error(f"API Error: {response.text}")
            else:
                data = response.json()

                # assume API returns base64 audio
                audio_base64 = data.get("audio")

                if audio_base64:
                    audio_bytes = base64.b64decode(audio_base64)

                    st.success("Podcast Generated!")

                    st.audio(audio_bytes, format="audio/mp3")

                    st.download_button(
                        label="⬇️ Download Podcast",
                        data=audio_bytes,
                        file_name="podcast.mp3",
                        mime="audio/mp3"
                    )
                else:
                    st.write(data)
