import os
from dotenv import load_dotenv
import streamlit as st
import openai
from PIL import Image
import requests
from io import BytesIO
import base64
import ffmpeg
import tempfile
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
elaine_voice = st.secrets["ELAINE_VOICE"]

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
            "content": f"The topic is: {topic}. Please obey newlines and DONT give ANY descriptors only Character: speech for the ENTIRE script only with the characters. Nothing else or else the system bugs. Only respond as previous instructions and be extremely funny, like genius comedy. Do not add any extra characters. Do not add any descriptors like (pauses) or (excitedly) NO MATTER WHAT!  because I will be programmatically generating voice clips from the script. So anything like (sarcastically) or ANYTHING like that will destroy our whole moat and program. Take this seriously. INCLUDE EVERY CHARACTER SELECTED . {', '.join(characters)}"},
    ]

    stream = client.chat.completions.create(
        messages=messages,
        model="llama3-8b-8192",
        temperature=0.420,
        max_tokens=1024,
        top_p=1,
        stop=None,
        stream=True,
    )

    generated_text = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            generated_text += chunk.choices[0].delta.content
            st.session_state['script'] = generated_text
    return generated_text

def generate_joke(topic, characters, use_gpt4=False, image_data=None):
    if use_gpt4 and image_data:
        st.info("Generating script with GPT-4 Vision. This might take a few moments...  API costs aren't free, you know! Consider following my [@didntdrinkwater](https://twitter.com/didntdrinkwater) and GitHub: [@younesbram](https://www.github.com/younesbram) as a form of compensation. 😂  ")
        img_str = base64.b64encode(image_data).decode('utf-8')
        messages = [
            {"role": "system",
                "content": f"You are an extremely funny and sarcastic comedian writer that knows Larry David and Jerry Seinfeld's writing styles, tasked with preserving {', '.join(characters)} jokes and delivering the same style punchlines in your short skits. You will respond in a script that includes {', '.join(characters)}."},
            {"role": "user",
                "content": f"The topic is: {topic}. Only respond as previous instructions and be extremely funny, like genius comedy. Reply only with character names that I gave you followed by their script (make the responses deeply affected by the character's portrayed personality on their respective shows). Do not add any extra characters or descriptors or anything like sarcastically or laughs or whatever, ONLY the text to be voiced.."},
            {"role": "user",
                "content": [
                    {"type": "text", "text": "Please use the following image as context."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}
                ]}
        ]

        data = {
            "model": "gpt-4o",
            "messages": messages,
            "temperature": 0.66666666666666666666666420,
        }

        api_url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}"
        }
        response = requests.post(api_url, headers=headers, json=data)
        
        try:
            response_data = response.json()
            generated_text = response_data['choices'][0]['message']['content']
            st.session_state['script'] = generated_text
            st.write("Generated script with image context:")
            st.write(generated_text)
            return generated_text
        except KeyError as e:
            st.error(f"Failed to generate script: {response_data}")
            return ""
    else:
        return generate_joke_with_groq(topic, characters)

def create_video_html(video_path_webm, video_path_mp4, width=None, height=None):
    width_attribute = f'width="{width}"' if width else ""
    height_attribute = f'height="{height}"' if height else ""
    return f"""
    <style>
        .video-container {{
            margin: 16px;
            display: inline-block;
        }}
        .video-container video {{
            {width_attribute};
            {height_attribute};
        }}
        @media only screen and (max-width: 480px) {{
            .video-container video {{
                width: 50%;
                height: auto;
            }}
        }}
    </style>
    <div class="video-container">
        <video {width_attribute} {height_attribute} autoplay loop muted playsinline>
            <source src="{video_path_webm}" type="video/webm">
            <source src="{video_path_mp4}" type="video/mp4">
        </video>
    </div>
    """

def load_image(url=None, path=None):
    if url:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
    elif path:
        img = Image.open(path)
    return img

def generate_voice(character_name, text):
    voice_id = {
        "jerry": jerry_voice,
        "kramer": kramer_voice,
        "george": george_voice,
        "elaine": elaine_voice,
    }.get(character_name.lower())
    
    if not voice_id:
        return None
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": elevenlabs_api_key
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
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
    return combined_audio

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
        combined_audio = stitch_audio_segments(audio_segments)
        audio_file_path = "generated_audio.mp3"
        with open(audio_file_path, "wb") as f:
            f.write(combined_audio)
        return audio_file_path
    return None

