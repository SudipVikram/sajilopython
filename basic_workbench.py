import tkinter as tk
from tkinter import ttk
import subprocess
import tempfile
import sys
import os
import json

# --- Config Persistence ---
CONFIG_FILE = "sajilo_config.json"


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"theme": "default"}


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

# --- Globals ---
previous_process = None
file_offsets = {}
output_path_active = None
kill_requested = False


# --- Tkinter UI Setup ---
root = tk.Tk()
root.title("Sajilo Python Playground")
root.geometry("900x700")

# Apply saved theme
style = ttk.Style()
config = load_config()
theme_to_use = config.get("theme", "default")
if theme_to_use in style.theme_names():
    style.theme_use(theme_to_use)

# --- Top: Editor ---
editor = tk.Text(root, font=("Consolas", 12), height=20)
editor.pack(fill="both", expand=True, padx=10, pady=(10, 0))

# --- Middle: Shell Output ---
shell_output = tk.Text(root, height=10, bg="#111", fg="#0f0", insertbackground="white", font=("Consolas", 11))
shell_output.pack(fill="both", expand=False, padx=10, pady=(5, 5))
shell_output.insert(tk.END, "💡 Shell output will appear here...\n")
shell_output.config(state="disabled")

# --- Bottom: Controls ---
bottom_bar = ttk.Frame(root)
bottom_bar.pack(fill="x", padx=10, pady=(0, 10))

run_button = ttk.Button(bottom_bar, text="▶️ Run")
run_button.pack(side="left")

status_label = ttk.Label(bottom_bar, text="💡 Write your code and press Run.")
status_label.pack(side="left", padx=10)

settings_button = ttk.Button(bottom_bar, text="⚙️ Settings", command=lambda: open_settings())
settings_button.pack(side="right")


# --- Helpers ---
def is_pygame_code(code):
    lowered = code.lower()
    return "import pygame" in lowered or "from pygame" in lowered or "pygame." in lowered


def kill_process():
    global kill_requested, previous_process, output_path_active
    kill_requested = True

    if previous_process and previous_process.poll() is None:
        try:
            previous_process.kill()
            status_label.config(text="❌ Process killed.")
        except Exception as e:
            status_label.config(text=f"❌ Failed to kill: {e}")

    previous_process = None
    output_path_active = None
    run_button.config(text="▶️ Run", command=run_code)


def run_code():
    global previous_process, kill_requested, output_path_active

    code = editor.get("1.0", tk.END)
    is_pygame = is_pygame_code(code)

    shell_output.config(state="normal")
    shell_output.delete("1.0", tk.END)
    if is_pygame:
        shell_output.insert(tk.END, "🔄 Running your code...\n")
    shell_output.config(state="disabled")

    if previous_process and previous_process.poll() is None:
        try:
            previous_process.kill()
        except Exception as e:
            print("Failed to kill previous process:", e)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as tmp_file:
        tmp_file.write(code)
        temp_path = tmp_file.name

    output_file = tempfile.NamedTemporaryFile(delete=False, mode="w+", encoding="utf-8")
    output_path = output_file.name
    output_file.close()

    file_offsets[output_path] = 0
    output_path_active = output_path
    kill_requested = False

    try:
        previous_process = subprocess.Popen(
            [sys.executable, temp_path],
            stdout=open(output_path, "w"),
            stderr=subprocess.STDOUT,
            start_new_session=True
        )

        status_label.config(
            text="✅ Running in separate Pygame window. Output below:" if is_pygame else "✅ Code is running...")
        run_button.config(text="❌ Kill", command=kill_process)

        read_output(output_path)
    except Exception as e:
        shell_output.config(state="normal")
        shell_output.insert(tk.END, f"❌ Error launching code: {e}\n")
        shell_output.config(state="disabled")
        status_label.config(text="❌ Run failed.")


def read_output(output_path):
    global kill_requested

    if kill_requested or output_path != output_path_active:
        return

    try:
        with open(output_path, "r") as f:
            f.seek(file_offsets[output_path])
            new_output = f.read()
            file_offsets[output_path] = f.tell()

        if new_output:
            shell_output.config(state="normal")
            shell_output.insert(tk.END, new_output)
            shell_output.config(state="disabled")
            shell_output.see("end")

    except Exception as e:
        shell_output.config(state="normal")
        shell_output.insert(tk.END, f"❌ Error reading output: {e}\n")
        shell_output.config(state="disabled")

    root.after(500, lambda: read_output(output_path))


# --- Settings Dialog ---
def open_settings():
    settings_win = tk.Toplevel(root)
    settings_win.title("Editor Settings")
    settings_win.geometry("400x300")
    settings_win.resizable(False, False)
    settings_win.grab_set()

    ttk.Label(settings_win, text="Select a Theme", font=("Arial", 12)).pack(pady=10)

    theme_var = tk.StringVar()
    theme_var.set(style.theme_use())

    def apply_theme(theme_name):
        style.theme_use(theme_name)
        build_preview(preview_frame)
        config["theme"] = theme_name
        save_config(config)

    ttk.OptionMenu(settings_win, theme_var, theme_var.get(), *style.theme_names(),
                   command=apply_theme).pack()

    ttk.Label(settings_win, text="Preview:", font=("Arial", 10, "bold")).pack(pady=10)
    preview_frame = ttk.Frame(settings_win)
    preview_frame.pack(pady=5)

    def build_preview(parent):
        for widget in parent.winfo_children():
            widget.destroy()
        ttk.Label(parent, text="Sample Label").pack(pady=2)
        ttk.Entry(parent).pack(pady=2)
        ttk.Button(parent, text="Sample Button").pack(pady=2)

    build_preview(preview_frame)
    ttk.Button(settings_win, text="Close", command=settings_win.destroy).pack(pady=15)


# Assign run_code to the button after defining it
run_button.config(command=run_code)

# Run the app
root.mainloop()