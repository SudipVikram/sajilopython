import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, Menu, PhotoImage, messagebox
import pygame
import threading
import re
import sys
import io
import os
import ctypes

# Initialize pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 800, 500
BG_COLOR = (0, 0, 0)
GRAVITY = 1

# Global flag for running state
running = True

# Global tab tracking
tabs = {}

class CreateToolTip(object):
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.showtip)
        widget.bind("<Leave>", self.hidetip)

    def showtip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify="left",
                         background="#ffffe0", relief="solid", borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

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

# Embed Pygame in Tkinter using a canvas
class EmbeddedPygame:
    def __init__(self, frame):
        os.environ['SDL_WINDOWID'] = str(frame.winfo_id())
        if sys.platform == "win32":
            ctypes.windll.user32.SetProcessDPIAware()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.init()
        pygame.display.update()
        self.running = True
        self.rect = pygame.Rect(375, 400, 50, 50)
        self.velocity_y = 0
        self.is_jumping = False
        self.speech = ""
        self.loop()

    def loop(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    return

            self.velocity_y += GRAVITY
            self.rect.y += self.velocity_y
            if self.rect.bottom > HEIGHT:
                self.rect.bottom = HEIGHT
                self.velocity_y = 0
                self.is_jumping = False

            self.screen.fill(BG_COLOR)
            pygame.draw.rect(self.screen, (255, 0, 0), self.rect)
            if self.speech:
                font = pygame.font.SysFont("Comic Sans MS", 20)
                text_surface = font.render(self.speech, True, (255, 255, 255))
                pygame.draw.rect(self.screen, (0, 0, 0), (
                    self.rect.x + 10, self.rect.y - 30,
                    text_surface.get_width() + 10, text_surface.get_height() + 10))
                self.screen.blit(text_surface, (self.rect.x + 15, self.rect.y - 25))

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

def highlight_syntax(editor):
    editor.tag_remove("keyword", "1.0", "end")
    editor.tag_remove("string", "1.0", "end")
    editor.tag_remove("comment", "1.0", "end")
    editor.tag_remove("number", "1.0", "end")

    code = editor.get("1.0", "end-1c").split("\n")
    patterns = {
        "keyword": r"\\b(def|class|import|from|return|if|else|elif|for|while|try|except|print|True|False|None)\\b",
        "string": r'(\".*?\"|\'.*?\')',
        "comment": r"#.*",
        "number": r"\\b\\d+\\b",
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

def workbench():
    global running
    root = tk.Tk()
    root.title("Sajilo Python Workbench")
    root.state('zoomed')

    def run_code():
        tab = notebook.select()
        if not tab:
            return
        editor = tabs[tab]['editor']
        shell.config(state="normal")
        shell.delete("1.0", "end")
        output = capture_output(editor.get("1.0", "end-1c"))
        shell.insert("insert", output)
        shell.config(state="disabled")

    def update_status(message):
        status_var.set(message)

    def highlight_current_line(editor):
        editor.tag_remove("current_line", "1.0", "end")
        editor.tag_add("current_line", "insert linestart", "insert lineend+1c")

    def add_new_tab(filename="Untitled", content=""):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text=os.path.basename(filename))
        notebook.select(tab)

        line_frame = tk.Frame(tab)
        line_frame.pack(fill="both", expand=True)

        editor = scrolledtext.ScrolledText(line_frame, undo=True, wrap="none", font=("Helvetica", 14))
        editor.insert("1.0", content)
        editor.pack(side="right", fill="both", expand=True)
        editor.configure(insertbackground="black", insertwidth=2)

        line_numbers = LineNumberCanvas(editor, line_frame)
        line_numbers.pack(side="left", fill="y")

        editor.tag_configure("keyword", foreground="blue")
        editor.tag_configure("string", foreground="green")
        editor.tag_configure("comment", foreground="gray")
        editor.tag_configure("number", foreground="purple")
        editor.tag_configure("current_line", background="#f5eb5f")

        editor.bind("<KeyRelease>", lambda e: (highlight_syntax(editor), highlight_current_line(editor)))
        highlight_current_line(editor)

        tabs[str(tab)] = {'editor': editor, 'filepath': None}
        return tab

    def get_current_editor():
        tab = notebook.select()
        if tab in tabs:
            return tabs[tab]['editor']
        return None

    def new_file():
        add_new_tab()
        update_status("New file created")

    def close_file():
        tab = notebook.select()
        if tab:
            notebook.forget(tab)
            tabs.pop(tab, None)
            update_status("File closed")

    def save_file():
        tab = notebook.select()
        if not tab:
            return
        editor = tabs[tab]['editor']
        filepath = tabs[tab]['filepath']

        if not filepath:
            filepath = filedialog.asksaveasfilename(defaultextension=".py",
                                                     filetypes=[("Python Files", "*.py")])
            if not filepath:
                return

        with open(filepath, "w") as f:
            f.write(editor.get("1.0", "end-1c"))

        tabs[tab]['filepath'] = filepath
        notebook.tab(tab, text=os.path.basename(filepath))
        update_status("File saved successfully!")

    def load_file():
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            with open(file_path, "r") as f:
                content = f.read()
            tab = add_new_tab(file_path, content)
            tabs[str(tab)]['filepath'] = file_path
            update_status("File opened successfully!")

    def undo_action():
        editor = get_current_editor()
        if editor:
            editor.edit_undo()
            update_status("Undo performed")

    def redo_action():
        editor = get_current_editor()
        if editor:
            editor.edit_redo()
            update_status("Redo performed")

    def show_about():
        messagebox.showinfo("About", "Sajilo Python Workbench\nCreated by Beyond Apogee")

    def toggle_gravity():
        global GRAVITY
        GRAVITY = 1 if gravity_on.get() else 0

    def toggle_pygame():
        pygame_window_open.set(not pygame_window_open.get())
        if not pygame_window_open.get():
            pygame.quit()
        else:
            threading.Thread(target=playground, daemon=True).start()

    gravity_on = tk.BooleanVar(value=True)
    pygame_window_open = tk.BooleanVar(value=True)

    toolbar = tk.Frame(root, bg="#f0f0f0", height=30)
    toolbar.pack(fill="x")

    new_icon = PhotoImage(file="icons/new.png")
    undo_icon = PhotoImage(file="icons/undo.png")
    redo_icon = PhotoImage(file="icons/redo.png")
    load_icon = PhotoImage(file="icons/load.png")
    save_icon = PhotoImage(file="icons/save.png")
    close_icon = PhotoImage(file="icons/close.png")
    about_icon = PhotoImage(file="icons/about.png")
    run_icon = PhotoImage(file="icons/play.png")

    tk.Button(toolbar, image=new_icon, command=new_file).pack(side="left", padx=2)
    tk.Button(toolbar, image=undo_icon, command=undo_action).pack(side="left", padx=2)
    tk.Button(toolbar, image=redo_icon, command=redo_action).pack(side="left", padx=2)
    tk.Button(toolbar, image=load_icon, command=load_file).pack(side="left", padx=2)
    tk.Button(toolbar, image=save_icon, command=save_file).pack(side="left", padx=2)
    tk.Button(toolbar, image=close_icon, command=close_file).pack(side="left", padx=2)
    tk.Button(toolbar, image=about_icon, command=show_about).pack(side="left", padx=2)
    tk.Button(toolbar, image=run_icon, command=run_code).pack(side="left", padx=2)

    menu_button = tk.Menubutton(toolbar, text="Options", relief="raised", bg="#ddd")
    menu = Menu(menu_button, tearoff=0)
    menu_button.config(menu=menu)

    menu.add_checkbutton(label="Gravity ON/OFF", variable=gravity_on, command=toggle_gravity)
    menu.add_command(label="Close Pygame Window", command=toggle_pygame)
    menu.add_separator()
    menu.add_command(label="Settings", command=lambda: print("Settings clicked"))
    menu_button.pack(side="right", padx=5)

    root.bind_all("<Control-s>", lambda event: save_file())
    root.bind_all("<Control-o>", lambda event: load_file())
    root.bind_all("<Control-n>", lambda event: new_file())
    root.bind_all("<Control-w>", lambda event: close_file())
    root.bind_all("<Control-z>", lambda event: undo_action())
    root.bind_all("<Control-y>", lambda event: redo_action())
    root.bind_all("<F5>", lambda event: run_code())

    editor_frame = tk.Frame(root)
    editor_frame.pack(fill="both", expand=True)

    notebook = ttk.Notebook(editor_frame)
    notebook.pack(fill="both", expand=True)

    # Shell Output
    shell = tk.Text(root, height=7, bg="black", fg="white", state="disabled")
    shell.pack(fill='both', expand=False)

    # Status Bar
    status_var = tk.StringVar()
    status_bar = tk.Label(root, textvariable=status_var, bd=1, relief=tk.SUNKEN, anchor="w")
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    add_new_tab()
    threading.Thread(target=playground, daemon=True).start()
    root.mainloop()

workbench()