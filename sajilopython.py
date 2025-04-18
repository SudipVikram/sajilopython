import tkinter as tk
from tkinter import scrolledtext
import pygame
import threading
import time
import re
import sys
import io

# Initialize pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 800, 500
BG_COLOR = (0, 0, 0)
GRAVITY = 1

# Global flag for running state
running = True

# Bob Character Class
class BobCharacter:
    def __init__(self):
        self.rect = pygame.Rect(375, 400, 50, 50)
        self.color = (255, 0, 0)
        self.velocity_y = 0
        self.is_jumping = False
        self.speech = ""
        self.loaded = False

    def load(self):
        self.loaded = True

    def move_left(self):
        if self.loaded:
            self.rect.x -= 5

    def move_right(self):
        if self.loaded:
            self.rect.x += 5

    def jump(self):
        if self.loaded and not self.is_jumping:
            self.velocity_y = -15
            self.is_jumping = True

    def say(self, text):
        if self.loaded:
            self.speech = text

    def update(self):
        if not self.loaded:
            return
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.velocity_y = 0
            self.is_jumping = False

    def draw(self, screen):
        if not self.loaded:
            return
        pygame.draw.rect(screen, self.color, self.rect)
        if self.speech:
            font = pygame.font.SysFont("Comic Sans MS", 20)
            text_surface = font.render(self.speech, True, (255, 255, 255))
            pygame.draw.rect(screen, (0, 0, 0), (
                self.rect.x + 10, self.rect.y - 30,
                text_surface.get_width() + 10, text_surface.get_height() + 10))
            screen.blit(text_surface, (self.rect.x + 15, self.rect.y - 25))


# Global Bob instance
bob = BobCharacter()


def playground():
    global running
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sajilo Python Playground")
    clock = pygame.time.Clock()
    bob.load()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                return

        bob.update()
        screen.fill(BG_COLOR)
        bob.draw(screen)
        pygame.display.update()
        clock.tick(30)


def capture_output(code):
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        exec(code, {'bob': bob})
    except Exception as e:
        sys.stdout = old_stdout
        return str(e)

    output = sys.stdout.getvalue()
    sys.stdout = old_stdout
    return output


def highlight_syntax(event=None):
    editor.tag_remove("keyword", "1.0", "end")
    editor.tag_remove("string", "1.0", "end")
    editor.tag_remove("comment", "1.0", "end")
    editor.tag_remove("number", "1.0", "end")

    code = editor.get("1.0", "end-1c").split("\n")

    patterns = {
        "keyword": r"\b(def|class|import|from|return|if|else|elif|for|while|try|except|print|True|False|None)\b",
        "string": r"(\".*?\"|\'.*?\')",
        "comment": r"#.*",
        "number": r"\b\d+\b",
    }

    for lineno, line in enumerate(code, start=1):
        for tag, pattern in patterns.items():
            for match in re.finditer(pattern, line):
                start_idx = f"{lineno}.{match.start()}"
                end_idx = f"{lineno}.{match.end()}"
                editor.tag_add(tag, start_idx, end_idx)


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
            self.create_text(8, y + 2, anchor="nw", text=line_num, font=self.font, fill="#333")
            i = self.text_widget.index(f"{i}+1line")
        self.after(50, self.update_line_numbers)


def run_code(editor, shell):
    code = editor.get("1.0", "end-1c")
    output = capture_output(code)

    shell.config(state="normal")
    shell.delete(1.0, "end")
    shell.insert("insert", output)
    shell.config(state="disabled")


def workbench():
    global editor, running
    root = tk.Tk()
    root.title("Sajilo Python Workbench")

    def on_closing():
        global running
        running = False
        pygame.quit()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Editor Frame
    editor_frame = tk.Frame(root)
    editor_frame.pack(fill="both", expand=True)

    # Editor
    editor = scrolledtext.ScrolledText(editor_frame, height=15, width=50, font=("Helvetica", 14))
    editor.configure(insertbackground="black", insertwidth=2)
    editor.pack(side="right", fill="both", expand=True)

    editor.tag_configure("keyword", foreground="blue")
    editor.tag_configure("string", foreground="green")
    editor.tag_configure("comment", foreground="gray")
    editor.tag_configure("number", foreground="purple")
    editor.tag_configure("current_line", background="#e8e815")

    def highlight_current_line(event=None):
        editor.tag_remove("current_line", "1.0", "end")
        editor.tag_add("current_line", "insert linestart", "insert lineend+1c")

    editor.bind("<KeyRelease>", lambda e: (highlight_syntax(), highlight_current_line()))
    highlight_current_line()

    # Line numbers
    line_numbers = LineNumberCanvas(editor, editor_frame)
    line_numbers.pack(side="left", fill="y")

    # Shell Output
    shell = tk.Text(root, height=7, bg="black", fg="white", state="disabled")
    shell.pack(fill='both', expand=False)

    # Run Button
    run_button = tk.Button(root, text="Run", command=lambda: run_code(editor, shell))
    run_button.pack()

    # Start Pygame in background
    threading.Thread(target=playground, daemon=True).start()
    root.mainloop()


workbench()