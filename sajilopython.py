import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog, Menu, PhotoImage
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
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 20
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

    # Toolbar
    toolbar = tk.Frame(root, bg="#f0f0f0", height=30)
    toolbar.pack(fill="x")

    # Save and Load icons
    save_icon = PhotoImage(file="icons/save.png")
    load_icon = PhotoImage(file="icons/load.png")
    about_icon = PhotoImage(file="icons/about.png")
    new_icon = PhotoImage(file="icons/new.png")
    close_icon = PhotoImage(file="icons/close.png")
    undo_icon = PhotoImage(file="icons/undo.png")
    redo_icon = PhotoImage(file="icons/redo.png")

    # Undo and Redo functions
    def undo_action():
        try:
            editor.edit_undo()
            update_status("Undo performed")
        except:
            pass

    def redo_action():
        try:
            editor.edit_redo()
            update_status("Redo performed")
        except:
            pass

    # Buttons with padding and tooltip
    undo_button = tk.Button(toolbar, image=undo_icon, command=undo_action, padx=5, pady=5)
    undo_button.image = undo_icon
    undo_button.pack(side="left", padx=2)
    CreateToolTip(undo_button, "Undo (Ctrl+Z)")

    redo_button = tk.Button(toolbar, image=redo_icon, command=redo_action, padx=5, pady=5)
    redo_button.image = redo_icon
    redo_button.pack(side="left", padx=2)
    CreateToolTip(redo_button, "Redo (Ctrl+Y)")

    # New File
    def new_file():
        editor.delete("1.0", "end")
        update_status("New file created")

    # Close File (clears editor and shell)
    def close_file():
        editor.delete("1.0", "end")
        shell.configure(state="normal")
        shell.delete("1.0", "end")
        shell.configure(state="disabled")
        update_status("File closed")

    # New and Close buttons
    new_button = tk.Button(toolbar, image=new_icon, command=new_file)
    new_button.image = new_icon
    new_button.pack(side="left", padx=2)
    CreateToolTip(new_button, "New File (Ctrl+N)")

    close_button = tk.Button(toolbar, image=close_icon, command=close_file)
    close_button.image = close_icon
    close_button.pack(side="left", padx=2)
    CreateToolTip(close_button, "Close (Ctrl+Q)")

    # Save File
    def save_file():
        file_path = filedialog.asksaveasfilename(defaultextension=".py",
                                                 filetypes=[("Python Files", "*.py")])
        if file_path:
            with open(file_path, "w") as f:
                f.write(editor.get("1.0", "end-1c"))
                # update status
                update_status("File saved successfully!")

    # Load File
    def load_file():
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            with open(file_path, "r") as f:
                content = f.read()
            editor.delete("1.0", "end")
            editor.insert("1.0", content)
            # update status
            update_status("File saved successfully!")

    # About Dialog
    def show_about():
        tk.messagebox.showinfo("About", "Sajilo Python Workbench\nCreated by Beyond Apogee")

    # Toolbar Buttons
    save_button = tk.Button(toolbar, image=save_icon, command=save_file)
    save_button.image = save_icon
    save_button.pack(side="left", padx=2)
    CreateToolTip(save_button, "Save File (Ctrl+S)")

    load_button = tk.Button(toolbar, image=load_icon, command=load_file)
    load_button.image = load_icon
    load_button.pack(side="left", padx=2)
    CreateToolTip(load_button, "Open File (Ctrl+O)")

    about_button = tk.Button(toolbar, image=about_icon, command=show_about)
    about_button.image = about_icon
    about_button.pack(side="left", padx=2)
    CreateToolTip(about_button, "About")

    # Dropdown menu
    menu_button = tk.Menubutton(toolbar, text="Options", relief="raised", bg="#ddd")
    menu = Menu(menu_button, tearoff=0)
    menu_button.config(menu=menu)

    # Variables for toggles
    gravity_on = tk.BooleanVar(value=True)
    pygame_window_open = tk.BooleanVar(value=True)

    def toggle_gravity():
        global GRAVITY
        GRAVITY = 1 if gravity_on.get() else 0

    def toggle_pygame():
        pygame_window_open.set(not pygame_window_open.get())
        if not pygame_window_open.get():
            pygame.quit()
        else:
            threading.Thread(target=playground, daemon=True).start()

    menu.add_checkbutton(label="Gravity ON/OFF", variable=gravity_on, command=toggle_gravity)
    menu.add_command(label="Close Pygame Window", command=toggle_pygame)
    menu.add_separator()
    menu.add_command(label="Settings", command=lambda: print("Settings clicked"))

    menu_button.pack(side="right", padx=5)

    # Shortcut bindings
    root.bind("<Control-s>", lambda event: save_file())
    root.bind("<Control-o>", lambda event: open_file())
    root.bind("<Control-n>", lambda event: new_file())
    root.bind("<Control-w>", lambda event: close_file())
    root.bind("<Control-z>", lambda event: undo_action())
    root.bind("<Control-y>", lambda event: redo_action())
    root.bind("<F5>", lambda event: run_code(editor, shell))

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
    # Run Button (without green background)
    run_icon = PhotoImage(file="icons/play.png")
    run_button = tk.Button(root, text=" Run", image=run_icon, compound="left",
                           font=("Helvetica", 10, "bold"),
                           command=lambda: run_code(editor, shell))
    run_button.image = run_icon
    run_button.pack(pady=4)

    # Status Bar
    status_var = tk.StringVar()
    status_bar = tk.Label(root, textvariable=status_var, bd=1, relief=tk.SUNKEN, anchor="w")
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(message):
        status_var.set(message)

    # Start Pygame in background
    threading.Thread(target=playground, daemon=True).start()
    root.mainloop()


workbench()