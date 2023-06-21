from pathlib import Path
from PIL import Image

GLOBAL_STREAMLIT_STYLE = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """

DATA_PATH = Path("..", "data", "in")

FAVICON = Image.open(Path("..", "images", "favicon.ico"))
