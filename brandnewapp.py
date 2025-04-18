import tkinter as tk
from tkinter import scrolledtext
import pygame
import threading
import time

# Initialize Pygame first
pygame.init()

# Constants for game
WIDTH, HEIGHT = 400, 300
CHAR_WIDTH, CHAR_HEIGHT = 40, 60
BG_COLOR = (135, 206, 250)  # Sky blue

# Global for character
char_x = 50
char_y = HEIGHT - CHAR_HEIGHT
velocity = 5

# Main Game Thread
def run_pygame():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Playground")

    global char_x, char_y
    clock = pygame.time.Clock()
    is_running = True
    jump = False
    jump_count = 10
    font = pygame.font.SysFont('Comic Sans MS', 20)

    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
                pygame.quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            char_x -= velocity
        if keys[pygame.K_RIGHT]:
            char_x += velocity
        if not jump:
            if keys[pygame.K_SPACE]:
                jump = True
        else:
            if jump_count >= -10:
                neg = 1
                if jump_count < 0:
                    neg = -1
                char_y -= (jump_count ** 2) * 0.5 * neg
                jump_count -= 1
            else:
                jump = False
                jump_count = 10

        # Draw
        screen.fill(BG_COLOR)
        pygame.draw.rect(screen, (255, 0, 0), (char_x, char_y, CHAR_WIDTH, CHAR_HEIGHT))

        # Optional: text bubble
        bubble_text = font.render("Hello!", True, (0, 0, 0))
        screen.blit(bubble_text, (char_x, char_y - 25))

        pygame.display.update()
        clock.tick(30)

# Tkinter UI
def start_gui():
    root = tk.Tk()
    root.title("KiddoCode Playground")

    # Editor area
    editor = scrolledtext.ScrolledText(root, height=15)
    editor.pack(fill='both', expand=True)

    # Output shell
    output = tk.Text(root, height=5, bg="#f0f0f0", fg="black", state="disabled")
    output.pack(fill='both', expand=False)

    # Start Pygame thread
    threading.Thread(target=run_pygame, daemon=True).start()

    root.mainloop()

start_gui()
