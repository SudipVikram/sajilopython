# Background module for sajilopython package
from sajilopygame import sajilopygame
import os

# Initialize the game instance (shared for the entire library)
_game = sajilopygame()
_game.window_title("SajiloPython")

class Background:
    def __init__(self):
        # Predefined backgrounds with their image paths
        self.backgrounds = {
            "dawn": "assets/backgrounds/dawn.png",
            "dusk": "assets/backgrounds/dusk.png",
            "sunshine": "assets/backgrounds/sunshine.png"
        }

    def load(self, name):
        """
        Load one of the preset backgrounds.
        
        Args:
            name (str): Name of the background ("dawn", "dusk", "sunshine").
        """
        if name in self.backgrounds:
            _game.background_image(self.backgrounds[name])
        else:
            print(f"❌ Background '{name}' not found! Available options: {list(self.backgrounds.keys())}")

# Create an instance to be imported directly
background = Background()
