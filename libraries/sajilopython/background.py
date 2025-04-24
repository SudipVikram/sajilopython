# sajilopython/background.py

import os
from .shared import _game, game_content_used

# ✅ Enable content flag to trigger the auto loop
game_content_used = True

# ✅ Calculate base path for the assets folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def asset_path(*parts):
    return os.path.join(BASE_DIR, "assets", *parts)

class Background:
    def __init__(self):
        global game_content_used
        game_content_used = True
        # Define available backgrounds with proper paths
        self.backgrounds = {
            "dawn": asset_path("backgrounds", "dawn.png"),
            "dusk": asset_path("backgrounds", "dusk.png"),
            "sunshine": asset_path("backgrounds", "sunshine.png")
        }

    def load(self, name):
        global game_content_used
        game_content_used = True
        if name in self.backgrounds:
            _game.background_image(self.backgrounds[name])
        else:
            print(f"[ERROR] Background '{name}' not found. Available options: {list(self.backgrounds.keys())}")

# ✅ Create the instance that will be imported as 'background'
background = Background()