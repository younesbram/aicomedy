import os
from dotenv import load_dotenv
import streamlit as st
import openai
from PIL import Image
import requests
from io import BytesIO
import base64
from groq import Groq
# Load environment variables from .env file
load_dotenv()
# Retrieve API keys from environment variables and secrets
openai_api_key = st.secrets["OPENAI_API_KEY"]
elevenlabs_api_key = st.secrets["EV_API_KEY"]
groq_api_key = st.secrets["GROQ_API_KEY"]
jerry_voice = st.secrets["JERRY_VOICE"]
kramer_voice = st.secrets["KRAMER_VOICE"]
george_voice = st.secrets["GEORGE_VOICE"]
larry_david_voice = st.secrets["LARRY_DAVID_VOICE"]
elaine_voice = st.secrets["ELAINE_VOICE"]
newman_voice = st.secrets["NEWMAN_VOICE"]
leon_voice = st.secrets["LEON_VOICE"]
jeff_voice = st.secrets["JEFF_VOICE"]
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable not set")
st.set_page_config(
    page_title="AI Skit Generator",
    page_icon="😂",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://www.github.com/younesbram/aicomedy",
        "Report a bug": "https://www.younes.ca/contact",
        "About": "# AI Skit Generator\nAn app that uses AI to generate hilarious skits!",
    },
)
client = Groq(api_key=groq_api_key)
# Initialize session state variables
if 'script' not in st.session_state:
    st.session_state['script'] = None
if 'intro_audio' not in st.session_state:
    st.session_state['intro_audio'] = None
if 'outro_audio' not in st.session_state:
    st.session_state['outro_audio'] = None
def generate_joke_with_groq(topic, characters):
    messages = [
        {"role": "system",
            "content": f"You never give emotions in the script or pauses or descriptors or laughs. NO (pauses) NO (smirks) NO (laughs) NO ANY OF THAT ONLY THE TEXT!!!! You are an extremely funny and sarcastic comedian writer that knows Larry David and Jerry Seinfeld's writing styles, tasked with preserving {', '.join(characters)} jokes and delivering the same style punchlines in your short skits. You will respond in a script that includes {', '.join(characters)}."},
        {"role": "user",
            "content": f"The topic is: {topic}. Please obey newlines and DONT give ANY descriptors only Character: speech for the ENTIRE script only with the characters selected. Nothing else or else the system bugs. Only respond as previous instructions and be extremely funny, like genius comedy. Do not add any extra characters. Do not add any descriptors like (pauses) or (excitedly) NO MATTER WHAT!  because I will be programmatically generating voice clips from the script. So anything like (sarcastically) or ANYTHING like that will destroy our whole moat and program. Take this seriously. INCLUDE EVERY CHARACTER SELECTED . {', '.join(characters)}"},
            "content": f"The topic is: {topic}. Please obey newlines and DONT give ANY descriptors only Character: speech for the ENTIRE script only with the characters. Nothing else or else the system bugs. Only respond as previous instructions and be extremely funny, like genius comedy. Do not add any extra characters. Do not add any descriptors like (pauses) or (excitedly) NO MATTER WHAT!  because I will be programmatically generating voice clips from the script. So anything like (sarcastically) or ANYTHING like that will destroy our whole moat and program. Take this seriously. INCLUDE EVERY CHARACTER SELECTED . {', '.join(characters)}"},
    ]

    stream = client.chat.completions.create(
@@ -175,8 +175,8 @@ def generate_voice(character_name, text):
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.7
            "stability": 0.5,
            "similarity_boost": 0.6
        }
    }
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        st.error(f"Failed to generate audio for {character_name}: {response.text}")
        return None
def stitch_audio_segments(audio_segments):
    combined_audio = b""
    for segment in audio_segments:
        combined_audio += segment
    with open("combined_audio.mp3", "wb") as f:
        f.write(combined_audio)
    return "combined_audio.mp3"
def generate_audio_script(script):
    lines = script.split("\n")
    audio_segments = []
    st.info("API costs aren't free, you know! Consider following my [@didntdrinkwater](https://twitter.com/didntdrinkwater) and GitHub: [@younesbram](https://www.github.com/younesbram) as a form of compensation. 😂")
    progress_bar = st.progress(0)
    for i, line in enumerate(lines):
        st.write(f"Processing line: {line}")
        if ":" in line:
            character, text = line.split(":", 1)
            st.write(f"Generating voice for {character.strip()} with text: {text.strip()}")
            audio_segment = generate_voice(character.strip(), text.strip())
            if audio_segment:
                audio_segments.append(audio_segment)
            else:
                st.write(f"Failed to generate audio segment for {character.strip()}")
        progress_bar.progress((i + 1) / len(lines))
    if audio_segments:
        audio_file_path = stitch_audio_segments(audio_segments)
        return audio_file_path
    return None
