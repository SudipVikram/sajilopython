# FULL ENHANCED VERSION OF SAJILO PYTHON WORKBENCH WITH FIXES
import tkinter as tk
from tkinter import filedialog, messagebox, PhotoImage
import subprocess
import tempfile
import sys
import os
import json
import threading
import shutil
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk
from PIL import Image, ImageTk

CONFIG_FILE = "sajilopython_workbench_config.json"
LIBRARY_FOLDER = "libraries"
MEDIA_FOLDER = "media"
SESSION_FILE = "last_session.json"
os.makedirs(LIBRARY_FOLDER, exist_ok=True)
os.makedirs(MEDIA_FOLDER, exist_ok=True)

# --- Load/Save Config ---
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"theme": "flatly", "physics": {"enabled": False, "gravity": False, "wall": False, "collision": False, "boundary": False}}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

config = load_config()
root = tb.Window(themename=config.get("theme", "flatly"))
root.title("Sajilo Python Playground")
root.geometry("1000x880")
previous_process = None
kill_requested = False
output_thread = None
editors = {}
unsaved_tabs = set()

# --- Restore Previous Session ---
def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            paths = json.load(f)
        for path in paths:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                new_file(content, path)
            except:
                continue

def save_session():
    paths = [data["file"] for data in editors.values() if data["file"]]
    with open(SESSION_FILE, "w") as f:
        json.dump(paths, f)

# --- Setup UI ---
toolbar = tb.Frame(root)
toolbar.pack(fill=X, padx=10, pady=5)
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 0))
shell_output = tk.Text(root, height=6, bg="black", fg="light green", insertbackground="white", font=("Consolas", 11))
shell_output.pack(fill=tk.BOTH, expand=False, padx=10, pady=(0, 5))
shell_output.insert(tk.END, "\U0001F4A1 Shell output will appear here...\n")
shell_output.config(state=tk.DISABLED)
physics_state_label = tb.Label(root, text="")
physics_state_label.pack(fill=X, padx=10)
bottom_bar = tb.Frame(root)
bottom_bar.pack(fill=X, padx=10, pady=(0, 10))
run_button = tb.Button(bottom_bar, text="▶️ Run", bootstyle=(OUTLINE, SUCCESS), command=lambda: run_code())
run_button.pack(side=LEFT)
status_label = tb.Label(bottom_bar, text="💡 Write your code and press Run.")
status_label.pack(side=LEFT, padx=10)
settings_menu = tk.Menu(root, tearoff=0)
settings_button = tb.Menubutton(bottom_bar, text="⚙️ Settings", bootstyle="primary")
settings_button.pack(side=tk.RIGHT)
settings_button["menu"] = settings_menu

# --- Editor Handling ---
def new_file(content="", filepath=None):
    frame = tk.Frame(notebook)
    editor = tk.Text(frame, font=("Consolas", 12), undo=True)
    editor.pack(fill=tk.BOTH, expand=True)
    notebook.add(frame, text="Untitled")
    notebook.select(frame)
    editors[str(frame)] = {"editor": editor, "file": filepath}
    if filepath:
        notebook.tab(frame, text=os.path.basename(filepath))
    editor.insert("1.0", content)
    editor.bind("<Key>", lambda e: mark_unsaved(str(frame)))

def get_current_tab_id():
    return notebook.select()

def get_current_editor():
    return editors.get(get_current_tab_id(), {}).get("editor")

def get_current_file():
    return editors.get(get_current_tab_id(), {}).get("file")

def set_current_file(filepath):
    tab_id = get_current_tab_id()
    if tab_id in editors:
        editors[tab_id]["file"] = filepath
        notebook.tab(tab_id, text=os.path.basename(filepath))
        unsaved_tabs.discard(tab_id)

# --- Unsaved Indicator ---
def mark_unsaved(tab_id):
    if tab_id not in unsaved_tabs:
        name = notebook.tab(tab_id, option="text")
        if not name.endswith("*"):
            notebook.tab(tab_id, text=name + "*")
        unsaved_tabs.add(tab_id)

def check_unsaved():
    if unsaved_tabs:
        return messagebox.askyesno("Unsaved Changes", "Some files are unsaved. Are you sure you want to exit?")
    return True

# --- File Operations ---
def open_file():
    filepath = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
    if filepath:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        new_file(content, filepath)

