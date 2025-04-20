import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import font as tkfont, colorchooser
import pygame
import threading
import re
import sys
import os
import ctypes
import io
import shutil
import json
from _thread import interrupt_main

# Set appearance mode and color theme
ctk.set_appearance_mode("system")  # "light", "dark", or "system"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue", etc.

# Initialize pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 600, 500
BG_COLOR = (0, 0, 0)
GRAVITY = 1

# Global theme state
config_path = "config.json"


def load_config():
    default_config = {
        "theme_mode": "system",
        "ctk_theme": "blue",
        "editor_font_family": "Comic Sans MS",
        "editor_font_size": 14,
        "editor_font_color": "black",
        "bg_color": "#f5f5f5",
        "fg_color": "black",
        "insert_bg": "black",
        "shell_bg": "black",
        "shell_fg": "white",
        "highlight_bg": "#fffacd",
        "line_bg": "#e6f3ff"
    }

    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                loaded_config = json.load(f)
                return {**default_config, **loaded_config}
        except:
            return default_config
    return default_config


config = load_config()
theme_mode = config["theme_mode"]
ctk_theme = config["ctk_theme"]
editor_font_family = config["editor_font_family"]
editor_font_size = config["editor_font_size"]
editor_font_color = config["editor_font_color"]
bg_color = config["bg_color"]
fg_color = config["fg_color"]
insert_bg = config["insert_bg"]
shell_bg = config["shell_bg"]
shell_fg = config["shell_fg"]
highlight_bg = config["highlight_bg"]
line_bg = config["line_bg"]


def save_config():
    with open(config_path, "w") as f:
        json.dump({
            "theme_mode": theme_mode,
            "ctk_theme": ctk_theme,
            "editor_font_family": editor_font_family,
            "editor_font_size": editor_font_size,
            "editor_font_color": editor_font_color,
            "bg_color": bg_color,
            "fg_color": fg_color,
            "insert_bg": insert_bg,
            "shell_bg": shell_bg,
            "shell_fg": shell_fg,
            "highlight_bg": highlight_bg,
            "line_bg": line_bg
        }, f)


class BobCharacter:
    def __init__(self):
        self.rect = pygame.Rect(275, HEIGHT - 70, 50, 50)
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


class AutoCompleteText(ctk.CTkTextbox):
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

        word = self.get_current_word()
        if not word:
            self._remove_popup()
            return

        matches = [w for w in self.completion_list if w.startswith(word)]
        if not matches:
            self._remove_popup()
            return

        self._show_popup(matches)

    def get_current_word(self):
        pos = self.index("insert")
        start = pos.split('.')
        start[1] = str(int(start[1]) - 20)
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

        x, y, _, _ = self.bbox("insert")
        x += self.winfo_rootx() + 20
        y += self.winfo_rooty() + 20

        self.popup = ctk.CTkToplevel(self)
        self.popup.wm_overrideredirect(True)
        self.popup.wm_geometry(f"+{x}+{y}")

        lb = ctk.CTkScrollableFrame(self.popup)
        lb.pack()

        for m in matches:
            # Create a closure to capture the current value of m
            def make_lambda(match):
                return lambda: self._insert_completion(match)

            btn = ctk.CTkButton(lb, text=m, command=make_lambda(m))
            btn.pack(fill="x")

    def _remove_popup(self):
        if self.popup:
            self.popup.destroy()
            self.popup = None

    def _on_tab(self, event):
        if self.popup:
            if self.popup.winfo_children():
                first_child = self.popup.winfo_children()[0].winfo_children()[0]
                self._insert_completion(first_child.cget("text"))
            return "break"
        return None

    def _insert_completion(self, completion):
        self._remove_popup()
        if self.completion_start:
            self.delete(self.completion_start, "insert")
            self.insert("insert", completion)
            self.completion_start = None

    def _on_return(self, event):
        current_line = self.get("insert linestart", "insert")
        indent = re.match(r'^\s*', current_line).group()
        self.insert("insert", "\n" + indent)
        return "break"

    def _on_backspace(self, event):
        cursor_pos = self.index("insert")
        line_start = self.get(cursor_pos + " linestart", cursor_pos)
        if line_start.isspace() and len(line_start) > 0:
            self.delete(cursor_pos + "-1c linestart", cursor_pos)
            return "break"
        return None


