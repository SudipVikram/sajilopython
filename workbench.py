import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, Menu, messagebox, simpledialog, font
import pygame
import threading
import re
import sys
import os
import ctypes
import io
import shutil

# Initialize pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 600, 500
BG_COLOR = (0, 0, 0)
GRAVITY = 1


class BobCharacter:
    def __init__(self):
        self.rect = pygame.Rect(275, HEIGHT - 70, 50, 50)  # Fixed at bottom
        self.color = (255, 100, 100)
        self.velocity_y = 0
        self.is_jumping = False
        self.speech = ""
        self.loaded = False

    def load(self):
        self.loaded = True

    def move_left(self):
        if self.loaded:
            self.rect.x -= 5
            if self.rect.left < 0:
                self.rect.left = 0

    def move_right(self):
        if self.loaded:
            self.rect.x += 5
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH

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
        if self.rect.bottom > HEIGHT - 10:
            self.rect.bottom = HEIGHT - 10
            self.velocity_y = 0
            self.is_jumping = False

    def draw(self, screen):
        if not self.loaded:
            return
        pygame.draw.rect(screen, self.color, self.rect)
        if self.speech:
            font = pygame.font.SysFont("Comic Sans MS", 18)
            text_surface = font.render(self.speech, True, (255, 255, 255))
            pygame.draw.rect(screen, (0, 0, 0), (
                self.rect.x + 10, self.rect.y - 30,
                text_surface.get_width() + 10, text_surface.get_height() + 10))
            screen.blit(text_surface, (self.rect.x + 15, self.rect.y - 25))


bob = BobCharacter()


