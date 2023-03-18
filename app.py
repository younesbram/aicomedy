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
            {"role": "system", "content": f"You are a extremely funny and extremely sarcastic comedian writer tasked with preserving {', '.join(characters)} jokes and delivering the same style punchlines in your short skits. You will respond in a script that includes {', '.join(characters)}"},
            {"role": "user", "content": f"the topic is: {topic}. only respond as previous instructions and reply only with character names that I gave you followed by their script. Do not add any extra characters."},
        ],
        temperature=0.66666666666666666666666,
    )

    # Get the generated text from the response
    generated_text = response['choices'][0]['message']['content']
    return generated_text

def create_video_html(video_path):
    return f"""
    <style>
        .video-container {{
            margin: 8px;
        }}
    </style>
    <div class="video-container">
        <video width="179.26666420" autoplay loop muted playsinline>
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
        "laugh_path": "",
        "key": "jerry-checkbox"
    },
    "kramer": {
        "name": "Kramer",
        "video_path": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/kramer.webm",
        "selected": False,
        "laugh_path": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/kramerlaugh.webm",
        "key": "kramer-checkbox"
    },
    "george": {
        "name": "George",
        "video_path": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/george.webm",
        "selected": False,
        "laugh_path": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/georgelaugh.webm",
        "key": "george-checkbox"
    },
    "larry_david": {
        "name": "Larry David",
        "video_path": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/larry.webm",
        "selected": False,
        "laugh_path": "https://raw.githubusercontent.com/younesbram/aicomedy/master/loadables/larrylaugh.webm",
        "key": "larry-checkbox"
    },
}

# Create a container for the character selection
character_selection_container = st.container()

# Create columns for each character
num_characters = len(characters)
cols = character_selection_container.columns(num_characters)

for idx, (char_key, char_info) in enumerate(characters.items()):
    with cols[idx]:
        video_html = create_video_html(char_info["video_path"])
        st.markdown(video_html, unsafe_allow_html=True)
        char_info["selected"] = st.checkbox(char_info["name"])

selected_characters = [char_info["name"] for char_info in characters.values() if char_info["selected"]]



if st.button("Generate script"):
    if topic and len(selected_characters) > 1:
        generated_script = generate_joke(topic, selected_characters)
        st.write(generated_script)
        
        # Show dropdown with generated jokes
        joke_options = generated_script.split("\n\n")
        selected_joke = st.selectbox("Select a joke to generate a video clip:", joke_options)
        
        # Generate video clip for selected joke
        for char_key, char_info in characters.items():
            if char_info["name"] in selected_joke:
                video_html = create_video_html(char_info["video_path"])
                st.markdown(video_html, unsafe_allow_html=True)
                if char_info["laugh_path"]:
                    laugh_html = create_video_html(char_info["laugh_path"])
                    st.markdown(laugh_html, unsafe_allow_html=True)
        
        # Add social media links
        st.markdown("Follow me on my Twitter: [@didntdrinkwater](https://twitter.com/didntdrinkwater) and GitHub: [@younesbram](https://www.github.com/younesbram)")
    else:
        st.write("Please provide a topic and select at least two characters.")