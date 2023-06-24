from pathlib import Path, PurePath
from PIL import Image
import os

script_running_path = str(Path(__file__).parent.resolve())
split_script_running_path = path_split = PurePath(script_running_path).parts
assets_path = str(
    os.path.join(*split_script_running_path[0 : len(split_script_running_path) - 1])
)

# Data/images

DATA_PATH = Path(assets_path, "data", "in")
FAVICON = Image.open(Path(assets_path, "images", "favicon.ico"))

# Streamlit/Plotly vars

GLOBAL_STREAMLIT_STYLE = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .css-15zrgzn {display: none}
            </style>
            """

PLT_CONFIG = {
    "displaylogo": False,
    "modeBarButtonsToAdd": [
        "drawline",
        "drawopenpath",
        "drawcircle",
        "drawrect",
        "eraseshape",
    ],
    "scrollZoom": False,
}

PLT_CONFIG_NO_LOGO = {"displaylogo": False}

CACHE_EXPIRE_SECONDS = 600
