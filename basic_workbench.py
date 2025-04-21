import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import tempfile
import sys
import os
import json
import threading
import ttkbootstrap as tb
from ttkbootstrap.constants import *

CONFIG_FILE = "sajilopython_workbench_config.json"

# --- Config Handling ---
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {
        "theme": "flatly",
        "physics": {"enabled": False, "gravity": False, "wall": False, "collision": False, "boundary": False}
    }

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

# --- Globals ---
config = load_config()
root = tb.Window(themename=config.get("theme", "flatly"))
root.title("Sajilo Python Playground")
root.geometry("900x740")  # increased height
root.update_idletasks()
previous_process = None
kill_requested = False
output_thread = None
current_file = None

# --- Toolbar Functions ---
def new_file():
    global current_file
    editor.delete("1.0", tk.END)
    current_file = None
    root.title("Sajilo Python Playground - Untitled")

def open_file():
    global current_file
    filepath = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
    if filepath:
        with open(filepath, "r", encoding="utf-8") as f:
            editor.delete("1.0", tk.END)
            editor.insert("1.0", f.read())
        current_file = filepath
        root.title(f"Sajilo Python Playground - {os.path.basename(filepath)}")

def save_file():
    global current_file
    if not current_file:
        current_file = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")])
    if current_file:
        with open(current_file, "w", encoding="utf-8") as f:
            f.write(editor.get("1.0", tk.END))
        root.title(f"Sajilo Python Playground - {os.path.basename(current_file)}")

def close_editor():
    root.quit()

def media_action():
    messagebox.showinfo("Media", "Media functionality coming soon!")

def show_about():
    messagebox.showinfo("About", "Sajilo Python Playground\nMade with ❤️ at Beyond Apogee")

# --- Top Toolbar ---
toolbar = tb.Frame(root)
toolbar.pack(fill=X, padx=10, pady=5)

button_specs = [
    ("🆕 New", new_file, "info"),
    ("📂 Open", open_file, "secondary"),
    ("💾 Save", save_file, "success"),
    ("❌ Close", close_editor, "danger"),
    ("🎞️ Media", media_action, "warning")
]

for label, cmd, style in button_specs:
    tb.Button(toolbar, text=label, command=cmd, bootstyle=style).pack(side=LEFT, padx=2)

# About Button to far right
tb.Button(toolbar, text="ℹ️ About", command=show_about, bootstyle="light-outline").pack(side=RIGHT, padx=2)

# --- Physics Status Label Function ---
def update_physics_status_label():
    physics = config.get("physics", {})
    if physics.get("enabled", False) or any([physics.get(k) for k in ["gravity", "wall", "collision", "boundary"]]):
        active = [k.capitalize() for k, v in physics.items() if k != "enabled" and v]
        text = "Physics: " + (", ".join(active) if active else "Enabled with no components")
        physics_state_label.config(text=text, bootstyle=SUCCESS)
    else:
        physics_state_label.config(text="Physics: Disabled", bootstyle=SECONDARY)

# --- UI Elements ---
editor = tk.Text(root, font=("Consolas", 12), height=20, undo=True)
editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 0))

shell_output = tk.Text(root, height=5, bg="black", fg="light green", insertbackground="white", font=("Consolas", 11))
shell_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
shell_output.insert(tk.END, "\U0001F4A1 Shell output will appear here...\n")
shell_output.config(state=tk.DISABLED)

physics_state_label = tb.Label(root, text="")
physics_state_label.pack(fill=tk.X, padx=10)

bottom_bar = tb.Frame(root)
bottom_bar.pack(fill=tk.X, padx=10, pady=(0, 10))

settings_menu = tk.Menu(root, tearoff=0)

run_button = tb.Button(bottom_bar, text="▶️ Run", bootstyle=(OUTLINE, SUCCESS), command=lambda: run_code())
run_button.pack(side=tk.LEFT)

status_label = tb.Label(bottom_bar, text="💡 Write your code and press Run.")
status_label.pack(side=tk.LEFT, padx=10)

# --- Run / Kill ---
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
        if kill_requested:
            break
        shell_output.config(state=tk.NORMAL)
        shell_output.insert(tk.END, line.decode(errors="ignore"))
        shell_output.see(tk.END)
        shell_output.config(state=tk.DISABLED)
    if not kill_requested:
        proc.wait()
        status_label.config(text="✅ Done.")
    else:
        status_label.config(text="❌ Process killed.")
    run_button.config(text="▶️ Run", command=run_code)