st.title("AI Skit Generator")
# Topic input and optional image upload
topic = st.text_input("Enter a topic:")
uploaded_image = st.file_uploader("Upload an image (optional - you can do only image or image + topic)", type=["jpg", "jpeg", "png"])
# Character selection
seinfeld_characters = ["jerry", "kramer", "george", "elaine", "newman"]
curb_characters = ["larry_david", "leon", "jeff"]
characters = {
    "jerry": {
        "name": "Jerry",
        "videopath_webm": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/jerry.webm",
        "videopath_mp4": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/jerry.mp4",
        "selected": False,
    },
    "kramer": {
        "name": "Kramer",
        "videopath_webm": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/kramer.webm",
        "videopath_mp4": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/kramer.mp4",
        "laugh_video_webm": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/kramerlaugh.webm",
        "laugh_video_mp4": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/kramerlaugh.mp4",
        "selected": False,
    },
    "george": {
        "name": "George",
        "videopath_webm": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/george.webm",
        "videopath_mp4": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/george.mp4",
        "laugh_video_mp4": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/georgelaugh.mp4",
        "laugh_video_webm": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/georgelaugh.webm",
        "selected": False,
    },
    "larry_david": {
        "name": "Larry David",
        "videopath_webm": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/larry.webm",
        "videopath_mp4": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/larry.mp4",
        "laugh_video_mp4": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/larrylaugh.mp4",
        "laugh_video_webm": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/larrylaugh.webm",
        "selected": False,
    },
    "elaine": {
        "name": "Elaine",
        "videopath_webm": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/elaine.webm",
        "videopath_mp4": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/elaine.mp4",
        "selected": False,
    },
    "newman": {
        "name": "Newman",
        "videopath_webm": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/newman.webm",
        "videopath_mp4": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/newman.mp4",
        "selected": False,
    },
    "leon": {
        "name": "Leon",
        "videopath_webm": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/leon.webm",
        "videopath_mp4": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/leon.mp4",
        "selected": False,
    },
    "jeff": {
        "name": "Jeff",
        "videopath_webm": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/jeff.webm",
        "videopath_mp4": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/jeff.mp4",
        "selected": False,
    },
}
# Create a container for the character selection
character_selection_container = st.container()
# Define the number of characters per row
characters_per_row = 4
# Calculate the number of rows required
num_rows = (len(characters) + characters_per_row - 1) // characters_per_row
# Iterate through the rows and columns to display the characters
for row in range(num_rows):
    row_container = character_selection_container.container()
    cols = row_container.columns(characters_per_row)
    for col in range(characters_per_row):
        idx = row * characters_per_row + col
        # If there are no more characters to display, break the loop
        if idx >= len(characters):
            break
        char_key, char_info = list(characters.items())[idx]
        video_height = 120  # Set the desired height in pixels
        with cols[col]:
            video_html = create_video_html(
                char_info["videopath_webm"], char_info["videopath_mp4"], height=video_height)
            st.markdown(video_html, unsafe_allow_html=True)
            char_info["selected"] = st.checkbox(char_info["name"])
selected_characters = [char_info["name"]
                       for char_info in characters.values() if char_info["selected"]]
if st.button("Generate script"):
    num_seinfeld_chars = sum(char_key in seinfeld_characters for char_key,
                             char_info in characters.items() if char_info["selected"])
    num_curb_chars = sum(char_key in curb_characters for char_key,
                         char_info in characters.items() if char_info["selected"])
    if (topic or uploaded_image) and len(selected_characters) > 1:
        # Determine which show's intro and outro to play based on the counts of selected characters
        if num_seinfeld_chars > num_curb_chars:
            intro_audio = open('sounds/introseinfeld.mp3', 'rb').read()
            outro_audio = open('sounds/outroseinfeld.mp3', 'rb').read()
        else:
            intro_audio = open('sounds/introcurb.mp3', 'rb').read()
            outro_audio = open('sounds/outrocurb.mp3', 'rb').read()
        # Store intro and outro audio in session state
        st.session_state['intro_audio'] = intro_audio
        st.session_state['outro_audio'] = outro_audio
        # Play the intro audio while the user waits
        st.audio(intro_audio, format="audio/mp3")
        # Add a spinner with a message while generating the script
        with st.spinner("Generating script... This might take a few moments... might as well follow my twitter and github.."):
            image_data = None
            use_gpt4 = False
            if uploaded_image:
                image_data = uploaded_image.read()
                use_gpt4 = True
            generated_script = generate_joke(topic, selected_characters, use_gpt4, image_data)
        
        st.session_state['script'] = generated_script
        st.write(generated_script)
# Add button to generate audio if script is generated
if st.session_state.get('script'):
    if st.button("Generate Audio"):
        with st.spinner("Generating audio..."):
            audio_file_path = generate_audio_script(st.session_state['script'])
            if audio_file_path:
                st.audio(audio_file_path, format="audio/mp3")
            else:
                st.error("Failed to generate audio.")
        
        st.info("Follow me on my Twitter: [@didntdrinkwater](https://twitter.com/didntdrinkwater) and GitHub: [@younesbram](https://www.github.com/younesbram)")
        # Display the laugh videos after generating the audio
        laugh_videos_container = st.container()
        laugh_video_height = 166.67
        num_laugh_videos = 3
        laugh_videos_cols = laugh_videos_container.columns(num_laugh_videos)
        col_index = 0
        laugh_video_characters = ["kramer", "george", "larry_david"]
        for char_key in laugh_video_characters:
            char_info = characters[char_key]
            if "laugh_video_webm" in char_info and "laugh_video_mp4" in char_info:
                laugh_video_webm = char_info["laugh_video_webm"]
                laugh_video_mp4 = char_info["laugh_video_mp4"]
                with laugh_videos_cols[col_index]:
                    laugh_video_html = create_video_html(
                        laugh_video_webm, laugh_video_mp4, width=220, height=laugh_video_height)
                    st.markdown(laugh_video_html, unsafe_allow_html=True)
                col_index += 1
st.markdown(
    "Follow me on my Twitter: [@didntdrinkwater](https://twitter.com/didntdrinkwater) and GitHub: [@younesbram](https://www.github.com/younesbram)")
if st.session_state.get('outro_audio'):
    st.audio(st.session_state['outro_audio'], format="audio/mp3")
else:
    st.write("Please provide a topic or upload an image and select at least two characters. Not all voices are supported. Currently supported voices are: Jerry, Kramer, George, Elaine.")
