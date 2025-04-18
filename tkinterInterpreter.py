import pygame
import threading
import tkinter as tk
from tkinter import scrolledtext
import time

# ---------------- Pygame Visuals ----------------
WIDTH, HEIGHT = 800, 600
character = pygame.Rect(100, 500, 50, 50)
color = (100, 200, 255)
message_log = []
commands = []

def redraw(win):
    win.fill((30, 30, 30))
    pygame.draw.rect(win, color, character)
    pygame.display.update()

def pygame_loop():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Python Playground")

    clock = pygame.time.Clock()
    running = True

    while running:
        redraw(win)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Process commands
        if commands:
            cmd = commands.pop(0)
            try:
                cmd()
            except:
                pass

        clock.tick(30)  # Limit FPS

    pygame.quit()

# ---------------- Commands ----------------
def move_right():
    character.x += 50

def move_left():
    character.x -= 50

def jump():
    original_y = character.y
    character.y -= 80
    time.sleep(0.3)
    character.y = original_y

def say(msg):
    message_log.append(str(msg))
    if len(message_log) > 5:
        message_log.pop(0)
    update_log()

# ---------------- Safe Execution ----------------
def run_user_code():
    user_code = input_box.get("1.0", tk.END)
    try:
        exec(user_code, {
            'move_right': lambda: commands.append(move_right),
            'move_left': lambda: commands.append(move_left),
            'jump': lambda: commands.append(jump),
            'say': lambda msg: commands.append(lambda: say(msg))
        })
    except Exception as e:
        say("Error: " + str(e))

# ---------------- Tkinter UI ----------------
root = tk.Tk()
root.title("Kid's Python Interpreter")
root.geometry("500x400")

tk.Label(root, text="Type your Python commands below:").pack()

input_box = scrolledtext.ScrolledText(root, height=6, font=("Courier", 12))
input_box.pack(padx=10, pady=10)

run_button = tk.Button(root, text="Run Code", command=run_user_code)
run_button.pack(pady=5)

log_output = scrolledtext.ScrolledText(root, height=6, font=("Courier", 12), state='disabled')
log_output.pack(padx=10, pady=10)

def update_log():
    log_output.config(state='normal')
    log_output.delete("1.0", tk.END)
    for msg in message_log:
        log_output.insert(tk.END, msg + "\n")
    log_output.config(state='disabled')

# ---------------- Start Threads ----------------
pygame_thread = threading.Thread(target=pygame_loop, daemon=True)
pygame_thread.start()

# ---------------- Main Loop ----------------
root.mainloop()
