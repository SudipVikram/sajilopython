# run.py

from .shared import _game
import pygame

class Runner:
    def start(self):
        """Manages the event loop externally (since sajilopygame can't hold it)."""
        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            _game.refresh_window()  # Keep refreshing continuously
            clock.tick(60)          # FPS control (you can also use _game's FPS here)

        pygame.quit()
