from pathlib import Path
from PIL import Image

GLOBAL_STREAMLIT_STYLE = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .css-15zrgzn {display: none}
            </style>
            """

DATA_PATH = Path("..", "data", "in")

FAVICON = Image.open(Path("..", "images", "favicon.ico"))

CACHE_EXPIRE_SECONDS = 600
