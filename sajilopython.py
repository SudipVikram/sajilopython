import tkinter as tk
from tkinter import scrolledtext
import pygame
import threading
import time
import re
import sys
import io

# initializing pygame
pygame.init()

# constants for the game
WIDTH, HEIGHT = 800, 500
BG_COLOR = (0,0,0)
BOB_COLOR = (255, 0, 0)  # Red color for Bob
BOB_WIDTH, BOB_HEIGHT = 50, 50
GRAVITY = 1

# Create Bob as a rectangle
bob = pygame.Rect(375, 400, BOB_WIDTH, BOB_HEIGHT)
bob_velocity_y = 0  # To simulate jumping (gravity)
is_jumping = False
speech_bubble = ""

# Function to move Bob left
def move_left():
    bob.x -= 5

# Function to move Bob right
def move_right():
    bob.x += 5

# Function to make Bob jump
def jump():
    global bob_velocity_y, is_jumping
    if not is_jumping:
        bob_velocity_y = -15  # Initial jump velocity
        is_jumping = True

# Function for Bob to say something
def say(text):
    global speech_bubble
    speech_bubble = text

# Function to handle the Run button click
def run_code(editor, shell):
    code = editor.get("1.0", "end-1c")  # Get the code from the editor
    output = capture_output(code)  # Capture the output of the code

    # Display output in the shell
    shell.config(state="normal")
    shell.delete(1.0, "end")
    shell.insert("insert", output)
    shell.config(state="disabled")

def highlight_syntax(event=None):
    # Clear all previous tags
    editor.tag_remove("keyword", "1.0", "end")
    editor.tag_remove("string", "1.0", "end")
    editor.tag_remove("comment", "1.0", "end")
    editor.tag_remove("number", "1.0", "end")

    # Get all text
    code = editor.get("1.0", "end-1c")

    # Regex patterns
    keywords = r"\b(def|class|import|from|return|if|else|elif|for|while|try|except|print|True|False|None)\b"
    strings = r"(['\"])(?:(?=(\\?))\2.)*?\1"
    comments = r"#.*"
    numbers = r"\b\d+\b"

    for match in re.finditer(keywords, code):
        start = f"1.0 + {match.start()}c"
        end = f"1.0 + {match.end()}c"
        editor.tag_add("keyword", start, end)

    for match in re.finditer(strings, code):
        start = f"1.0 + {match.start()}c"
        end = f"1.0 + {match.end()}c"
        editor.tag_add("string", start, end)

    for match in re.finditer(comments, code):
        start = f"1.0 + {match.start()}c"
        end = f"1.0 + {match.end()}c"
        editor.tag_add("comment", start, end)

    for match in re.finditer(numbers, code):
        start = f"1.0 + {match.start()}c"
        end = f"1.0 + {match.end()}c"
        editor.tag_add("number", start, end)


# the pygame execution code segment or playground
def playground():
    global bob_velocity_y, is_jumping, speech_bubble
    is_running = True

    screen = pygame.display.set_mode((WIDTH,HEIGHT))
    pygame.display.set_caption("Sajilo Python Playground")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Comic Sans MS",size=20)
    is_running = False

    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
                pygame.quit()

        # Update Bob's Y position to simulate gravity and jumping
        bob_velocity_y += GRAVITY
        bob.y += bob_velocity_y

        # Check for collision with the ground
        if bob.bottom > HEIGHT:
            bob.bottom = HEIGHT
            bob_velocity_y = 0
            is_jumping = False

        # background
        screen.fill(BG_COLOR)

        # Draw Bob (the character)
        pygame.draw.rect(screen, BOB_COLOR, bob)

        # Display speech bubble above Bob if there's text
        if speech_bubble:
            font = pygame.font.SysFont("Comic Sans MS", 20)
            text_surface = font.render(speech_bubble, True, (255, 255, 255))  # White text
            pygame.draw.rect(screen, (0, 0, 0), (
            bob.x + 10, bob.y - 30, text_surface.get_width() + 10, text_surface.get_height() + 10))  # Speech bubble
            screen.blit(text_surface, (bob.x + 15, bob.y - 25))  # Text inside the bubble

        # refreshing the output
        pygame.display.update()
        # setting fps
        clock.tick(30)

class LineNumberCanvas(tk.Canvas):
    def __init__(self, text_widget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_widget = text_widget
        self.font = ("Helvetica", 13)
        self.config(width=35, bg="#e0e0af")
        self.update_line_numbers()

    def update_line_numbers(self):
        self.delete("all")
        i = self.text_widget.index("@0,0")
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            line_num = str(i).split(".")[0]
            self.create_text(8, y+2, anchor="nw", text=line_num, font=self.font, fill="#333")
            i = self.text_widget.index(f"{i}+1line")
        self.after(50, self.update_line_numbers)


# Capture output for the shell display
def capture_output(code):
    # Create a StringIO object to capture the output
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        exec(code)  # Execute the code in the editor
    except Exception as e:
        # If there's an error, display it in the shell
        sys.stdout = old_stdout
        return str(e)

    output = sys.stdout.getvalue()
    sys.stdout = old_stdout  # Reset stdout
    return output

# tkinter GUI or workbench
def workbench():
    global editor
    root = tk.Tk()
    root.title("Sajilo Python Workbench")

    # frame to hold line numbers and editor
    editor_frame = tk.Frame(root)
    editor_frame.pack(fill="both", expand=True)

    # text editor
    editor = scrolledtext.ScrolledText(editor_frame, height=15, width=50, font=("Helvetica", 14))
    editor.configure(insertbackground="black", insertwidth=2, insertontime=300, insertofftime=300)
    editor.pack(side="right", fill="both", expand=True)

    # highlighting tag
    editor.tag_configure("current_line", background="#e8e815")

    # syntax highlighting # Define syntax tags
    editor.tag_configure("keyword", foreground="blue")
    editor.tag_configure("string", foreground="green")
    editor.tag_configure("comment", foreground="gray")
    editor.tag_configure("number", foreground="purple")

    # Function to update highlight
    def highlight_current_line(event=None):
        editor.tag_remove("current_line", "1.0", "end")
        editor.tag_add("current_line", "insert linestart", "insert lineend+1c")

    # Bind events
    editor.bind("<KeyRelease>", lambda event: (highlight_syntax(), highlight_current_line()))

    # Initial highlight
    highlight_current_line()

    # line numbers
    line_numbers = LineNumberCanvas(editor, editor_frame)
    line_numbers.pack(side="left", fill="y")

    # output shell
    shell = tk.Text(root, height=7, bg="#000000", fg="white", state="disabled", width=10)
    shell.pack(fill='both', expand=False)

    # Run button
    run_button = tk.Button(root, text="Run", command=lambda: run_code(editor, shell))
    run_button.pack()

    # start pygame thread
    threading.Thread(target=playground(), daemon=True).start()

    root.mainloop()

workbench()




