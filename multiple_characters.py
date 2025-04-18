import tkinter as tk
from tkinter import ttk
import pygame
import threading
import os

# Initialize Pygame in a separate thread
def start_pygame():
    pygame.init()
    screen = pygame.display.set_mode((500, 400))
    pygame.display.set_caption("Sajilo Playground")

    # Load assets
    character_image = pygame.image.load("alien.png")
    move_sound = pygame.mixer.Sound("move.mp3")
    background_music = "background_sound.mp3"

    # Start background music
    pygame.mixer.music.load(background_music)
    pygame.mixer.music.play(-1)

    x, y = 100, 100
    speed = 5

    running = True
    while running:
        screen.fill((255, 255, 255))  # White background
        screen.blit(character_image, (x, y))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            x += speed
            move_sound.play()
        elif keys[pygame.K_LEFT]:
            x -= speed
            move_sound.play()
        elif keys[pygame.K_UP]:
            y -= speed
            move_sound.play()
        elif keys[pygame.K_DOWN]:
            y += speed
            move_sound.play()

    pygame.quit()

# GUI Thread
def start_tk():
    root = tk.Tk()
    root.title("SajiloPython - Control Panel")
    root.geometry("300x200")

    label = ttk.Label(root, text="Use arrow keys to move your character!")
    label.pack(pady=20)

    start_button = ttk.Button(root, text="Start Game", command=lambda: threading.Thread(target=start_pygame).start())
    start_button.pack()

    root.mainloop()

# Run GUI
start_tk()
