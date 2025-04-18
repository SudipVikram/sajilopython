import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import pygame
import os
import sys

# Initialize Pygame
pygame.init()

# Global variables
CHAR_IMG_PATH = "character.png"
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
char_rect = pygame.Rect(100, 500, 80, 80)
commands = []

# Create the main Tkinter window
root = tk.Tk()
root.title("Pygame in Tkinter - Teaching Tool")
root.geometry("1000x600")

# ---- Pygame Frame Embedding ----
embed_frame = tk.Frame(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
embed_frame.pack(side=tk.LEFT)

# Right side for input + logs
control_frame = tk.Frame(root)
control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Input box
tk.Label(control_frame, text="Type your code:").pack()
input_box = scrolledtext.ScrolledText(control_frame, height=10)
input_box.pack(fill=tk.X, padx=10, pady=5)

# Log box
tk.Label(control_frame, text="Status:").pack()
log_box = scrolledtext.ScrolledText(control_frame, height=10, state='disabled')
log_box.pack(fill=tk.X, padx=10, pady=5)

# Show logs
def log(msg):
    log_box.config(state='normal')
    log_box.insert(tk.END, msg + "\n")
    log_box.config(state='disabled')
    log_box.see(tk.END)

# ---- Pygame Setup ----
def init_pygame():
    os.environ['SDL_WINDOWID'] = str(embed_frame.winfo_id())
    if sys.platform == "win32":
        os.environ['SDL_VIDEODRIVER'] = 'windib'
    pygame.display.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.update()
    return screen

# ---- Commands ----
def move_right():
    char_rect.x += 50
def move_left():
    char_rect.x -= 50
def jump():
    y = char_rect.y
    char_rect.y -= 100
    time.sleep(0.2)
    char_rect.y = y
def say(msg):
    log(str(msg))

# ---- Run User Code ----
def run_code():
    code = input_box.get("1.0", tk.END)
    try:
        exec(code, {
            'move_right': lambda: commands.append(move_right),
            'move_left': lambda: commands.append(move_left),
            'jump': lambda: commands.append(jump),
            'say': lambda msg: commands.append(lambda: say(msg))
        })
    except Exception as e:
        log("Error: " + str(e))

# Button to run code
tk.Button(control_frame, text="Run", command=run_code).pack(pady=10)

# ---- Game Loop ----
def game_loop():
    screen = init_pygame()
    clock = pygame.time.Clock()

    # Load character image
    if os.path.exists(CHAR_IMG_PATH):
        char_img = pygame.image.load(CHAR_IMG_PATH).convert_alpha()
        char_img = pygame.transform.scale(char_img, (80, 80))
    else:
        char_img = None
        log("character.png not found. Using rectangle.")

    running = True
    while running:
        screen.fill((255, 255, 255))

        if char_img:
            screen.blit(char_img, char_rect)
        else:
            pygame.draw.rect(screen, (255, 100, 100), char_rect)

        pygame.display.update()

        if commands:
            try:
                cmd = commands.pop(0)
                cmd()
            except Exception as e:
                log("Command Error: " + str(e))

        clock.tick(30)

# ---- Start game loop in thread ----
def start_game():
    time.sleep(1)  # Let Tkinter load first
    game_loop()

game_thread = threading.Thread(target=start_game, daemon=True)
game_thread.start()

root.mainloop()