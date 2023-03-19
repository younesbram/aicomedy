import streamlit as st
import openai
from PIL import Image
import requests
from io import BytesIO

# Replace with your OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(
    page_title="AI Comedy",
    page_icon="😂",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://www.github.com/younesbram/aicomedy",
        "Report a bug": "https://www.younes.ca/contact",
        "About": "# AI Comedy\nAn app that uses NLP to generate hilarious skits!",
    },
)

def generate_joke(topic, characters):
    # A faked few-shot conversation to prime the model into becoming a sarcastic comedian selected earlier
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
                "content": f"You are a extremely funny and extremely sarcastic comedian writer tasked with preserving {', '.join(characters)} jokes and delivering the same style punchlines in your short skits. You will respond in a script that includes {', '.join(characters)}"},
            {"role": "user",
                "content": f"the topic is: {topic}. only respond as previous instructions and reply only with character names that I gave you followed by their script(make the responses deeply affected by the character's portrayed personality on their respective shows). Do not add any extra characters."},
        ],
        temperature=0.66666666666666666666666420,
    )

    # Get the generated text from the response
    generated_text = response['choices'][0]['message']['content']
    return generated_text


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
                width: 50%; /* Change this value to the desired width for smaller screens */
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


st.title("Seinfeld gpt-3.5 Joke Generator")

topic = st.text_input("Enter a topic:")

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

    if topic and len(selected_characters) > 1:

        # Determine which show's intro and outro to play based on the counts of selected characters
        if num_seinfeld_chars > num_curb_chars:
            intro_audio = open('sounds/introseinfeld.mp3', 'rb').read()
            outro_audio = open('sounds/outroseinfeld.mp3', 'rb').read()
        else:
            intro_audio = open('sounds/introcurb.mp3', 'rb').read()
            outro_audio = open('sounds/outrocurb.mp3', 'rb').read()

        # Play the intro audio while the user waits
        st.audio(intro_audio, format="audio/mp3")
        generated_script = generate_joke(topic, selected_characters)
        st.write(generated_script)

        # Display the laugh videos
        # Set the desired height in pixels for laugh videos
        laugh_video_height = 166.666666666666666666666666666666666666666666666666420666666666666666666666666666666666
        # Create a container for the laugh videos
        laugh_videos_container = st.container()

        # Create columns for each laugh video
        num_laugh_videos = 3  # TODO : Make the unchecked characters the ones laughing
        laugh_videos_cols = laugh_videos_container.columns(num_laugh_videos)

        # Initialize column index
        col_index = 0

        laugh_video_characters = ["kramer", "george", "larry_david"]
        for char_key in laugh_video_characters:
            char_info = characters[char_key]
            if "laugh_video_webm" in char_info and "laugh_video_mp4" in char_info:
                laugh_video_webm = char_info["laugh_video_webm"]
                laugh_video_mp4 = char_info["laugh_video_mp4"]

            # Add laugh video to the corresponding column
            with laugh_videos_cols[col_index]:
                laugh_video_html = create_video_html(
                    laugh_video_webm, laugh_video_mp4, width=220, height=laugh_video_height)
                st.markdown(laugh_video_html, unsafe_allow_html=True)

            # Increment the column index
            col_index += 1

        st.markdown(
            "Follow me on my Twitter: [@didntdrinkwater](https://twitter.com/didntdrinkwater) and GitHub: [@younesbram](https://www.github.com/younesbram)")
        # Play the outro audio
        st.audio(outro_audio, format="audio/mp3")

else:
    st.write("Please provide a topic and select at least two characters.")