class PygameManager:
    def __init__(self):
        self.screen = None
        self.running = False
        self.thread = None
        self.frame = None

    def init_pygame(self, window_id=None):
        if window_id:
            os.environ['SDL_WINDOWID'] = str(window_id)
        if sys.platform == "win32":
            ctypes.windll.user32.SetProcessDPIAware()
        pygame.display.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Sajilo Playground")
        self.running = True
        bob.load()

    def quit_pygame(self):
        self.running = False
        if pygame.get_init():
            pygame.quit()

    def run_playground(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_pygame()
                    return

            bob.update()
            self.screen.fill(BG_COLOR)
            bob.draw(self.screen)
            pygame.display.update()
            clock.tick(30)


pygame_manager = PygameManager()


class AutoCompleteText(scrolledtext.ScrolledText):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind("<KeyRelease>", self._on_key_release)
        self.bind("<Tab>", self._on_tab)
        self.bind("<Return>", self._on_return)
        self.bind("<BackSpace>", self._on_backspace)
        self.completion_list = [
            'print', 'range', 'len', 'input', 'def', 'class',
            'if', 'else', 'elif', 'for', 'while', 'try', 'except',
            'import', 'from', 'return', 'True', 'False', 'None',
            'bob.move_left()', 'bob.move_right()', 'bob.jump()', 'bob.say()'
        ]
        self.completion_start = None
        self.popup = None

    def _on_key_release(self, event):
        if event.keysym in ('BackSpace', 'Left', 'Right', 'Up', 'Down'):
            self._remove_popup()
            return

        # Get current word
        word = self.get_current_word()
        if not word:
            self._remove_popup()
            return

        # Get matches
        matches = [w for w in self.completion_list if w.startswith(word)]
        if not matches:
            self._remove_popup()
            return

        # Show popup
        self._show_popup(matches)

    def get_current_word(self):
        pos = self.index(tk.INSERT)
        start = pos.split('.')
        start[1] = str(int(start[1]) - 20)  # Look back 20 chars max
        start = '.'.join(start)

        try:
            word = self.get(start, pos)
            word = re.sub(r'[^a-zA-Z0-9_]', '', word)
            self.completion_start = f"{pos.split('.')[0]}.{pos.split('.')[1]}-{len(word)}c"
            return word
        except:
            return None

    def _show_popup(self, matches):
        self._remove_popup()

        x, y, _, _ = self.bbox(tk.INSERT)
        x += self.winfo_rootx() + 20
        y += self.winfo_rooty() + 20

        self.popup = tk.Toplevel(self)
        self.popup.wm_overrideredirect(True)
        self.popup.wm_geometry(f"+{x}+{y}")

        lb = tk.Listbox(self.popup, height=min(5, len(matches)), font=("Comic Sans MS", 12))
        lb.pack()

        for m in matches:
            lb.insert(tk.END, m)

        lb.bind("<Button-1>", lambda e: self._insert_completion(lb.get(lb.curselection())))
        lb.bind("<Return>", lambda e: self._insert_completion(lb.get(lb.curselection())))

    def _remove_popup(self):
        if self.popup:
            self.popup.destroy()
            self.popup = None

    def _on_tab(self, event):
        if self.popup:
            lb = self.popup.winfo_children()[0]
            if lb.size() > 0:
                self._insert_completion(lb.get(0))
            return "break"
        return None

    def _insert_completion(self, completion):
        self._remove_popup()
        if self.completion_start:
            self.delete(self.completion_start, tk.INSERT)
            self.insert(tk.INSERT, completion)
            self.completion_start = None

    def _on_return(self, event):
        # Auto-indent on new line
        current_line = self.get("insert linestart", "insert")
        indent = re.match(r'^\s*', current_line).group()
        self.insert(tk.INSERT, "\n" + indent)
        return "break"

    def _on_backspace(self, event):
        # Smart backspace for indentation
        cursor_pos = self.index(tk.INSERT)
        line_start = self.get(cursor_pos + " linestart", cursor_pos)
        if line_start.isspace() and len(line_start) > 0:
            self.delete(cursor_pos + "-1c linestart", cursor_pos)
            return "break"
        return None


class LineNumberCanvas(tk.Canvas):
    def __init__(self, text_widget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_widget = text_widget
        self.font = ("Comic Sans MS", 13)
        self.config(width=35, bg="#e6f3ff")
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


def capture_output(code):
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        exec(code, {'bob': bob})
    except Exception as e:
        sys.stdout = old_stdout
        return f"Error: {str(e)}"
    output = sys.stdout.getvalue()
    sys.stdout = old_stdout
    return output


def highlight_syntax(editor):
    editor.tag_remove("keyword", "1.0", "end")
    editor.tag_remove("builtin", "1.0", "end")
    editor.tag_remove("string", "1.0", "end")
    editor.tag_remove("comment", "1.0", "end")
    editor.tag_remove("number", "1.0", "end")
    editor.tag_remove("loop", "1.0", "end")
    editor.tag_remove("function", "1.0", "end")
    editor.tag_remove("classobj", "1.0", "end")

    code = editor.get("1.0", "end-1c").split("\n")
    patterns = {
        "keyword": r"\b(def|class|import|from|return|if|else|elif|try|except|True|False|None)\b",
        "builtin": r"\b(print|input|range|len)\b",
        "loop": r"\b(for|while|in)\b",
        "function": r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(?=\()",
        "classobj": r"\b([A-Z][a-zA-Z0-9_]*)\b",
        "string": r'(\".*?\"|\'.*?\')',
        "comment": r"#.*",
        "number": r"\b\d+\b",
    }

    for lineno, line in enumerate(code, start=1):
        for tag, pattern in patterns.items():
            for match in re.finditer(pattern, line):
                start_idx = f"{lineno}.{match.start()}"
                end_idx = f"{lineno}.{match.end()}"
                editor.tag_add(tag, start_idx, end_idx)


def workbench():
    root = tk.Tk()
    root.title("Sajilo Python Workbench")
    root.state('zoomed')

    # Initialize control variables
    gravity_on = tk.BooleanVar(value=True)
    global GRAVITY
    GRAVITY = 1

    tabs = {}
    unsaved_changes = {}

    def toggle_gravity():
        global GRAVITY
        GRAVITY = 1 if gravity_on.get() else 0
        status_var.set(f"Gravity {'ON' if gravity_on.get() else 'OFF'}")

    # Main layout containers
    main_panel = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashwidth=8, sashrelief=tk.RAISED)
    main_panel.pack(fill=tk.BOTH, expand=True)

    # Left panel (Editor + Shell)
    left_panel = tk.PanedWindow(main_panel, orient=tk.VERTICAL, sashwidth=8, sashrelief=tk.RAISED)
    main_panel.add(left_panel)

    # Right panel (Playground)
    right_panel = tk.Frame(main_panel, bg='#333333')
    main_panel.add(right_panel)

    # Editor Notebook
    editor_frame = ttk.Frame(left_panel)
    left_panel.add(editor_frame, height=500)

    notebook = ttk.Notebook(editor_frame)
    notebook.pack(fill="both", expand=True)

    # Configure tab style
    style = ttk.Style()
    style.configure("TNotebook.Tab", font=("Comic Sans MS", 12), padding=[10, 5])
    style.configure("TNotebook", tabmargins=[2, 5, 2, 0])  # Reduce tab indent

    # Shell Output
    shell_frame = ttk.Frame(left_panel)
    left_panel.add(shell_frame, height=200)

    shell = scrolledtext.ScrolledText(shell_frame, height=10, bg="black", fg="white",
                                      font=("Consolas", 12), state="disabled",
                                      insertbackground="white")
    shell.pack(fill='both', expand=True)

    # Initialize playground
    pygame_frame = tk.Frame(right_panel, width=WIDTH, height=HEIGHT)
    pygame_frame.pack(fill="both", expand=True)
    pygame_manager.init_pygame(pygame_frame.winfo_id())

    # Start pygame thread
    def run_pygame():
        pygame_manager.run_playground()

    threading.Thread(target=run_pygame, daemon=True).start()

    # UI Functions
    def run_code():
        tab = notebook.select()
        if not tab:
            return
        editor = tabs[str(tab)]['editor']
        shell.config(state="normal")
        shell.delete("1.0", "end")
        output = capture_output(editor.get("1.0", "end-1c"))
        shell.insert("insert", output)
        shell.config(state="disabled")
        shell.see("end")
        status_var.set("Code executed!")

    def update_status(message):
        status_var.set(message)

    def highlight_current_line(editor):
        editor.tag_remove("current_line", "1.0", "end")
        editor.tag_add("current_line", "insert linestart", "insert lineend+1c")

    def add_new_tab(filename="Untitled", content=""):
        tab = ttk.Frame(notebook)
        tab_name = os.path.basename(filename)
        notebook.add(tab, text=tab_name)
        notebook.select(tab)

        line_frame = tk.Frame(tab, bg="#f5f5f5")
        line_frame.pack(fill="both", expand=True)

        editor = AutoCompleteText(line_frame, undo=True, wrap="none",
                                  font=("Comic Sans MS", 14),
                                  bg="white", padx=10, pady=10)
        editor.insert("1.0", content)
        editor.pack(side="right", fill="both", expand=True)

        line_numbers = LineNumberCanvas(editor, line_frame)
        line_numbers.pack(side="left", fill="y")

        # Configure tab stops for proper indentation
        font = tk.font.Font(font=editor['font'])
        tab_width = font.measure('    ')  # 4 spaces
        editor.config(tabs=tab_width)

        # Syntax highlighting
        editor.tag_configure("keyword", foreground="#FF5722", font=("Comic Sans MS", 14, "bold"))
        editor.tag_configure("builtin", foreground="#1976D2", font=("Comic Sans MS", 14, "bold"))
        editor.tag_configure("loop", foreground="#FF9800", font=("Comic Sans MS", 14, "bold"))
        editor.tag_configure("function", foreground="#7B1FA2", font=("Comic Sans MS", 14))
        editor.tag_configure("classobj", foreground="#00897B", font=("Comic Sans MS", 14, "bold"))
        editor.tag_configure("string", foreground="#388E3C")
        editor.tag_configure("comment", foreground="#9E9E9E", font=("Comic Sans MS", 14, "italic"))
        editor.tag_configure("number", foreground="#9C27B0")
        editor.tag_configure("current_line", background="#fffacd")

        def mark_unsaved(event=None):
            if str(tab) in tabs:
                unsaved_changes[str(tab)] = True
                update_tab_title(tab)

        editor.bind("<KeyRelease>",
                    lambda e: (highlight_syntax(editor), highlight_current_line(editor), mark_unsaved()))
        editor.bind("<<Modified>>", mark_unsaved)
        highlight_current_line(editor)

        tabs[str(tab)] = {'editor': editor, 'filepath': None}
        unsaved_changes[str(tab)] = False
        return tab

    def update_tab_title(tab):
        tab_id = notebook.index(tab)
        filepath = tabs[str(tab)]['filepath']
        basename = os.path.basename(filepath) if filepath else "Untitled"
        if unsaved_changes.get(str(tab), False):
            notebook.tab(tab_id, text=f"*{basename}")
        else:
            notebook.tab(tab_id, text=basename)

    def check_unsaved_changes(tab):
        if unsaved_changes.get(str(tab), False):
            filepath = tabs[str(tab)]['filepath']
            name = os.path.basename(filepath) if filepath else "Untitled"
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                f"Do you want to save changes to {name}?",
                parent=root
            )
            if response is None:  # Cancel
                return False
            if response:  # Yes
                return save_file(tab=tab)
        return True

    def save_file(tab=None):
        tab = tab or notebook.select()
        if not tab:
            return False
        editor = tabs[str(tab)]['editor']
        filepath = tabs[str(tab)]['filepath']

        if not filepath:
            filepath = filedialog.asksaveasfilename(defaultextension=".py",
                                                    filetypes=[("Python Files", "*.py")])
            if not filepath:
                return False

        with open(filepath, "w") as f:
            f.write(editor.get("1.0", "end-1c"))

        tabs[str(tab)]['filepath'] = filepath
        unsaved_changes[str(tab)] = False
        update_tab_title(tab)
        update_status("File saved successfully!")
        return True

    def close_file():
        tab = notebook.select()
        if tab and check_unsaved_changes(tab):
            notebook.forget(tab)
            tabs.pop(str(tab), None)
            unsaved_changes.pop(str(tab), None)
            update_status("File closed")

    def new_file():
        add_new_tab()
        update_status("New file created")

    def load_file():
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            with open(file_path, "r") as f:
                content = f.read()
            tab = add_new_tab(file_path, content)
            tabs[str(tab)]['filepath'] = file_path
            update_status(f"Opened: {file_path}")

    def show_about():
        messagebox.showinfo("About Sajilo Python",
                            "Sajilo Python Workbench\n\n"
                            "A kid-friendly Python editor with visual feedback\n"
                            "Created by Beyond Apogee\n\n"
                            "Version 1.0")

    def upload_library():
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            try:
                dest_path = os.path.join(os.getcwd(), os.path.basename(file_path))
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                shutil.copy(file_path, os.getcwd())
                status_var.set(f"Library updated: {os.path.basename(file_path)}")
            except Exception as e:
                status_var.set(f"Error: {str(e)}")

    # Toolbar
    toolbar = tk.Frame(root, bg="#c0e0ff", height=40)
    toolbar.pack(fill="x", padx=5, pady=5)

    button_style = {
        'font': ("Comic Sans MS", 12),
        'fg': "black",
        'borderwidth': 3,
        'relief': "raised",
        'padx': 10,
        'pady': 5
    }

    # Buttons in order with Run last
    tk.Button(toolbar, text="🆕 New", command=new_file,
              bg="#FF9800", **button_style).pack(side="left", padx=5)
    tk.Button(toolbar, text="📂 Open", command=load_file,
              bg="#9C27B0", **button_style).pack(side="left", padx=5)
    tk.Button(toolbar, text="💾 Save", command=lambda: save_file(notebook.select()),
              bg="#2196F3", **button_style).pack(side="left", padx=5)
    tk.Button(toolbar, text="❌ Close", command=close_file,
              bg="#F44336", **button_style).pack(side="left", padx=5)
    tk.Button(toolbar, text="▶️ Run", command=run_code,
              bg="#4CAF50", **button_style).pack(side="left", padx=5)
    tk.Button(toolbar, text="ℹ️ About", command=show_about,
              bg="#607D8B", **button_style).pack(side="left", padx=5)

    # Options menu
    menu_button = tk.Menubutton(toolbar, text="⚙️ Options",
                                bg="#FFFFFF", fg="black",
                                font=("Comic Sans MS", 12),
                                relief="raised", borderwidth=3)
    menu = Menu(menu_button, tearoff=0, font=("Comic Sans MS", 10))
    menu_button.config(menu=menu)

    menu.add_checkbutton(label="🌍 Gravity ON/OFF",
                         variable=gravity_on,
                         command=toggle_gravity)
    menu.add_command(label="📤 Upload Library", command=upload_library)
    menu_button.pack(side="right", padx=10)

    # Keyboard shortcuts
    root.bind_all("<Control-n>", lambda e: new_file())
    root.bind_all("<Control-o>", lambda e: load_file())
    root.bind_all("<Control-s>", lambda e: save_file())
    root.bind_all("<Control-w>", lambda e: close_file())
    root.bind_all("<F5>", lambda e: run_code())

    # Status bar
    status_var = tk.StringVar()
    status_var.set("🚀 Ready to code!")
    status_bar = tk.Label(root, textvariable=status_var, bd=2, relief=tk.SUNKEN,
                          anchor="w", bg="#FFEB3B", fg="black",
                          font=("Comic Sans MS", 10))
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # Initial setup
    add_new_tab()

    def on_closing():
        # Check all tabs for unsaved changes
        for tab in list(tabs.keys()):
            notebook.select(tab)
            if not check_unsaved_changes(tab):
                return  # User cancelled closing

        pygame_manager.quit_pygame()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


workbench()