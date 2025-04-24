# sajilopython/shared.py

import sys
import os

# Add the parent 'libraries' folder to sys.path to locate sajilopygame.py
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# ✅ Import the sajilopygame class
from sajilopygame import sajilopygame

# ✅ Create the shared _game instance
_game = sajilopygame()
_game.set_fps(60)  # You can change the default FPS here if needed

# ✅ Global flag to check if any game content was used
game_content_used = False  # This will be set True from background.py, characters.py, draw.py

# ✅ Expose both _game and game_content_used for other modules
__all__ = ["_game", "game_content_used"]