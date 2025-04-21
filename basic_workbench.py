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

CONFIG_FILE = "sajilopython_workbench_config.json"
SESSION_FILE = "last_session.json"
LIBRARY_FOLDER = "libraries"
MEDIA_FOLDER = "media"
FAVICON = "sajilopythonplayground.png"

os.makedirs(LIBRARY_FOLDER, exist_ok=True)
os.makedirs(MEDIA_FOLDER, exist_ok=True)

# --- Load config ---
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"theme": "flatly", "physics": {"enabled": False, "gravity": False, "wall": False, "collision": False, "boundary": False}}

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=4)

config = load_config()

# --- Main Window ---
root = tb.Window(themename=config.get("theme", "flatly"))
root.title("Sajilo Python Playground")
root.geometry("1000x880")
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

# --- Editor Tab ---
def create_editor_tab(code="", filepath=None):
    frame = tk.Frame(notebook)
    line_numbers = tk.Text(frame, width=5, padx=4, takefocus=0, border=0, background='#f0f0f0', state='disabled')
    line_numbers.pack(side="left", fill="y")
    text_frame = tk.Frame(frame)
    text_frame.pack(side="right", fill="both", expand=True)
    editor = tk.Text(text_frame, wrap="none", font=("Consolas", 12), undo=True, tabs=(Font(font=("Consolas", 12)).measure('    '),))
    editor.pack(fill="both", expand=True, side="left")
    vscroll = tk.Scrollbar(text_frame, command=editor.yview)
    vscroll.pack(side="right", fill="y")
    editor.configure(yscrollcommand=lambda *args: (vscroll.set(*args), line_numbers.yview_moveto(args[0])))
    line_numbers.configure(yscrollcommand=vscroll.set)

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
        editor.tag_config("keyword", foreground="blue")
        editor.tag_config("builtin", foreground="purple")
        editor.tag_config("special", foreground="green")

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

    editor.bind("<KeyRelease>", lambda e: (highlight(), update_lines(), highlight_line()))
    editor.bind("<ButtonRelease>", highlight_line)
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
    dialog = tb.Toplevel(root)
    dialog.title("Media Manager")
    dialog.geometry("600x400")
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
        row = 0
        col = 0
        for fname in os.listdir(MEDIA_FOLDER):
            fpath = os.path.join(MEDIA_FOLDER, fname)
            if fname.lower().endswith((".png", ".jpg", ".gif")):
                try:
                    img = Image.open(fpath)
                    img.thumbnail((64, 64))
                    thumb = ImageTk.PhotoImage(img)
                    lbl = tk.Label(scroll_frame, image=thumb)
                    lbl.image = thumb
                    lbl.grid(row=row, column=col, padx=5, pady=5)
                except:
                    continue
            else:
                tb.Label(scroll_frame, text=fname).grid(row=row, column=col, padx=5, pady=5)
            col += 1
            if col > 4:
                col = 0
                row += 1

    def upload():
        files = filedialog.askopenfilenames(filetypes=[("Media Files", ".png .jpg .gif .mp3 .wav")])
        for f in files:
            shutil.copy(f, os.path.join(MEDIA_FOLDER, os.path.basename(f)))
        refresh()

    tb.Button(dialog, text="Upload Media", command=upload, bootstyle=INFO).pack(pady=5)
    refresh()