class LineNumberCanvas(ctk.CTkCanvas):
    def __init__(self, text_widget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_widget = text_widget
        self.font = ("Comic Sans MS", 13)
        self.configure(width=35, bg=line_bg)
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
    if not pygame.get_init():
        return "Error: Pygame window is closed. Please reopen it from the Options menu."

    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    safe_globals = {
        'bob': bob,
        '__builtins__': {
            'print': print,
            'range': range,
            'len': len,
            'input': input,
            'str': str,
            'int': int,
            'float': float,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'bool': bool
        }
    }

    exec_result = {"output": None, "error": None}

    def execute_code():
        try:
            exec(code, safe_globals)
            exec_result["output"] = sys.stdout.getvalue()
        except Exception as e:
            exec_result["error"] = str(e)

    exec_thread = threading.Thread(target=execute_code)
    exec_thread.daemon = True
    exec_thread.start()

    exec_thread.join(timeout=3)

    if exec_thread.is_alive():
        interrupt_main()
        exec_thread.join()
        return "Error: Code execution timed out (possible infinite loop)"

    sys.stdout = old_stdout

    if exec_result["error"]:
        return f"Error: {exec_result['error']}"

    return exec_result["output"] or ""


def highlight_syntax(editor):
    text_widget = editor._textbox
    for tag in ["keyword", "builtin", "string", "comment", "number", "loop", "function", "classobj"]:
        text_widget.tag_remove(tag, "1.0", "end")

    code = text_widget.get("1.0", "end-1c").split("\n")
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
                text_widget.tag_add(tag, start_idx, end_idx)


def workbench():
    root = ctk.CTk()
    root.title("Sajilo Python Workbench")

    # Windows-specific window setup
    if sys.platform == "win32":
        root.state('zoomed')
    else:
        # Fallback for other OS
        root.after(100, lambda: root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0"))

    # Initialize control variables
    gravity_on = ctk.BooleanVar(value=True)
    global GRAVITY
    GRAVITY = 1

    tabs = {}
    unsaved_changes = {}

    def toggle_gravity():
        global GRAVITY
        GRAVITY = 1 if gravity_on.get() else 0
        status_var.set(f"Gravity {'ON' if gravity_on.get() else 'OFF'}")

    # Main layout containers
    main_panel = ctk.CTkFrame(root)
    main_panel.pack(fill="both", expand=True)

    # Left panel (Editor + Shell)
    left_panel = ctk.CTkFrame(main_panel)
    left_panel.pack(side="left", fill="both", expand=True)

    # Right panel (Playground)
    right_panel = ctk.CTkFrame(main_panel)
    right_panel.pack(side="right", fill="both", expand=True)

    # Editor Notebook
    editor_frame = ctk.CTkFrame(left_panel)
    editor_frame.pack(fill="both", expand=True)

    notebook = ctk.CTkTabview(editor_frame)
    notebook.pack(fill="both", expand=True)

    # Shell Output
    shell_frame = ctk.CTkFrame(left_panel)
    shell_frame.pack(fill="both", expand=True)

    shell = ctk.CTkTextbox(shell_frame, height=10, font=("Consolas", 12))
    shell.pack(fill='both', expand=True)

    # Initialize playground
    pygame_frame = ctk.CTkFrame(right_panel, width=WIDTH, height=HEIGHT)
    pygame_frame.pack(fill="both", expand=True)
    pygame_manager.init_pygame(pygame_frame.winfo_id())

    # Start pygame thread
    def run_pygame():
        try:
            clock = pygame.time.Clock()
            while pygame_manager.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame_manager.quit_pygame()
                        return

                try:
                    bob.update()
                    pygame_manager.screen.fill(BG_COLOR)
                    bob.draw(pygame_manager.screen)
                    pygame.display.update()
                    clock.tick(30)
                except KeyboardInterrupt:
                    pygame_manager.quit_pygame()
                    return
        except Exception as e:
            print(f"Playground error: {str(e)}")

    threading.Thread(target=run_pygame, daemon=True).start()

    # UI Functions
    def run_code():
        tab = notebook.get()
        if not tab:
            return
        editor = tabs[tab]['editor']
        shell.configure(state="normal")
        shell.delete("1.0", "end")
        output = capture_output(editor.get("1.0", "end-1c"))
        shell.insert("insert", output)
        shell.configure(state="disabled")
        shell.see("end")
        status_var.set("Code executed!")

    def update_status(message):
        status_var.set(message)

    def highlight_current_line(editor):
        text_widget = editor._textbox
        text_widget.tag_remove("current_line", "1.0", "end")
        text_widget.tag_add("current_line", "insert linestart", "insert lineend+1c")

    def add_new_tab(filename="Untitled", content=""):
        tab_name = os.path.basename(filename)
        notebook.add(tab_name)
        notebook.set(tab_name)

        tab_frame = notebook.tab(tab_name)
        line_frame = ctk.CTkFrame(tab_frame)
        line_frame.pack(fill="both", expand=True)

        editor = AutoCompleteText(line_frame, wrap="none",
                                  font=(editor_font_family, editor_font_size))
        editor.insert("1.0", content)

        # Configure tags on the underlying Text widget
        text_widget = editor._textbox
        text_widget.tag_configure("keyword", foreground="#FF5722",
                                  font=(editor_font_family, editor_font_size, "bold"))
        text_widget.tag_configure("builtin", foreground="#1976D2",
                                  font=(editor_font_family, editor_font_size, "bold"))
        text_widget.tag_configure("loop", foreground="#FF9800",
                                  font=(editor_font_family, editor_font_size, "bold"))
        text_widget.tag_configure("function", foreground="#7B1FA2",
                                  font=(editor_font_family, editor_font_size))
        text_widget.tag_configure("classobj", foreground="#00897B",
                                  font=(editor_font_family, editor_font_size, "bold"))
        text_widget.tag_configure("string", foreground="#388E3C")
        text_widget.tag_configure("comment", foreground="#9E9E9E",
                                  font=(editor_font_family, editor_font_size, "italic"))
        text_widget.tag_configure("number", foreground="#9C27B0")
        text_widget.tag_configure("current_line", background=highlight_bg)

        highlight_syntax(editor)
        highlight_current_line(editor)
        editor.pack(side="right", fill="both", expand=True)

        line_numbers = LineNumberCanvas(editor, line_frame)
        line_numbers.pack(side="left", fill="y")

        def mark_unsaved(event=None):
            if tab_name in tabs:
                unsaved_changes[tab_name] = True
                update_tab_title(tab_name)

        editor.bind("<KeyRelease>",
                    lambda e: (highlight_syntax(editor), highlight_current_line(editor), mark_unsaved()))
        editor.bind("<<Modified>>", mark_unsaved)
        highlight_current_line(editor)

        tabs[tab_name] = {'editor': editor, 'filepath': None}
        unsaved_changes[tab_name] = False
        return tab_name

    def update_tab_title(tab_name):
        filepath = tabs[tab_name]['filepath']
        basename = os.path.basename(filepath) if filepath else "Untitled"
        if unsaved_changes.get(tab_name, False):
            notebook.configure(tab_name, text=f"*{basename}")
        else:
            notebook.configure(tab_name, text=basename)

    def check_unsaved_changes(tab_name):
        if unsaved_changes.get(tab_name, False):
            filepath = tabs[tab_name]['filepath']
            name = os.path.basename(filepath) if filepath else "Untitled"
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                f"Do you want to save changes to {name}?",
                parent=root
            )
            if response is None:
                return False
            if response:
                return save_file(tab=tab_name)
        return True

    def save_file(tab=None):
        tab = tab or notebook.get()
        if not tab:
            return False
        editor = tabs[tab]['editor']
        filepath = tabs[tab]['filepath']

        if not filepath:
            filepath = filedialog.asksaveasfilename(defaultextension=".py",
                                                    filetypes=[("Python Files", "*.py")])
            if not filepath:
                return False

        with open(filepath, "w") as f:
            f.write(editor.get("1.0", "end-1c"))

        tabs[tab]['filepath'] = filepath
        unsaved_changes[tab] = False
        update_tab_title(tab)
        update_status("File saved successfully!")
        return True

    def close_file():
        tab = notebook.get()
        if tab and check_unsaved_changes(tab):
            notebook.delete(tab)
            tabs.pop(tab, None)
            unsaved_changes.pop(tab, None)
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
            tabs[tab]['filepath'] = file_path
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

    def reset_to_default():
        global theme_mode, ctk_theme, editor_font_family, editor_font_size, editor_font_color
        global bg_color, fg_color, insert_bg, shell_bg, shell_fg, highlight_bg, line_bg

        default_config = load_config()
        theme_mode = default_config["theme_mode"]
        ctk_theme = default_config["ctk_theme"]
        editor_font_family = default_config["editor_font_family"]
        editor_font_size = default_config["editor_font_size"]
        editor_font_color = default_config["editor_font_color"]
        bg_color = default_config["bg_color"]
        fg_color = default_config["fg_color"]
        insert_bg = default_config["insert_bg"]
        shell_bg = default_config["shell_bg"]
        shell_fg = default_config["shell_fg"]
        highlight_bg = default_config["highlight_bg"]
        line_bg = default_config["line_bg"]

        apply_theme()
        save_config()
        messagebox.showinfo("Reset Complete", "All settings have been reset to defaults")

    def open_settings():
        global settings_win

        if settings_win and ctk.Toplevel.winfo_exists(settings_win):
            settings_win.lift()
            return

        settings_win = ctk.CTkToplevel(root)
        settings_win.title("Settings")
        settings_win.geometry("400x550")
        settings_win.resizable(False, False)

        def choose_font_color():
            color = colorchooser.askcolor(title="Choose Font Color", parent=settings_win)
            if color[1]:
                global editor_font_color
                editor_font_color = color[1]
                apply_theme()
                save_config()

        def apply_font_settings():
            global editor_font_family, editor_font_size, editor_font_color
            editor_font_family = font_family_var.get()
            editor_font_size = int(font_size_var.get())
            apply_theme()
            save_config()

        def set_theme_mode(mode):
            global theme_mode
            theme_mode = mode
            ctk.set_appearance_mode(theme_mode)
            apply_theme()
            save_config()

        def set_ctk_theme(theme):
            global ctk_theme
            ctk_theme = theme
            ctk.set_default_color_theme(ctk_theme)
            apply_theme()
            save_config()

        ctk.CTkLabel(settings_win, text="Theme Mode:").pack(pady=(10, 0))
        theme_mode_var = ctk.StringVar(value=theme_mode)
        theme_mode_menu = ctk.CTkOptionMenu(settings_win, variable=theme_mode_var,
                                            values=["light", "dark", "system"],
                                            command=set_theme_mode)
        theme_mode_menu.pack()

        ctk.CTkLabel(settings_win, text="Color Theme:").pack(pady=(10, 0))
        ctk_theme_var = ctk.StringVar(value=ctk_theme)
        ctk_theme_menu = ctk.CTkOptionMenu(settings_win, variable=ctk_theme_var,
                                           values=["blue", "green", "dark-blue"],
                                           command=set_ctk_theme)
        ctk_theme_menu.pack()

        ctk.CTkLabel(settings_win, text="Font Family:").pack(pady=(10, 0))
        font_family_var = ctk.StringVar(value=editor_font_family)
        font_family_menu = ctk.CTkOptionMenu(settings_win, variable=font_family_var,
                                             values=sorted(tkfont.families()))
        font_family_menu.pack()

        ctk.CTkLabel(settings_win, text="Font Size:").pack(pady=(10, 0))
        font_size_var = ctk.StringVar(value=str(editor_font_size))
        font_size_menu = ctk.CTkOptionMenu(settings_win, variable=font_size_var,
                                           values=[str(s) for s in range(8, 33)])
        font_size_menu.pack()

        ctk.CTkButton(settings_win, text="Choose Font Color", command=choose_font_color).pack(pady=10)
        ctk.CTkButton(settings_win, text="Apply Font Settings", command=apply_font_settings).pack(pady=5)

        ctk.CTkLabel(settings_win,
                     text=f"Current Font: {editor_font_family}, Size: {editor_font_size}, Color: {editor_font_color}",
                     text_color="gray").pack(pady=5)

        ctk.CTkButton(settings_win, text="Reset to Defaults", command=reset_to_default,
                      fg_color="#FF9800", hover_color="#F57C00").pack(pady=10)

    def apply_theme():
        for tab_data in tabs.values():
            editor = tab_data["editor"]
            text_widget = editor._textbox
            editor.configure(font=(editor_font_family, editor_font_size))
            text_widget.tag_configure("current_line", background=highlight_bg)
            if "line_numbers" in tab_data:
                tab_data["line_numbers"].configure(bg=line_bg)
        shell.configure(font=("Consolas", 12))

    # Toolbar
    toolbar = ctk.CTkFrame(root, height=40)
    toolbar.pack(fill="x", padx=5, pady=5)

    button_style = {
        'font': ("Comic Sans MS", 12),
        'corner_radius': 5,
        'border_width': 2,
        'border_spacing': 10
    }

    ctk.CTkButton(toolbar, text="New", command=new_file,
                  fg_color="#FF9800", hover_color="#F57C00", **button_style).pack(side="left", padx=5)
    ctk.CTkButton(toolbar, text="Open", command=load_file,
                  fg_color="#9C27B0", hover_color="#7B1FA2", **button_style).pack(side="left", padx=5)
    ctk.CTkButton(toolbar, text="Save", command=lambda: save_file(notebook.get()),
                  fg_color="#2196F3", hover_color="#1976D2", **button_style).pack(side="left", padx=5)
    ctk.CTkButton(toolbar, text="Close", command=close_file,
                  fg_color="#F44336", hover_color="#D32F2F", **button_style).pack(side="left", padx=5)
    ctk.CTkButton(toolbar, text="Run", command=run_code,
                  fg_color="#4CAF50", hover_color="#388E3C", **button_style).pack(side="left", padx=5)
    ctk.CTkButton(toolbar, text="About", command=show_about,
                  fg_color="#607D8B", hover_color="#455A64", **button_style).pack(side="left", padx=5)

    options_menu = ctk.CTkOptionMenu(toolbar, values=["Gravity ON/OFF", "Upload Library", "Settings"],
                                     command=lambda choice: handle_menu_choice(choice),
                                     fg_color="#FFFFFF", text_color="black",
                                     button_color="#FFFFFF", button_hover_color="#EEEEEE",
                                     font=("Comic Sans MS", 12))
    options_menu.pack(side="right", padx=10)

    def handle_menu_choice(choice):
        if choice == "Gravity ON/OFF":
            toggle_gravity()
        elif choice == "Upload Library":
            upload_library()
        elif choice == "Settings":
            open_settings()

    # Keyboard shortcuts
    root.bind_all("<Control-n>", lambda e: new_file())
    root.bind_all("<Control-o>", lambda e: load_file())
    root.bind_all("<Control-s>", lambda e: save_file())
    root.bind_all("<Control-w>", lambda e: close_file())
    root.bind_all("<F5>", lambda e: run_code())

    # Status bar
    status_var = ctk.StringVar()
    status_var.set("Ready to code!")
    status_bar = ctk.CTkLabel(root, textvariable=status_var, anchor="w",
                              font=("Comic Sans MS", 10))
    status_bar.pack(side="bottom", fill="x")

    # Initial setup
    add_new_tab()

    def on_closing():
        for tab in list(tabs.keys()):
            notebook.set(tab)
            if not check_unsaved_changes(tab):
                return

        pygame_manager.quit_pygame()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    workbench()