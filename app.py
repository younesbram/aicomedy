import streamlit as st
import openai
from PIL import Image
import requests
from io import BytesIO

# Replace with your OpenAI API key
openai.api_key = "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"

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
    <video width="200" autoplay loop muted playsinline>
        <source src="{video_path}" type="video/webm">
    </video>
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
        "video_path": r"C:\Users\hoo-h\OneDrive\Desktop\compsci\jokegenerator\loadables\jerry.webm",
        "selected": False,
    },
    "kramer": {
        "name": "Kramer",
        "video_path": r"C:\Users\hoo-h\OneDrive\Desktop\compsci\jokegenerator\loadables\kramer.webm",
        "selected": False,
    },
    "george": {
        "name": "George",
        "video_path": r"C:\Users\hoo-h\OneDrive\Desktop\compsci\jokegenerator\loadables\george.webm",
        "selected": False,
    },
    "larry_david": {
        "name": "Larry David",
        "video_path": r"C:\Users\hoo-h\OneDrive\Desktop\compsci\jokegenerator\loadables\larry.webm",
        "selected": False,
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
        st.video(webm_url)  # Add this line to display the WebM video
        st
    else:
        st.write("Please provide a topic and select at least two characters.")
