import streamlit as st
import openai
from PIL import Image
import requests
from io import BytesIO

# Replace with your OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]


def generate_joke(topic, characters):
    # A faked few-shot conversation to prime the model into becoming a sarcastic comedian selected earlier
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
                "content": f"You are a extremely funny and extremely sarcastic comedian writer tasked with preserving {', '.join(characters)} jokes and delivering the same style punchlines in your short skits. You will respond in a script that includes {', '.join(characters)}"},
            {"role": "user", "content": f"the topic is: {topic}. only respond as previous instructions and reply only with character names that I gave you followed by their script(make the responses deeply affected by the character's portrayed personality on their respective shows). Do not add any extra characters."},
        ],
        temperature=0.66666666666666666666666420,
    )

    # Get the generated text from the response
    generated_text = response['choices'][0]['message']['content']
    return generated_text


def create_video_html(video_path, width=None, height=None):
    width_attribute = f'width="{width}"' if width else ""
    height_attribute = f'height="{height}"' if height else ""
    return f"""
    <style>
        .video-container {{
            margin: 16px;
        }}
    </style>
    <div class="video-container">
        <video {width_attribute} {height_attribute} autoplay loop muted playsinline>
            <source src="{video_path}" type="video/webm">
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


st.title("Seinfeld gpt-3.5 Joke Generator")

topic = st.text_input("Enter a topic:")

characters = {
    "jerry": {
        "name": "Jerry",
        "video_path": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/jerry.webm",
        "selected": False,
    },
    "kramer": {
        "name": "Kramer",
        "video_path": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/kramer.webm",
        "selected": False,
    },
    "george": {
        "name": "George",
        "video_path": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/george.webm",
        "selected": False,
    },
    "larry_david": {
        "name": "Larry David",
        "video_path": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/larry.webm",
        "selected": False,
    },
    "elaine": {
        "name": "Elaine",
        "video_path": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/elaine.webm",
        "selected": False,
    },
    "newman": {
        "name": "Newman",
        "video_path": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/newman.webm",
        "selected": False,
    },
    "leon": {
        "name": "Leon",
        # Replace with the actual URL for
        "video_path": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/leon.webm",
        "selected": False,
    },
    "jeff": {
        "name": "Jeff",
        "video_path": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/jeff.webm",
        "selected": False,
    },
}

intro_audio = open('intro.mp3', 'rb').read()
outro_audio = open('outro.mp3', 'rb').read()

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
            video_html = create_video_html(char_info["video_path"], height=video_height)
            st.markdown(video_html, unsafe_allow_html=True)
            char_info["selected"] = st.checkbox(char_info["name"])


selected_characters = [char_info["name"]
                       for char_info in characters.values() if char_info["selected"]]
if st.button("Generate script"):
    if topic and len(selected_characters) > 1:
        # Play the intro audio while the user waits
        st.audio(intro_audio, format="audio/mp3")
        generated_script = generate_joke(topic, selected_characters)
        st.write(generated_script)
        # Create a container for the laugh videos
        laugh_videos_container = st.container()

        # Create columns for each laugh video
        num_laugh_videos = 3
        laugh_videos_cols = laugh_videos_container.columns(num_laugh_videos)

        # Create a dictionary of character name to laugh video path
        laugh_videos = {
            "kramer": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/kramerlaugh.webm",
            "george": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/georgelaugh.webm",
            "larry_david": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/larrylaugh.webm",
        }
        # Display the laugh videos
        laugh_video_height = 166.666  # Set the desired height in pixels for laugh videos

    for idx, (char_key, laugh_video_path) in enumerate(laugh_videos.items()):
        with laugh_videos_cols[idx]:
            laugh_video_html = create_video_html(laugh_video_path, height=laugh_video_height, width=220)
            st.markdown(laugh_video_html, unsafe_allow_html=True)

    st.markdown(
        "Follow me on my Twitter: [@didntdrinkwater](https://twitter.com/didntdrinkwater) and GitHub: [@younesbram](https://www.github.com/younesbram)")
    # Play the outro audio
    st.audio(outro_audio, format="audio/mp3")

else:
    st.write("Please provide a topic and select at least two characters.")
