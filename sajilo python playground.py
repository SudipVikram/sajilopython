# Sajilo Python Workbench - Ultimate Final Version
# Includes: Syntax Highlighting, Line Highlighting, Session Persistence, Media/Library Manager, Physics Settings, Themes, Autocomplete Prep, Find/Replace, and More

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
from tkinter.font import Font
import subprocess
import tempfile
import sys
import os
import json
import threading
import shutil
import keyword
import re
from PIL import Image, ImageTk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

import re

# 🟠 Define Python syntax patterns
PY_SYNTAX_PATTERNS = {
    "keyword": r"\b(?:def|return|if|else|elif|for|while|import|from|as|class|try|except|finally|with|lambda|yield|assert|break|continue|pass|global|nonlocal|del|raise|in|is|and|or|not)\b",
    "builtin": r"\b(?:print|input|len|range|open|str|int|float|list|dict|set|tuple|type|isinstance|id|sum|map|filter|zip|sorted|min|max|abs|help|dir)\b",
    "special": r"\b(?:self|True|False|None)\b",
    "string": r"(\'[^\']*\'|\"[^\"]*\")",
    "comment": r"#.*",
    "number": r"\b\d+(\.\d+)?\b"
}

CONFIG_FILE = "sajilopython_workbench_config.json"
SESSION_FILE = "last_session.json"
LIBRARY_FOLDER = "libraries"
MEDIA_FOLDER = "media"
FAVICON = "sajilopythonplayground.png"

os.makedirs(LIBRARY_FOLDER, exist_ok=True)
os.makedirs(MEDIA_FOLDER, exist_ok=True)

SYNTAX_THEMES = {
    "Monokai": {
        "keyword": "#F92672",
        "builtin": "#A6E22E",
        "special": "#66D9EF",
        "comment": "#75715E",
        "string": "#E6DB74",
        "number": "#AE81FF"
    },
    "Solarized Light": {
        "keyword": "#268BD2",
        "builtin": "#859900",
        "special": "#D33682",
        "comment": "#93A1A1",
        "string": "#2AA198",
        "number": "#B58900"
    },
    "Solarized Dark": {
        "keyword": "#268BD2",
        "builtin": "#859900",
        "special": "#D33682",
        "comment": "#586E75",
        "string": "#2AA198",
        "number": "#B58900"
    },
    "Pythonic Pastel": {
        "keyword": "#FF6F61",
        "builtin": "#6B5B95",
        "special": "#88B04B",
        "comment": "#B565A7",
        "string": "#88B04B",
        "number": "#009B77"
    },
    "Soft Candy": {
        "keyword": "#FF69B4",
        "builtin": "#FFD700",
        "special": "#ADFF2F",
        "comment": "#CCCCCC",
        "string": "#FFB6C1",
        "number": "#00CED1"
    },
    "Dracula": {
        "keyword": "#FF79C6",
        "builtin": "#8BE9FD",
        "special": "#BD93F9",
        "comment": "#6272A4",
        "string": "#F1FA8C",
        "number": "#BD93F9"
    },
    "Gruvbox Dark": {
        "keyword": "#FB4934",
        "builtin": "#FABD2F",
        "special": "#83A598",
        "comment": "#928374",
        "string": "#B8BB26",
        "number": "#D3869B"
    },
    "Gruvbox Light": {
        "keyword": "#9D0006",
        "builtin": "#AF3A03",
        "special": "#427B58",
        "comment": "#7C6F64",
        "string": "#79740E",
        "number": "#B57614"
    },
    "Atom One Dark": {
        "keyword": "#C678DD",
        "builtin": "#61AFEF",
        "special": "#E06C75",
        "comment": "#5C6370",
        "string": "#98C379",
        "number": "#D19A66"
    },
    "Nord": {
        "keyword": "#81A1C1",
        "builtin": "#8FBCBB",
        "special": "#88C0D0",
        "comment": "#4C566A",
        "string": "#A3BE8C",
        "number": "#B48EAD"
    },
    "Night Owl": {
        "keyword": "#C792EA",
        "builtin": "#82AAFF",
        "special": "#F78C6C",
        "comment": "#5F7E97",
        "string": "#C3E88D",
        "number": "#F78C6C"
    },
    "Oceanic Next": {
        "keyword": "#6699CC",
        "builtin": "#C594C5",
        "special": "#5FB3B3",
        "comment": "#65737E",
        "string": "#99C794",
        "number": "#F99157"
    },
    "Tomorrow Light": {
        "keyword": "#8959A8",
        "builtin": "#4271AE",
        "special": "#3E999F",
        "comment": "#8E908C",
        "string": "#718C00",
        "number": "#C82829"
    },
    "Tomorrow Night": {
        "keyword": "#C397D8",
        "builtin": "#729FCF",
        "special": "#34E2E2",
        "comment": "#999999",
        "string": "#8AE234",
        "number": "#EF2929"
    },
    "Watermelon Pop": {
        "keyword": "#FF4D6D",
        "builtin": "#6A4C93",
        "special": "#FFB997",
        "comment": "#AAAAAA",
        "string": "#A1C181",
        "number": "#FF99C8"
    }
}

PYTHON_KEYWORDS = [
    "def", "return", "if", "elif", "else", "for", "while", "break", "continue", "pass", "import", "from", "as",
    "class", "try", "except", "finally", "with", "lambda", "yield", "assert", "global", "nonlocal", "del", "raise",
    "True", "False", "None", "print", "len", "input", "open", "range", "list", "dict", "set", "tuple", "str", "int",
    "float", "bool", "sum", "map", "filter", "zip", "sorted", "min", "max", "abs", "help", "dir", "type", "isinstance", "id"
]

def toggle_suggestions():
    current_state = config.get("suggestions_enabled", True)
    config["suggestions_enabled"] = not current_state
    save_config(config)
    status = "enabled" if config["suggestions_enabled"] else "disabled"
    update_status(f"💡 Code suggestions {status}")