def run_code():
    global previous_process, kill_requested, output_thread
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
    previous_process = subprocess.Popen(
        [sys.executable, temp_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=False
    )
    run_button.config(text="❌ Kill", command=kill_process)
    output_thread = threading.Thread(target=stream_output, args=(previous_process,), daemon=True)
    output_thread.start()

# --- Shortcuts ---
root.bind("<F5>", lambda e: run_code())
root.bind("<Control-n>", lambda e: new_file())
root.bind("<Control-o>", lambda e: open_file())
root.bind("<Control-s>", lambda e: save_file())
root.bind("<Control-w>", lambda e: close_editor())

# --- Settings ---
def open_theme_settings():
    dialog = tb.Toplevel(root)
    dialog.title("Theme Settings")
    dialog.geometry("300x200")
    dialog.grab_set()
    current_theme = root.style.theme_use()
    theme_var = tk.StringVar(value=current_theme)
    tb.Label(dialog, text="Select Theme:").pack(pady=5)
    theme_menu = tb.OptionMenu(
        dialog, theme_var, current_theme,
        *root.style.theme_names(),
        command=lambda t: apply_theme_and_save(t)
    )
    theme_menu.pack()
    tb.Button(dialog, text="Close", command=dialog.destroy, bootstyle=PRIMARY).pack(pady=15)

def apply_theme_and_save(theme):
    root.style.theme_use(theme)
    config["theme"] = theme
    save_config(config)

def open_physics_settings():
    dialog = tb.Toplevel(root)
    dialog.title("Physics Engine Settings")
    dialog.geometry("400x300")
    dialog.grab_set()
    physics = config.get("physics", {})
    physics_var = tk.BooleanVar(value=physics.get("enabled", False))
    gravity_var = tk.BooleanVar(value=physics.get("gravity", False))
    wall_var = tk.BooleanVar(value=physics.get("wall", False))
    collision_var = tk.BooleanVar(value=physics.get("collision", False))
    boundary_var = tk.BooleanVar(value=physics.get("boundary", False))

    def update_active_state():
        any_selected = any([gravity_var.get(), wall_var.get(), collision_var.get(), boundary_var.get()])
        physics_var.set(any_selected)
        config["physics"] = {
            "enabled": any_selected,
            "gravity": gravity_var.get(),
            "wall": wall_var.get(),
            "collision": collision_var.get(),
            "boundary": boundary_var.get()
        }
        update_physics_status_label()

    def sync_all_with_main():
        if physics_var.get():
            gravity_var.set(True)
            wall_var.set(True)
            collision_var.set(True)
            boundary_var.set(True)

    physics_frame = tb.Frame(dialog)
    physics_frame.pack(pady=10)
    tb.Checkbutton(physics_frame, text="Activate Physics Engine", variable=physics_var, command=sync_all_with_main, bootstyle="round-toggle").pack()
    tb.Checkbutton(physics_frame, text="Gravity", variable=gravity_var, command=update_active_state, bootstyle="round-toggle").pack(anchor=tk.W)
    tb.Checkbutton(physics_frame, text="Wall", variable=wall_var, command=update_active_state, bootstyle="round-toggle").pack(anchor=tk.W)
    tb.Checkbutton(physics_frame, text="Collision", variable=collision_var, command=update_active_state, bootstyle="round-toggle").pack(anchor=tk.W)
    tb.Checkbutton(physics_frame, text="Boundary", variable=boundary_var, command=update_active_state, bootstyle="round-toggle").pack(anchor=tk.W)

    tb.Button(dialog, text="Save", command=lambda: [save_and_close(), dialog.destroy()], bootstyle=SUCCESS).pack(pady=10)

    def save_and_close():
        config["physics"] = {
            "enabled": physics_var.get(),
            "gravity": gravity_var.get(),
            "wall": wall_var.get(),
            "collision": collision_var.get(),
            "boundary": boundary_var.get()
        }
        save_config(config)
        update_physics_status_label()

settings_menu.add_command(label="Theme", command=open_theme_settings)
settings_menu.add_command(label="Physics Engine", command=open_physics_settings)

settings_button = tb.Menubutton(bottom_bar, text="⚙️ Settings", bootstyle="primary")
settings_button.pack(side=tk.RIGHT)
settings_button["menu"] = settings_menu

update_physics_status_label()
root.update()
root.mainloop()