def open_library_manager():
    dialog = tb.Toplevel(root)
    dialog.title("Library Manager")
    dialog.geometry("600x400")
    frame = tb.Frame(dialog)
    frame.pack(fill="both", expand=True)

    def refresh():
        for widget in frame.winfo_children():
            widget.destroy()
        for fname in os.listdir(LIBRARY_FOLDER):
            fpath = os.path.join(LIBRARY_FOLDER, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                lines = f.readlines()
            meta = {'Author': '', 'Version': '', 'About': ''}
            for line in lines:
                for key in meta:
                    if line.startswith(f"# {key}:"):
                        meta[key] = line.split(":", 1)[1].strip()
            row = tb.Frame(frame)
            row.pack(fill="x", padx=5, pady=2)
            tb.Label(row, text=fname, width=25).pack(side="left")
            tb.Label(row, text=f"Author: {meta['Author']}  Version: {meta['Version']}  About: {meta['About']}").pack(side="left")
            tb.Button(row, text="Delete", bootstyle=DANGER, command=lambda f=fpath: (os.remove(f), refresh())).pack(side="right")

    def upload():
        file = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file:
            shutil.copy(file, os.path.join(LIBRARY_FOLDER, os.path.basename(file)))
            refresh()

    tb.Button(dialog, text="Upload Library", command=upload, bootstyle=SUCCESS).pack(pady=5)
    refresh()

# --- Toolbar Actions ---
def new_tab(): create_editor_tab()

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

def close_tab():
    tab = notebook.select()
    if tab:
        editors.pop(str(tab), None)
        notebook.forget(tab)

def find_and_replace():
    tab = notebook.select()
    editor = editors.get(str(tab), {}).get("editor")
    if not editor: return
    find = simpledialog.askstring("Find", "Find:", parent=root)
    replace = simpledialog.askstring("Replace", "Replace with:", parent=root)
    if find and replace:
        content = editor.get("1.0", "end")
        content = content.replace(find, replace)
        editor.delete("1.0", "end")
        editor.insert("1.0", content)

# --- Settings ---
def update_physics_status():
    physics = config.get("physics", {})
    if physics.get("enabled") or any(physics.values()):
        active = [k.capitalize() for k, v in physics.items() if v and k != "enabled"]
        text = "Physics: " + (", ".join(active) if active else "Enabled")
        physics_state_label.config(text=text, bootstyle=SUCCESS)
    else:
        physics_state_label.config(text="Physics: Disabled", bootstyle=SECONDARY)

def open_physics_settings():
    dialog = tb.Toplevel(root)
    dialog.title("Physics Engine Settings")
    dialog.geometry("400x350")
    physics = config.get("physics", {})
    vars = {k: tk.BooleanVar(value=physics.get(k, False)) for k in ["enabled", "gravity", "wall", "collision", "boundary"]}
    for key, var in vars.items():
        tb.Checkbutton(dialog, text=key.capitalize(), variable=var, bootstyle="round-toggle").pack(anchor="w", padx=20, pady=3)
    def save():
        config["physics"] = {k: v.get() for k, v in vars.items()}
        save_config(config)
        update_physics_status()
        dialog.destroy()
    tb.Button(dialog, text="Save", command=save, bootstyle=SUCCESS).pack(pady=10)

def open_theme_settings():
    dialog = tb.Toplevel(root)
    dialog.title("Theme Settings")
    dialog.geometry("300x160")
    current_theme = root.style.theme_use()
    theme_var = tk.StringVar(value=current_theme)

    tb.Label(dialog, text="Select Editor Theme:").pack(pady=10)
    theme_dropdown = ttk.OptionMenu(dialog, theme_var, current_theme, *root.style.theme_names())
    theme_dropdown.pack(pady=5)

    def apply_and_close():
        root.style.theme_use(theme_var.get())
        config["theme"] = theme_var.get()
        save_config(config)
        dialog.destroy()

    tb.Button(dialog, text="Apply", command=apply_and_close, bootstyle=SUCCESS).pack(pady=10)

def apply_theme(theme):
    root.style.theme_use(theme)
    config["theme"] = theme
    save_config(config)

# --- Run Button ---
def run_code():
    global previous_process, kill_requested
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
    proc = subprocess.Popen([sys.executable, path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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

# --- Toolbar Buttons ---
tb.Button(toolbar, text="🆕 New", command=new_tab, bootstyle=INFO).pack(side=tk.LEFT, padx=2)
tb.Button(toolbar, text="📂 Open", command=open_file, bootstyle=SECONDARY).pack(side=tk.LEFT, padx=2)
tb.Button(toolbar, text="💾 Save", command=save_file, bootstyle=SUCCESS).pack(side=tk.LEFT, padx=2)
tb.Button(toolbar, text="❌ Close", command=close_tab, bootstyle=DANGER).pack(side=tk.LEFT, padx=2)
tb.Button(toolbar, text="🔍 Find", command=find_and_replace, bootstyle=WARNING).pack(side=tk.LEFT, padx=2)
tb.Button(toolbar, text="ℹ️ About", command=lambda: messagebox.showinfo("About", "Sajilo Python Playground\nMade with ❤️ at Beyond Apogee"), bootstyle="light-outline").pack(side=tk.RIGHT, padx=2)

# Add Media and Library menu items
settings_menu.add_command(label="🎨 Theme", command=open_theme_settings)
settings_menu.add_command(label="🧲 Physics", command=open_physics_settings)
settings_menu.add_command(label="📚 Libraries", command=open_library_manager)
settings_menu.add_command(label="🎞️ Media", command=open_media_manager)

# --- Key Bindings ---
root.bind("<Control-n>", lambda e: new_tab())
root.bind("<Control-o>", lambda e: open_file())
root.bind("<Control-s>", lambda e: save_file())
root.bind("<Control-w>", lambda e: close_tab())
root.bind("<Control-f>", lambda e: find_and_replace())
root.bind("<F5>", lambda e: run_code())
root.protocol("WM_DELETE_WINDOW", lambda: (save_session(), root.destroy()))

# --- Boot ---
update_physics_status()
load_session()
if not notebook.tabs():
    new_tab()
root.mainloop()