def save_file():
    tab_id = get_current_tab_id()
    editor = get_current_editor()
    if not editor:
        return
    filepath = get_current_file()
    if not filepath:
        filepath = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")])
        if not filepath:
            return
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(editor.get("1.0", tk.END))
    set_current_file(filepath)
    notebook.tab(tab_id, text=os.path.basename(filepath))
    unsaved_tabs.discard(tab_id)

def close_tab():
    tab_id = get_current_tab_id()
    if tab_id in unsaved_tabs:
        if not messagebox.askyesno("Unsaved Tab", "This file is unsaved. Close anyway?"):
            return
    notebook.forget(tab_id)
    editors.pop(tab_id, None)
    unsaved_tabs.discard(tab_id)

# --- Run Logic (same as before) ---
def kill_process():
    global previous_process, kill_requested
    kill_requested = True
    if previous_process and previous_process.poll() is None:
        try:
            previous_process.kill()
            status_label.config(text="❌ Process killed.")
        except Exception as e:
            status_label.config(text=f"❌ Failed to kill: {e}")
    previous_process = None
    run_button.config(text="▶️ Run", command=run_code)

def stream_output(proc):
    global kill_requested
    while True:
        if kill_requested:
            break
        line = proc.stdout.readline()
        if not line:
            break
        shell_output.config(state=tk.NORMAL)
        shell_output.insert(tk.END, line.decode(errors="ignore"))
        shell_output.see(tk.END)
        shell_output.config(state=tk.DISABLED)
    run_button.config(text="▶️ Run", command=run_code)
    status_label.config(text="✅ Done." if not kill_requested else "❌ Process killed.")