def generate_video_with_audio(audio_path, images_paths, output_path, user_image_path=None):
    # Create a temp directory to store the intermediate files
    with tempfile.TemporaryDirectory() as tempdir:
        # Load the images and audio
        image_inputs = [ffmpeg.input(image) for image in images_paths]
        audio_input = ffmpeg.input(audio_path)
        
        if user_image_path:
            user_image_input = ffmpeg.input(user_image_path)
        
        # Create filter complex for video
        filters = []
        for i, image in enumerate(image_inputs):
            filters.append(f"[{i}:v]scale=320:240,setpts=PTS-STARTPTS[v{i}]")
        
        if user_image_path:
            filters.append("[4:v]scale=320:240,setpts=PTS-STARTPTS[user]")

        filter_complex = ";".join(filters)
        
        output_args = {
            'c:v': 'libx264',
            'c:a': 'aac',
            'pix_fmt': 'yuv420p',
            'shortest': None
        }
        
        # Build the command
        stream = ffmpeg.filter_multi_output(image_inputs, 'concat', n=len(images_paths), v=1, a=0).output(
            audio_input.audio, **output_args
        )

        if user_image_path:
            stream = ffmpeg.overlay(stream, user_image_input).output(output_path)

        # Run the ffmpeg command
        ffmpeg.run(stream)

def create_video_with_images_and_audio(script, audio_path, user_image=None):
    # Define the paths to the images
    image_paths = {
        "jerry": "path/to/jerry.png",
        "kramer": "path/to/kramer.png",
        "george": "path/to/george.png",
        "elaine": "path/to/elaine.png",
    }
    lines = script.split("\n")
    used_images = []
    for line in lines:
        if ":" in line:
            character = line.split(":")[0].strip().lower()
            used_images.append(image_paths.get(character))

    output_video_path = "generated_video.mp4"
    
    generate_video_with_audio(audio_path, used_images, output_video_path, user_image)
    
    return output_video_path

st.title("AI Skit Generator")

# Topic input and optional image upload
topic = st.text_input("Enter a topic:")
uploaded_image = st.file_uploader("Upload an image (optional - you can do only image or image + topic)", type=["jpg", "jpeg", "png"])

# Character selection
seinfeld_characters = ["jerry", "kramer", "george", "elaine"]
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
        "selected": False,
    },
    "george": {
        "name": "George",
        "videopath_webm": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/george.webm",
        "videopath_mp4": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/george.mp4",
        "selected": False,
    },
    "elaine": {
        "name": "Elaine",
        "videopath_webm": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/elaine.webm",
        "videopath_mp4": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/elaine.mp4",
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
    if (topic or uploaded_image) and len(selected_characters) > 1:
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
                st.download_button(label="Download Audio", data=open(audio_file_path, "rb").read(), file_name="generated_audio.mp3", mime="audio/mpeg")
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

        if st.button("Generate Video"):
            with st.spinner("Generating video..."):
                user_image_path = None
                if uploaded_image:
                    user_image_path = uploaded_image.name
                    with open(user_image_path, 'wb') as f:
                        f.write(uploaded_image.getvalue())

                video_path = create_video_with_images_and_audio(st.session_state['script'], audio_file_path, user_image=user_image_path)
                if video_path:
                    st.video(video_path)
                    st.download_button(label="Download Video", data=open(video_path, "rb").read(), file_name="generated_video.mp4", mime="video/mp4")
                    st.markdown(
                        f'<a href="https://twitter.com/intent/tweet?text=Check out this AI-generated skit!&url=https://younes.ca" target="_blank"><img src="https://upload.wikimedia.org/wikipedia/commons/4/4f/Twitter-logo.svg" alt="Share on Twitter" height="20" width="20" style="margin-right:10px;">Share on Twitter</a>',
                        unsafe_allow_html=True)
                else:
                    st.error("Failed to generate video.")
            
st.markdown(
    "Follow me on my Twitter: [@didntdrinkwater](https://twitter.com/didntdrinkwater) and GitHub: [@younesbram](https://www.github.com/younesbram)")
if st.session_state.get('outro_audio'):
    st.audio(st.session_state['outro_audio'], format="audio/mp3")
else:
    st.write("Please provide a topic or upload an image and select at least two characters. Not all voices are supported. Currently supported voices are: Jerry, Kramer, George, Elaine.")