def center_and_resize_window(win, default_width=900, default_height=700, margin=50):
    win.update_idletasks()

    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()

    # Adjust height if screen is smaller than default window height
    final_width = min(default_width, screen_width - margin)
    final_height = min(default_height, screen_height - margin)

    x = (screen_width // 2) - (final_width // 2)
    y = (screen_height // 2) - (final_height // 2)

    win.geometry(f"{final_width}x{final_height}+{x}+{y}")


# Add interpreter check at startup
def check_interpreter():
    interpreter = config.get("default_interpreter", None)
    if not interpreter or not os.path.exists(interpreter):
        run_btn.config(state="disabled")
        messagebox.showwarning("Interpreter Not Set", "Please select a valid Python interpreter from Settings > Interpreter.")
        open_interpreter_settings()
    else:
        run_btn.config(state="normal")

# Interpreter selection function
def apply_selected_interpreter(selected_path):
    config["default_interpreter"] = selected_path
    save_config(config)
    check_interpreter()

# Interpreter settings dialog
def open_interpreter_settings():
    dialog = tk.Toplevel(root)
    dialog.title("Select Python Interpreter")
    dialog.grab_set()
    dialog.transient(root)

    tk.Label(dialog, text="Select your Python Interpreter:").pack(pady=10)

    def browse_interpreter():
        path = filedialog.askopenfilename(filetypes=[("Python Executable", "python.exe")])
        if path:
            apply_selected_interpreter(path)
            dialog.destroy()

    tk.Button(dialog, text="Browse", command=browse_interpreter).pack(pady=5)
    tk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=5)

def center_window(win, width=900, height=700):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    win.geometry(f"{width}x{height}+{x}+{y}")


def set_dialog_icon(dialog):
    """
    Sets the icon of the given dialog window to match the main favicon.
    """
    try:
        dialog.iconphoto(False, tk.PhotoImage(file="sajilopythonplayground.png"))
    except Exception as e:
        print(f"Failed to set dialog icon: {e}")

def get_current_word(editor):
    try:
        index = editor.index("insert")
        line_start = editor.index(f"{index} linestart")
        text_line = editor.get(line_start, index)

        # Check for object.method pattern
        object_match = re.search(r"(\w+)\.$", text_line.strip())
        if object_match:
            return object_match.group(1)  # Return the object name (e.g., "oc")

        # Fallback: get last word if not in object.method form
        word = re.split(r'\W+', text_line)[-1]
        return word
    except tk.TclError:
        return ""

def update_status(message):
    status_lbl.config(text=message)
    status_lbl.after(3000, lambda: status_lbl.config(text="Ready"))  # Clears message after 3 secondsup

def update_suggestions(event=None):
    tab = notebook.select()
    editor = editors.get(str(tab), {}).get("editor")
    if not editor:
        return

    if not config.get("suggestions_enabled", True):
        suggestion_lbl.config(text="Code Suggestions: Disabled")
        return

    update_object_map(editor)
    current_object, prefix = detect_current_object_and_prefix(editor)

    if current_object and current_object in object_map:
        class_name = object_map[current_object]
        methods, properties = get_class_members(class_name)
        combined = methods + properties
        suggestions = [m for m in combined if m.startswith(prefix)]
        suggestion_lbl.config(
            text="Methods/Properties: " + ", ".join(suggestions[:5]) + ("..." if len(suggestions) > 5 else ""),
            font=("Arial", 10),
            foreground="green"
        )

    else:
        word = get_current_word(editor)
        if not word:
            suggestion_lbl.config(text="Code Suggestions: ")
            return

        class_suggestions = [cls for cls in get_classes_from_libraries() if word.lower() in cls.lower()]
        keyword_suggestions = [kw for kw in PYTHON_KEYWORDS if word.lower() in kw.lower()]
        suggestions = class_suggestions + keyword_suggestions

        if suggestions:
            suggestion_lbl.config(
                text="Code Suggestions: " + ", ".join(suggestions[:5]) + ("..." if len(suggestions) > 5 else ""),
                foreground="green"
            )
        else:
            suggestion_lbl.config(text="Code Suggestions: None")


def get_functions_from_libraries():
    function_names = []
    if not os.path.exists(LIBRARY_FOLDER):
        return function_names  # Return empty if folder doesn't exist
    for fname in os.listdir(LIBRARY_FOLDER):
        if fname.endswith(".py"):
            fpath = os.path.join(LIBRARY_FOLDER, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                # Extract functions with regex
                functions = re.findall(r"^\s*def\s+([a-zA-Z_]\w*)\s*\(", content, re.MULTILINE)
                function_names.extend(functions)
            except Exception as e:
                print(f"Error reading {fname}: {e}")
    return function_names

library_function_cache = []

def cache_library_functions():
    global library_function_cache
    library_function_cache.clear()

    if not os.path.exists(LIBRARY_FOLDER):
        return

    for fname in os.listdir(LIBRARY_FOLDER):
        if fname.endswith(".py"):
            fpath = os.path.join(LIBRARY_FOLDER, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                # Extract function names using regex
                functions = re.findall(r"^\s*def\s+([a-zA-Z_]\w*)\s*\(", content, re.MULTILINE)
                library_function_cache.extend(functions)
            except Exception as e:
                print(f"Error reading {fname}: {e}")

def get_functions_from_libraries():
    return library_function_cache

cache_library_functions()

import re

object_map = {}

def update_object_map(editor):
    code = editor.get("1.0", "end")
    object_map.clear()
    # Find lines like: oc = sajilocv()
    matches = re.findall(r"(\w+)\s*=\s*(\w+)\s*\(", code)
    for var, cls in matches:
        object_map[var] = cls


def detect_current_object_and_prefix(editor):
    """
    Detects object name before the dot and the prefix being typed after the dot.
    Example: oc.roam_ → returns ("oc", "roam_")
    """
    line_start = editor.index("insert linestart")
    current_line = editor.get(line_start, "insert")
    match = re.search(r"(\w+)\.(\w*)$", current_line.strip())
    if match:
        return match.group(1), match.group(2)
    return None, None



def get_classes_from_libraries():
    """
    Returns a list of class names defined inside all .py files within LIBRARY_FOLDER.
    """
    class_names = []
    if not os.path.exists(LIBRARY_FOLDER):
        return class_names

    for fname in os.listdir(LIBRARY_FOLDER):
        if fname.endswith(".py"):
            fpath = os.path.join(LIBRARY_FOLDER, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                classes = re.findall(r"^\s*class\s+([a-zA-Z_]\w*)\s*(\(|:)", content, re.MULTILINE)
                class_names.extend([cls[0] for cls in classes])
            except Exception as e:
                print(f"Error reading {fname}: {e}")
    return class_names



def get_class_methods(class_name):
    methods = []
    for fname in os.listdir(LIBRARY_FOLDER):
        if fname.endswith(".py"):
            with open(os.path.join(LIBRARY_FOLDER, fname), "r", encoding="utf-8") as f:
                content = f.read()
            # Look for class and its methods
            class_block = re.search(rf"class\s+{class_name}\s*.*?:((?:\n\s+.+)+)", content)
            if class_block:
                methods += re.findall(r"\n\s+def\s+(\w+)\s*\(", class_block.group(1))
    return methods


def get_class_members(class_name):
    """
    Extract method names with parameters and class properties (variables)
    from a class inside the libraries folder.
    """
    methods = []
    properties = []

    if not os.path.exists(LIBRARY_FOLDER):
        return methods, properties

    for fname in os.listdir(LIBRARY_FOLDER):
        if fname.endswith(".py"):
            fpath = os.path.join(LIBRARY_FOLDER, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract the full class block more reliably
                class_pattern = rf"class\s+{class_name}\s*(\(|:)[\s\S]*?(?=\nclass\s|\Z)"
                class_blocks = re.findall(class_pattern, content, re.MULTILINE)

                # Process each block
                for class_block in class_blocks:
                    # Method detection with parameters
                    method_matches = re.findall(r"^\s+def\s+([a-zA-Z_]\w*)\s*\((.*?)\):", content, re.MULTILINE)
                    for method, params in method_matches:
                        full_signature = f"{method}({params})"
                        methods.append(full_signature)

                    # Property detection
                    properties += re.findall(r"self\.(\w+)\s*=", content)
            except Exception as e:
                print(f"Error reading {fname}: {e}")

    return methods, properties



# --- Load config ---
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"theme": "flatly", "syntax_theme": "Monokai", "default_interpreter": sys.executable, "physics": {"enabled": False, "gravity": False, "wall": False, "collision": False, "boundary": False}}

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=4)

config = load_config()

# --- Main Window ---
root = tb.Window(themename=config.get("theme", "flatly"))
root.title("Sajilo Python Playground")
center_window(root, width=900, height=700)  # Adjust width and height if needed
root.geometry("1000x810")
try:
    root.iconphoto(False, tk.PhotoImage(file=FAVICON))
except:
    pass

editors = {}
unsaved_tabs = set()
previous_process = None
kill_requested = False
output_thread = None

# --- UI Layout ---
toolbar = tb.Frame(root)
toolbar.pack(fill=tk.X, padx=10, pady=5)
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=10)
output = tk.Text(root, height=6, bg='black', fg='light green', font=('Consolas', 11))
output.pack(fill=tk.BOTH, padx=10, pady=5)
physics_state_label = tb.Label(root, text="")
physics_state_label.pack(fill=tk.X, padx=10)
bottom_bar = tb.Frame(root)
bottom_bar.pack(fill=tk.X, padx=10, pady=10)
run_btn = tb.Button(bottom_bar, text="▶️ Run", bootstyle=DANGER)
run_btn.pack(side=tk.LEFT)
status_lbl = tb.Label(bottom_bar, text="💡 Write your code and press Run.")
status_lbl.pack(side=tk.LEFT, padx=10)
suggestion_lbl = tb.Label(bottom_bar, text="Code Suggestions: ", anchor="w")
suggestion_lbl.pack(side=tk.LEFT, padx=5)
settings_menu = tk.Menu(root, tearoff=0)
settings_btn = tb.Menubutton(bottom_bar, text="⚙️ Settings", bootstyle=PRIMARY, menu=settings_menu)
settings_btn.pack(side=tk.RIGHT)

# --- Python Keywords, Built-ins and Patterns ---
KEYWORDS = keyword.kwlist
BUILTINS = dir(__builtins__)
SYNTAX_MAP = {
    "keyword": KEYWORDS,
    "builtin": BUILTINS,
    "special": ["print", "input"]
}

# Call this at the end of your setup, after all widgets including run_btn are initialized
check_interpreter()

# --- Editor Tab ---
def create_editor_tab(code="", filepath=None):
    frame = tk.Frame(notebook)
    line_numbers = tk.Text(frame, width=5, padx=4, takefocus=0, border=0, background='#f0f0f0', state='disabled')
    line_numbers.pack(side="left", fill="y")
    text_frame = tk.Frame(frame)
    text_frame.pack(side="right", fill="both", expand=True)
    # ✅ Create the editor WITHOUT expand initially
    editor = tk.Text(
        text_frame, wrap="none", font=("Consolas", 12), undo=True,
        tabs=(Font(font=("Consolas", 12)).measure('    '),)
    )
    # ✅ Create the editor WITHOUT expand initially
    editor = tk.Text(
        text_frame, wrap="none", font=("Consolas", 12), undo=True,
        tabs=(Font(font=("Consolas", 12)).measure('    '),)
    )
    editor.pack(fill="both", side="left", expand=True)
    editor.config(height=21)  # You can adjust '20' to reduce or increase the height (lines of text)
    vscroll = tk.Scrollbar(text_frame, command=editor.yview)
    vscroll.pack(side="right", fill="y")

    hscroll = tk.Scrollbar(text_frame, orient="horizontal", command=editor.xview)
    hscroll.pack(side="bottom", fill="x")
    editor.configure(xscrollcommand=hscroll.set)

    # ✅ Ensure cursor is visible when pressing Enter near the bottom
    def ensure_cursor_visible(event=None):
        editor.see("insert")

    editor.bind("<Return>", ensure_cursor_visible)
    editor.bind("<<Paste>>", ensure_cursor_visible)

    editor.configure(yscrollcommand=lambda *args: (vscroll.set(*args), line_numbers.yview_moveto(args[0])))
    line_numbers.configure(yscrollcommand=vscroll.set)

    # Throttled line number update
    def update_line_numbers():
        line_numbers.config(state='normal')
        line_numbers.delete("1.0", "end")
        total_lines = editor.index('end-1c').split('.')[0]
        line_numbers_text = "\n".join(str(i) for i in range(1, int(total_lines) + 1))
        line_numbers.insert("1.0", line_numbers_text)
        line_numbers.config(state='disabled')

    def schedule_line_number_update(event=None):
        if hasattr(editor, 'line_number_update_id'):
            editor.after_cancel(editor.line_number_update_id)
        editor.line_number_update_id = editor.after(150, update_line_numbers)  # 150ms delay

    # Bind throttled update instead of direct update
    editor.bind("<KeyRelease>", schedule_line_number_update)

    def highlight(event=None):
        editor.tag_remove("keyword", "1.0", "end")
        editor.tag_remove("builtin", "1.0", "end")
        editor.tag_remove("special", "1.0", "end")
        for match in re.finditer(r"\b\w+\b", editor.get("1.0", "end")):
            word = match.group(0)
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            if word in SYNTAX_MAP["keyword"]:
                editor.tag_add("keyword", start, end)
            elif word in SYNTAX_MAP["builtin"]:
                editor.tag_add("builtin", start, end)
            elif word in SYNTAX_MAP["special"]:
                editor.tag_add("special", start, end)
        theme_colors = SYNTAX_THEMES.get(config.get("syntax_theme", "Monokai"), {})

        for token, color in theme_colors.items():
            editor.tag_config(token, foreground=color)

    def update_lines(event=None):
        lines = editor.get("1.0", "end").split("\n")
        line_numbers.configure(state="normal")
        line_numbers.delete("1.0", "end")
        line_numbers.insert("1.0", "\n".join(str(i + 1) for i in range(len(lines))))
        line_numbers.configure(state="disabled")

    def auto_indent(event):
        current = editor.get("insert linestart", "insert")
        match = re.match(r"^\s*", current)
        indent = match.group(0) if match else ""
        editor.insert("insert", f"\n{indent}")
        return "break"

    def highlight_line(event=None):
        editor.tag_remove("active_line", "1.0", "end")
        editor.tag_add("active_line", "insert linestart", "insert lineend+1c")
        editor.tag_config("active_line", background="#e9efff")

    def handle_paste(event=None):
        try:
            editor.config(undo=False)
            editor.insert(tk.INSERT, root.clipboard_get())
        except Exception as e:
            print(f"Paste Error: {e}")
        finally:
            editor.config(undo=True)
        schedule_line_number_update()
        return "break"  # Prevent double pasting

    editor.bind("<<Paste>>", handle_paste)

    editor.bind("<KeyRelease>", lambda e: (highlight(), update_lines(), highlight_line(), mark_unsaved(notebook.select())))
    editor.bind("<ButtonRelease>", highlight_line)
    editor.bind("<KeyRelease>", update_suggestions, add='+')
    editor.bind("<ButtonRelease>", update_suggestions, add='+')
    editor.bind("<Return>", auto_indent)
    editor.insert("1.0", code)
    highlight()
    update_lines()
    highlight_line()

    tab_name = os.path.basename(filepath) if filepath else "Untitled"
    notebook.add(frame, text=tab_name)
    notebook.select(frame)
    editors[str(frame)] = {"editor": editor, "file": filepath, "frame": frame}

# --- Autoload & Save Session ---
def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            paths = json.load(f)
        for path in paths:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                create_editor_tab(content, path)
            except:
                continue

def save_session():
    paths = [data["file"] for data in editors.values() if data["file"]]
    with open(SESSION_FILE, "w") as f:
        json.dump(paths, f)

# --- Media & Library Manager ---
def open_media_manager():
    root.attributes('-disabled', True)
    dialog = tb.Toplevel(root)
    dialog.title("Media Manager")
    dialog.grab_set()
    dialog.transient(root)
    dialog.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (600 // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (400 // 2)
    dialog.geometry(f"800x500+{x}+{y}")
    set_dialog_icon(dialog)

    canvas = tk.Canvas(dialog)
    scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
    scroll_frame = ttk.Frame(canvas)
    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def refresh():
        for widget in scroll_frame.winfo_children():
            widget.destroy()
        row = col = 0
        audio_row = col_audio = 0

        for fname in sorted(os.listdir(MEDIA_FOLDER)):
            fpath = os.path.join(MEDIA_FOLDER, fname)
            if fname.lower().endswith((".png", ".jpg", ".gif")):
                frame = tb.Frame(scroll_frame, relief="ridge", borderwidth=1)
                frame.grid(row=row, column=col, padx=8, pady=8, sticky="n")
                try:
                    img = Image.open(fpath)
                    img.thumbnail((64, 64))
                    thumb = ImageTk.PhotoImage(img)
                    img_lbl = tk.Label(frame, image=thumb)
                    img_lbl.image = thumb
                    img_lbl.pack()
                except:
                    tb.Label(frame, text="[Error loading image]").pack()
                tb.Label(frame, text=fname, font=("Arial", 8)).pack(pady=2)
                tb.Button(frame, text="Delete", bootstyle=DANGER, command=lambda f=fpath: (os.remove(f), refresh())).pack(pady=2)
                col += 1
                if col > 4:
                    col = 0
                    row += 1

        audio_label = tb.Label(scroll_frame, text="🎵 Audio Files", font=("Arial", 10, "bold"))
        audio_label.grid(row=row + 1, column=0, columnspan=5, pady=(20, 5), sticky="w")
        for fname in sorted(os.listdir(MEDIA_FOLDER)):
            if fname.lower().endswith((".mp3", ".wav")):
                fpath = os.path.join(MEDIA_FOLDER, fname)
                frame = tb.Frame(scroll_frame, relief="ridge", borderwidth=1)
                frame.grid(row=row + 2 + audio_row, column=col_audio, padx=8, pady=8, sticky="n")
                tb.Label(frame, text=fname, font=("Arial", 9)).pack(pady=(4, 2))
                tb.Button(frame, text="Delete", bootstyle=DANGER, command=lambda f=fpath: (os.remove(f), refresh())).pack(pady=2)
                col_audio += 1
                if col_audio > 4:
                    col_audio = 0
                    audio_row += 1

    def upload():
        files = filedialog.askopenfilenames(filetypes=[("Media Files", ".png .jpg .gif .mp3 .wav")])
        for f in files:
            shutil.copy(f, os.path.join(MEDIA_FOLDER, os.path.basename(f)))
        refresh()
        cache_library_functions()

    upload_frame = tb.Frame(scroll_frame)
    upload_frame.grid(row=0, column=0, columnspan=5, pady=(10, 5), sticky="w")
    tb.Button(upload_frame, text="Upload Media", command=upload, bootstyle=INFO).pack(anchor="w")
    refresh()

    upload_frame = tb.Frame(scroll_frame)
    upload_frame.grid(row=999, column=0, columnspan=5, pady=(10, 5), sticky="w")
    tb.Button(upload_frame, text="Upload Media", command=upload, bootstyle=INFO).pack(anchor="w")

    dialog.protocol("WM_DELETE_WINDOW", lambda: (root.attributes('-disabled', False), dialog.destroy()))

# ✅ Function to extract metadata from triple-quoted comments
def extract_library_metadata(fpath):
    meta = {'Author': '', 'Version': '', 'About': ''}
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(r"(?:'''|\"\"\")(.*?)(?:'''|\"\"\")", content, re.DOTALL)
        if match:
            comment_block = match.group(1)
            for line in comment_block.splitlines():
                if line.strip().startswith("Author:"):
                    meta['Author'] = line.split(":", 1)[1].strip()
                elif line.strip().startswith("Version:"):
                    meta['Version'] = line.split(":", 1)[1].strip()
                elif line.strip().startswith("About:"):
                    meta['About'] = line.split(":", 1)[1].strip()
    except Exception as e:
        print(f"Error reading metadata from {fpath}: {e}")
    return meta

# ✅ Open Library Manager function
def open_library_manager():
    root.attributes('-disabled', True)
    dialog = tk.Toplevel(root)
    dialog.title("Library Manager")
    dialog.grab_set()
    dialog.transient(root)
    dialog.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (600 // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (400 // 2)
    dialog.geometry(f"600x400+{x}+{y}")
    set_dialog_icon(dialog)

    frame = tk.Frame(dialog)
    frame.pack(fill="both", expand=True)

    def refresh():
        for widget in frame.winfo_children():
            widget.destroy()
        for fname in os.listdir(LIBRARY_FOLDER):
            fpath = os.path.join(LIBRARY_FOLDER, fname)
            meta = extract_library_metadata(fpath)
            row = tk.Frame(frame)
            row.pack(fill="x", padx=5, pady=2)
            tk.Label(row, text=fname, width=25).pack(side="left")
            tk.Label(row, text=f"Author: {meta['Author']}  Version: {meta['Version']}  About: {meta['About']}").pack(side="left")
            tk.Button(row, text="Delete", command=lambda f=fpath: (os.remove(f), refresh())).pack(side="right")

    def upload():
        file = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file:
            shutil.copy(file, os.path.join(LIBRARY_FOLDER, os.path.basename(file)))
            refresh()

    tk.Button(dialog, text="Upload Library", command=upload).pack(pady=5)
    refresh()
    dialog.protocol("WM_DELETE_WINDOW", lambda: (root.attributes('-disabled', False), dialog.destroy()))

# --- Toolbar Actions ---
def new_tab():
    create_editor_tab()
    update_status("🆕 New Tab Created")
    tab = notebook.select()
    editor = editors.get(str(tab), {}).get("editor")
    if editor:
        editor.mark_set("insert", "1.0")
        editor.focus()


def open_file():
    filepath = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
    if filepath:
        with open(filepath, "r", encoding="utf-8") as f:
            create_editor_tab(f.read(), filepath)

def save_file():
    tab = notebook.select()
    data = editors.get(str(tab))
    if not data: return
    filepath = data["file"]
    if not filepath:
        filepath = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")])
        if not filepath: return
        data["file"] = filepath
        notebook.tab(tab, text=os.path.basename(filepath))
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(data["editor"].get("1.0", "end"))
        update_status("✅ File Saved Successfully")

def close_tab():
    tab = notebook.select()
    if tab:
        editors.pop(str(tab), None)
        notebook.forget(tab)
        update_status("❎ Tab Closed")

def copy_code():
    tab = notebook.select()
    editor = editors.get(str(tab), {}).get("editor")
    if not editor:
        return
    try:
        editor.event_generate("<<Copy>>")
        update_status("📋 Code Copied")
    except Exception as e:
        update_status(f"Error copying: {e}")

def paste_code():
    tab = notebook.select()
    editor = editors.get(str(tab), {}).get("editor")
    if not editor:
        return
    try:
        editor.insert(tk.INSERT, root.clipboard_get())  # Paste only what's in clipboard
        update_status("📌 Code Pasted")
    except Exception as e:
        update_status(f"Paste Error: {e}")

def undo_code():
    tab = notebook.select()
    editor = editors.get(str(tab), {}).get("editor")
    if not editor:
        return
    try:
        editor.event_generate("<<Undo>>")
        update_status("↩️ Undo Performed")
    except Exception as e:
        update_status(f"Error undoing: {e}")

def redo_code():
    tab = notebook.select()
    editor = editors.get(str(tab), {}).get("editor")
    if not editor:
        return
    try:
        editor.event_generate("<<Redo>>")
        update_status("➡️ Redo Performed")
    except Exception as e:
        update_status(f"Error redoing: {e}")


def find_and_replace():
    tab = notebook.select()
    editor = editors.get(str(tab), {}).get("editor")
    if not editor:
        return

    dialog = tb.Toplevel(root)
    dialog.title("Find and Replace")
    dialog.geometry("400x180")
    dialog.grab_set()
    dialog.transient(root)
    x = root.winfo_x() + (root.winfo_width() // 2) - 200
    y = root.winfo_y() + (root.winfo_height() // 2) - 60
    dialog.geometry(f"400x180+{x}+{y}")
    set_dialog_icon(dialog)

    find_var = tk.StringVar()
    replace_var = tk.StringVar()

    def do_highlight(*_):
        editor.tag_remove("highlight", "1.0", "end")
        term = find_var.get()
        if not term:
            return
        start = "1.0"
        while True:
            start = editor.search(term, start, stopindex="end")
            if not start:
                break
            end = f"{start}+{len(term)}c"
            editor.tag_add("highlight", start, end)
            start = end
        editor.tag_config("highlight", background="yellow", foreground="black")

    def do_replace():
        find_text = find_var.get()
        replace_text = replace_var.get()
        if find_text:
            content = editor.get("1.0", "end")
            editor.delete("1.0", "end")
            editor.insert("1.0", content.replace(find_text, replace_text))
            do_highlight()

    tb.Label(dialog, text="Find:").pack(pady=2)
    tb.Entry(dialog, textvariable=find_var).pack(fill="x", padx=10)
    tb.Label(dialog, text="Replace with:").pack(pady=2)
    tb.Entry(dialog, textvariable=replace_var).pack(fill="x", padx=10)
    tb.Button(dialog, text="Replace", command=do_replace, bootstyle=SUCCESS).pack(pady=5)

    find_var.trace_add("write", do_highlight)
    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)

# --- Settings ---
def update_physics_status():
    physics = config.get("physics", {})
    enabled_flags = [k for k, v in physics.items() if v]
    if enabled_flags:
        physics_state_label.config(text="Physics: " + ", ".join([k.capitalize() for k in enabled_flags]), bootstyle=SUCCESS)
    else:
        physics_state_label.config(text="Physics: Disabled", bootstyle=SECONDARY)

def open_physics_settings():
    root.attributes('-disabled', True)
    dialog = tb.Toplevel(root)
    dialog.title("Physics Engine Settings")
    dialog.grab_set()
    dialog.transient(root)
    dialog.resizable(False, False)
    dialog.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (400 // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (350 // 2)
    dialog.geometry(f"400x350+{x}+{y}")
    set_dialog_icon(dialog)

    physics = config.get("physics", {})
    vars = {
        "gravity": tk.BooleanVar(value=physics.get("gravity", False)),
        "wall": tk.BooleanVar(value=physics.get("wall", False)),
        "collision": tk.BooleanVar(value=physics.get("collision", False)),
        "boundary": tk.BooleanVar(value=physics.get("boundary", False))
    }
    content = tb.Frame(dialog)
    content.pack(padx=20, pady=10, fill='x')
    for key, var in vars.items():
        tb.Checkbutton(content, text=key.capitalize(), variable=var, bootstyle="round-toggle").pack(anchor="w", pady=4)

    def save():
        config["physics"] = {k: v.get() for k, v in vars.items()}
        save_config(config)
        update_physics_status()
        root.attributes('-disabled', False)
        dialog.destroy()
        root.attributes('-disabled', False)

    tb.Button(dialog, text="Save", command=save, bootstyle=SUCCESS).pack(pady=10)
    dialog.protocol("WM_DELETE_WINDOW", lambda: (root.attributes('-disabled', False), dialog.destroy()))


def highlight_editor(editor):
    editor.tag_remove("keyword", "1.0", "end")
    editor.tag_remove("builtin", "1.0", "end")
    editor.tag_remove("special", "1.0", "end")
    editor.tag_remove("comment", "1.0", "end")
    editor.tag_remove("string", "1.0", "end")
    editor.tag_remove("number", "1.0", "end")

    theme = SYNTAX_THEMES.get(config.get("syntax_theme", "Monokai"), {})
    text = editor.get("1.0", "end-1c")
    for token, pattern in PY_SYNTAX_PATTERNS.items():
        for match in re.finditer(pattern, text):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            editor.tag_add(token, start, end)

    for token, color in theme.items():
        editor.tag_config(token, foreground=color)


def open_theme_settings():
    root.attributes('-disabled', True)
    dialog = tb.Toplevel(root)
    dialog.title("Theme Settings")
    dialog.grab_set()
    dialog.transient(root)
    dialog.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (300 // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (160 // 2)
    dialog.geometry(f"300x240+{x}+{y}")
    set_dialog_icon(dialog)

    current_theme = root.style.theme_use()
    theme_var = tk.StringVar(value=current_theme)

    # --- Syntax Theme Change Handler ---
    def on_syntax_theme_change(new_theme):
        config["syntax_theme"] = new_theme
        save_config(config)
        for data in editors.values():
            highlight_editor(data["editor"])  # NEW FUNCTION to call manually

    # --- GUI elements ---
    tb.Label(dialog, text="🎨 Syntax Highlight Theme:").pack(pady=(10, 2))

    syntax_theme_var = tk.StringVar(value=config.get("syntax_theme", "Monokai"))
    theme_dropdown = ttk.OptionMenu(dialog, syntax_theme_var, syntax_theme_var.get(), *SYNTAX_THEMES.keys(),
                                    command=on_syntax_theme_change)
    theme_dropdown.pack(pady=5)

    tb.Label(dialog, text="🎨 Select Editor Theme:").pack(pady=10)

    def on_syntax_theme_change(new_theme):
        config["syntax_theme"] = new_theme
        save_config(config)
        for data in editors.values():
            data["editor"].event_generate("<KeyRelease>")  # Refresh highlighting

    def on_theme_change(new_theme):
        root.style.theme_use(new_theme)
        config["theme"] = new_theme
        save_config(config)

    theme_dropdown = ttk.OptionMenu(dialog, theme_var, current_theme, *root.style.theme_names(), command=on_theme_change)
    theme_dropdown.pack(pady=5)

    # Handle dialog close from [X] button
    dialog.protocol("WM_DELETE_WINDOW", lambda: (root.attributes('-disabled', False), dialog.destroy()))

def apply_theme(theme):
    root.style.theme_use(theme)
    config["theme"] = theme
    save_config(config)

def find_python_interpreters():
    possible_names = ["python", "python3", "python3.11", "python3.10", "python3.9", "python3.8"]
    interpreters = []
    for name in possible_names:
        path = shutil.which(name)
        if path and path not in interpreters:
            interpreters.append(path)
    # Add previously saved custom interpreters from config
    extra = config.get("custom_interpreters", [])
    for item in extra:
        if item not in interpreters:
            interpreters.append(item)
    return interpreters if interpreters else [sys.executable]

def open_about_dialog():
    root.attributes('-disabled', True)
    dialog = tb.Toplevel(root)
    dialog.title("About Sajilo Python Playground")
    dialog.geometry("400x200")
    dialog.grab_set()
    dialog.transient(root)
    dialog.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (400 // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (200 // 2)
    dialog.geometry(f"400x200+{x}+{y}")
    set_dialog_icon(dialog)

    tb.Label(dialog, text="Sajilo Python Playground", font=("Helvetica", 16, "bold")).pack(pady=10)
    tb.Label(dialog, text="Made with ❤️ at Beyond Apogee\n                   Version 0.1").pack()
    tb.Button(dialog, text="Close", command=lambda: (root.attributes('-disabled', False), dialog.destroy()), bootstyle=SECONDARY).pack(pady=15)
    dialog.protocol("WM_DELETE_WINDOW", lambda: (root.attributes('-disabled', False), dialog.destroy()))

def open_interpreter_settings():
    root.attributes('-disabled', True)
    dialog = tb.Toplevel(root)
    dialog.title("Python Interpreter Settings")
    dialog.grab_set()
    dialog.transient(root)
    dialog.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (400 // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (300 // 2)
    dialog.geometry(f"400x300+{x}+{y}")
    set_dialog_icon(dialog)

    interpreters = find_python_interpreters()
    interpreter_var = tk.StringVar(value=config.get("default_interpreter", sys.executable))

    tb.Label(dialog, text="Select Python Interpreter:").pack(pady=10)
    dropdown = ttk.OptionMenu(dialog, interpreter_var, interpreter_var.get(), *interpreters)
    dropdown.pack(pady=5)

    def add_custom_interpreter():
        path = filedialog.askopenfilename(title="Select Python Interpreter", filetypes=[("Python Executable", "python*")])
        if path:
            # Save the new interpreter to config under 'custom_interpreters'
            custom = config.get("custom_interpreters", [])
            if path not in custom:
                custom.append(path)
                config["custom_interpreters"] = custom
                save_config(config)
            dialog.destroy()  # Restart the dialog to refresh the list
            open_interpreter_settings()

    tb.Button(dialog, text="➕ Add Python Path", command=add_custom_interpreter, bootstyle=INFO).pack(pady=5)

    def apply_change():
        config["default_interpreter"] = interpreter_var.get()
        save_config(config)
        messagebox.showinfo("Interpreter Changed", f"Python interpreter set to:\n{config['default_interpreter']}")
        root.attributes('-disabled', False)  # ENABLE FIRST
        dialog.destroy()  # THEN DESTROY THE DIALOG

    tb.Button(dialog, text="Apply", command=apply_change, bootstyle=SUCCESS).pack(pady=10)
    dialog.protocol("WM_DELETE_WINDOW", lambda: (root.attributes('-disabled', False), dialog.destroy()))

# --- Run Button ---
def run_code():
    global previous_process, kill_requested

    interpreter = config.get("default_interpreter", None)
    if not interpreter or not os.path.exists(interpreter):
        update_status("❌ No valid Python interpreter selected.")
        messagebox.showerror("Interpreter Not Set", "Please select a valid Python interpreter from Settings > Interpreter before running code.")
        run_btn.config(state="disabled")
        open_interpreter_settings()
        return

    tab = notebook.select()
    editor = editors.get(str(tab), {}).get("editor")
    if not editor:
        return
    code = editor.get("1.0", "end")
    output.config(state="normal")
    output.delete("1.0", "end")
    output.insert("end", "Running your code...\n")
    output.config(state="disabled")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as f:
        f.write(code)
        path = f.name

    kill_requested = False
    interpreter = config.get("default_interpreter", sys.executable)


    CREATE_NO_WINDOW = 0x08000000
    proc = subprocess.Popen([interpreter, path], creationflags=CREATE_NO_WINDOW, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    previous_process = proc

    def stream():
        for line in proc.stdout:
            if kill_requested:
                break
            output.config(state="normal")
            output.insert("end", line.decode())
            output.see("end")
            output.config(state="disabled")
        proc.wait()
        os.unlink(path)
        if not kill_requested:
            run_btn.config(text="▶️ Run", bootstyle=DANGER, command=run_code)

    run_btn.config(text="❌ Kill", bootstyle=WARNING, command=kill_process)
    threading.Thread(target=stream, daemon=True).start()

def kill_process():
    global previous_process, kill_requested
    kill_requested = True
    if previous_process and previous_process.poll() is None:
        try:
            previous_process.kill()
            output.config(state=tk.NORMAL)
            output.insert(tk.END, "\n❌ Process was killed.\n")
            output.config(state=tk.DISABLED)
            status_lbl.config(text="❌ Process killed.")
        except Exception as e:
            output.config(state=tk.NORMAL)
            output.insert(tk.END, f"\n❌ Error killing process: {e}\n")
            output.config(state=tk.DISABLED)
    run_btn.config(text="▶️ Run", bootstyle=DANGER, command=run_code)
    previous_process = None


run_btn.config(command=run_code)

def mark_unsaved(tab_id):
    if not tab_id:
        return
    if tab_id not in unsaved_tabs:
        tab_text = notebook.tab(tab_id, "text")
        if not tab_text.startswith("*"):
            notebook.tab(tab_id, text="*" + tab_text)
        unsaved_tabs.add(tab_id)

# ✅ Handle Save Confirmation on Exit

def confirm_on_exit():
    unsaved = list(unsaved_tabs)
    if unsaved:
        # Create a custom dialog box for confirmation
        confirm_dialog = tb.Toplevel(root)
        confirm_dialog.title("Unsaved Changes")
        confirm_dialog.grab_set()
        confirm_dialog.transient(root)
        confirm_dialog.update_idletasks()

        # Center the dialog on screen
        width, height = 350, 150
        x = root.winfo_x() + (root.winfo_width() // 2) - (width // 2)
        y = root.winfo_y() + (root.winfo_height() // 2) - (height // 2)
        confirm_dialog.geometry(f"{width}x{height}+{x}+{y}")
        set_dialog_icon(confirm_dialog)

        tb.Label(confirm_dialog, text="You have unsaved tabs.\nDo you want to save them before exiting?", wraplength=280).pack(pady=20)

        def save_and_exit():
            for tab_id in unsaved:
                notebook.select(tab_id)
                save_file()
            save_session()
            confirm_dialog.destroy()
            root.destroy()

        def exit_without_save():
            save_session()
            confirm_dialog.destroy()
            root.destroy()

        def cancel_exit():
            confirm_dialog.destroy()

        button_frame = tb.Frame(confirm_dialog)
        button_frame.pack(pady=10)
        tb.Button(button_frame, text="Save & Exit", command=save_and_exit, bootstyle=SUCCESS).pack(side=tk.LEFT, padx=5)
        tb.Button(button_frame, text="Exit Without Save", command=exit_without_save, bootstyle=DANGER).pack(side=tk.LEFT, padx=5)
        tb.Button(button_frame, text="Cancel", command=cancel_exit, bootstyle=WARNING).pack(side=tk.LEFT, padx=5)
    else:
        save_session()
        root.destroy()

# --- Toolbar Buttons ---
tb.Button(toolbar, text="🆕 New", command=new_tab, bootstyle=INFO).pack(side=tk.LEFT, padx=2)
tb.Button(toolbar, text="📂 Open", command=open_file, bootstyle=SECONDARY).pack(side=tk.LEFT, padx=2)
tb.Button(toolbar, text="💾 Save", command=save_file, bootstyle=SUCCESS).pack(side=tk.LEFT, padx=2)
tb.Button(toolbar, text="❌ Close", command=close_tab, bootstyle=DANGER).pack(side=tk.LEFT, padx=2)
tb.Button(toolbar, text="🔍 Find", command=find_and_replace, bootstyle=WARNING).pack(side=tk.LEFT, padx=2)
tb.Button(toolbar, text="ℹ️ About", command=open_about_dialog, bootstyle="light-outline").pack(side=tk.RIGHT, padx=2)

# Add Media and Library menu items
settings_menu.add_command(label="🎨 Theme", command=open_theme_settings)
settings_menu.add_command(label="🧲 Physics", command=open_physics_settings)
settings_menu.add_command(label="📚 Libraries", command=open_library_manager)
settings_menu.add_command(label="📸 Media", command=open_media_manager)
settings_menu.add_command(label="🐍 Interpreter", command=open_interpreter_settings)  # ✅ Interpreter selector added here
settings_menu.add_command(label="💡 Toggle Suggestions", command=toggle_suggestions)

# --- Key Bindings ---
root.bind("<Control-n>", lambda e: new_tab())
root.bind("<Control-o>", lambda e: open_file())
root.bind("<Control-s>", lambda e: save_file())
root.bind("<Control-w>", lambda e: close_tab())
root.bind("<Control-f>", lambda e: find_and_replace())
root.bind("<F5>", lambda e: run_code())
root.protocol("WM_DELETE_WINDOW", lambda: (save_session(), root.destroy()))

root.bind("<Control-c>", lambda e: copy_code())
#root.bind("<Control-v>", lambda e: paste_code())
root.bind("<Control-z>", lambda e: undo_code())
root.bind("<Control-y>", lambda e: redo_code())


# --- Boot ---
update_physics_status()
load_session()
if not notebook.tabs():
    new_tab()

root.protocol("WM_DELETE_WINDOW", confirm_on_exit)
root.mainloop()