def run_code():
    global previous_process, kill_requested, output_thread
    editor = get_current_editor()
    if not editor:
        return
    code = editor.get("1.0", tk.END)
    shell_output.config(state=tk.NORMAL)
    shell_output.delete("1.0", tk.END)
    shell_output.insert(tk.END, "Running your code...\n")
    shell_output.config(state=tk.DISABLED)
    status_label.config(text="⏳ Running...")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as tmp_file:
        tmp_file.write(code)
        temp_path = tmp_file.name
    kill_requested = False
    previous_process = subprocess.Popen([sys.executable, temp_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=False)
    run_button.config(text="❌ Kill", command=kill_process)
    output_thread = threading.Thread(target=stream_output, args=(previous_process,), daemon=True)
    output_thread.start()

# --- Settings & Dialogs ---
def open_library_settings():
    dialog = tb.Toplevel(root)
    dialog.title("Library Manager")
    dialog.geometry("600x400")

    def refresh():
        for widget in content_frame.winfo_children():
            widget.destroy()
        for fname in os.listdir(LIBRARY_FOLDER):
            fpath = os.path.join(LIBRARY_FOLDER, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                header = f.read(300)
            author = version = about = ""
            for line in header.splitlines():
                if line.startswith("# Author:"):
                    author = line.split(":", 1)[1].strip()
                if line.startswith("# Version:"):
                    version = line.split(":", 1)[1].strip()
                if line.startswith("# About:"):
                    about = line.split(":", 1)[1].strip()
            frame = tb.Frame(content_frame)
            frame.pack(fill=X, pady=2)
            tb.Label(frame, text=fname).pack(side=LEFT, padx=5)
            tb.Label(frame, text=f"Author: {author} | Version: {version} | About: {about}", font=("Consolas", 9)).pack(side=LEFT, padx=5)
            tb.Button(frame, text="❌", bootstyle=DANGER, command=lambda f=fpath: (os.remove(f), refresh())).pack(side=RIGHT)

    def upload():
        file = filedialog.askopenfilename()
        if file:
            shutil.copy(file, os.path.join(LIBRARY_FOLDER, os.path.basename(file)))
            refresh()

    tb.Button(dialog, text="Upload File", command=upload, bootstyle=SUCCESS).pack(pady=5)
    content_frame = tb.Frame(dialog)
    content_frame.pack(fill=BOTH, expand=True)
    refresh()

def open_media_dialog():
    dialog = tb.Toplevel(root)
    dialog.title("Media Manager")
    dialog.geometry("600x400")

    def refresh():
        for widget in content_frame.winfo_children():
            widget.destroy()
        for fname in os.listdir(MEDIA_FOLDER):
            fpath = os.path.join(MEDIA_FOLDER, fname)
            frame = tb.Frame(content_frame)
            frame.pack(fill=X, pady=3)
            if fname.lower().endswith((".jpg", ".png", ".gif")):
                try:
                    img = Image.open(fpath)
                    img.thumbnail((40, 40))
                    thumb = ImageTk.PhotoImage(img)
                    label = tk.Label(frame, image=thumb)
                    label.image = thumb
                    label.pack(side=LEFT, padx=5)
                except:
                    tb.Label(frame, text="[Image Error]").pack(side=LEFT, padx=5)
            else:
                tb.Label(frame, text=fname).pack(side=LEFT, padx=5)

    def upload():
        files = filedialog.askopenfilenames(filetypes=[("Media", ".jpg .png .gif .mp3 .wav")])
        for f in files:
            shutil.copy(f, os.path.join(MEDIA_FOLDER, os.path.basename(f)))
        refresh()

    tb.Button(dialog, text="Add Media", command=upload, bootstyle=INFO).pack(pady=5)
    content_frame = tb.Frame(dialog)
    content_frame.pack(fill=BOTH, expand=True)
    refresh()

def update_physics_status_label():
    physics = config.get("physics", {})
    if physics.get("enabled") or any(physics.values()):
        active = [k.capitalize() for k, v in physics.items() if v and k != "enabled"]
        text = "Physics: " + (", ".join(active) if active else "Enabled")
        physics_state_label.config(text=text, bootstyle=SUCCESS)
    else:
        physics_state_label.config(text="Physics: Disabled", bootstyle=SECONDARY)

def open_theme_settings():
    dialog = tb.Toplevel(root)
    dialog.title("Theme Settings")
    dialog.geometry("300x200")
    current_theme = root.style.theme_use()
    theme_var = tk.StringVar(value=current_theme)
    tb.Label(dialog, text="Select Theme:").pack(pady=5)
    tb.OptionMenu(dialog, theme_var, current_theme, *root.style.theme_names(), command=lambda t: apply_theme_and_save(t)).pack()
    tb.Button(dialog, text="Close", command=dialog.destroy, bootstyle=PRIMARY).pack(pady=15)

def apply_theme_and_save(theme):
    root.style.theme_use(theme)
    config["theme"] = theme
    save_config(config)

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
        update_physics_status_label()
        dialog.destroy()
    tb.Button(dialog, text="Save", command=save, bootstyle=SUCCESS).pack(pady=10)

settings_menu.add_command(label="Theme", command=open_theme_settings)
settings_menu.add_command(label="Physics Engine", command=open_physics_settings)
settings_menu.add_command(label="Libraries", command=open_library_settings)

# --- Toolbar Buttons ---
tb.Button(toolbar, text="🆕 New", command=new_file, bootstyle=INFO).pack(side=LEFT, padx=2)
tb.Button(toolbar, text="📂 Open", command=open_file, bootstyle=SECONDARY).pack(side=LEFT, padx=2)
tb.Button(toolbar, text="💾 Save", command=save_file, bootstyle=SUCCESS).pack(side=LEFT, padx=2)
tb.Button(toolbar, text="❌ Close", command=close_tab, bootstyle=DANGER).pack(side=LEFT, padx=2)
tb.Button(toolbar, text="🎞️ Media", command=open_media_dialog, bootstyle=WARNING).pack(side=LEFT, padx=2)
tb.Button(toolbar, text="ℹ️ About", command=lambda: messagebox.showinfo("About", "Sajilo Python Playground\nMade with ❤️ at Beyond Apogee"), bootstyle="light-outline").pack(side=RIGHT, padx=2)

# --- Keybindings & Startup ---
root.bind("<F5>", lambda e: run_code())
root.bind("<Control-n>", lambda e: new_file())
root.bind("<Control-o>", lambda e: open_file())
root.bind("<Control-s>", lambda e: save_file())
root.bind("<Control-w>", lambda e: close_tab())
root.protocol("WM_DELETE_WINDOW", lambda: (save_session(), root.destroy()) if check_unsaved() else None)

update_physics_status_label()
load_session()
if not notebook.tabs():
    new_file()
root.mainloop()