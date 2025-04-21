import tkinter as tk
from tkinter import ttk
import subprocess
import tempfile
import sys
import os
import json

# --- Config Persistence ---
CONFIG_FILE = "sajilopython_workbench_config.json"


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"theme": "default", "physics": {"enabled": False, "gravity": False, "wall": False, "collision": False, "boundary": False}}


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

# --- Physics State Bar ---
physics_state_label = ttk.Label(root, text="", foreground="green")
physics_state_label.pack(fill="x", padx=10)

# --- Bottom: Controls ---
bottom_bar = ttk.Frame(root)
bottom_bar.pack(fill="x", padx=10, pady=(0, 10))

run_button = ttk.Button(bottom_bar, text="▶️ Run")
run_button.pack(side="left")

status_label = ttk.Label(bottom_bar, text="💡 Write your code and press Run.")
status_label.pack(side="left", padx=10)

# --- Settings Menu ---
settings_menu = tk.Menu(root, tearoff=0)

def open_physics_settings():
    if hasattr(root, "active_dialog") and root.active_dialog:
        return
    root.active_dialog = tk.Toplevel(root)
    root.active_dialog.title("Physics Engine Settings")
    root.active_dialog.geometry("400x300")
    root.active_dialog.grab_set()
    root.active_dialog.protocol("WM_DELETE_WINDOW", lambda: close_dialog())

    physics = config.get("physics", {})
    physics_var = tk.BooleanVar(value=physics.get("enabled", False))
    gravity_var = tk.BooleanVar(value=physics.get("gravity", False))
    wall_var = tk.BooleanVar(value=physics.get("wall", False))
    collision_var = tk.BooleanVar(value=physics.get("collision", False))
    boundary_var = tk.BooleanVar(value=physics.get("boundary", False))

    def update_active_state():
        all_selected = any([gravity_var.get(), wall_var.get(), collision_var.get(), boundary_var.get()])
        physics_var.set(all_selected)
        config["physics"] = {
            "enabled": all_selected,
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

    physics_frame = ttk.Frame(root.active_dialog)
    physics_frame.pack(pady=10)
    ttk.Checkbutton(physics_frame, text="Activate Physics Engine", variable=physics_var, command=sync_all_with_main).pack()
    ttk.Checkbutton(physics_frame, text="Gravity", variable=gravity_var, command=update_active_state).pack(anchor="w")
    ttk.Checkbutton(physics_frame, text="Wall", variable=wall_var, command=update_active_state).pack(anchor="w")
    ttk.Checkbutton(physics_frame, text="Collision", variable=collision_var, command=update_active_state).pack(anchor="w")
    ttk.Checkbutton(physics_frame, text="Boundary", variable=boundary_var, command=update_active_state).pack(anchor="w")

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
        close_dialog()

    ttk.Button(root.active_dialog, text="Save", command=save_and_close).pack(pady=10)

def open_theme_settings():
    if hasattr(root, "active_dialog") and root.active_dialog:
        return
    root.active_dialog = tk.Toplevel(root)
    root.active_dialog.title("Theme Settings")
    root.active_dialog.geometry("300x200")
    root.active_dialog.grab_set()
    root.active_dialog.protocol("WM_DELETE_WINDOW", lambda: close_dialog())

    theme_var = tk.StringVar(value=style.theme_use())
    ttk.Label(root.active_dialog, text="Select Theme:").pack(pady=5)
    ttk.OptionMenu(root.active_dialog, theme_var, theme_var.get(), *style.theme_names(),
                   command=lambda t: apply_theme_and_save(t)).pack()

    ttk.Button(root.active_dialog, text="Close", command=lambda: close_dialog()).pack(pady=15)

def apply_theme_and_save(theme):
    style.theme_use(theme)
    config["theme"] = theme
    save_config(config)

def close_dialog():
    if hasattr(root, "active_dialog") and root.active_dialog:
        root.active_dialog.destroy()
        root.active_dialog = None

settings_menu.add_command(label="Theme", command=open_theme_settings)
settings_menu.add_command(label="Physics Engine", command=open_physics_settings)

settings_button = ttk.Menubutton(bottom_bar, text="⚙️ Settings", menu=settings_menu, direction="above")
settings_button.pack(side="right")
settings_button["menu"] = settings_menu

# --- Helpers ---
def update_physics_status_label():
    if config.get("physics", {}).get("enabled", False):
        active = [k.capitalize() for k, v in config.get("physics", {}).items() if k != "enabled" and v]
        text = "Physics: " + (", ".join(active) if active else "Enabled with no components")
    else:
        text = "Physics: Disabled"
    physics_state_label.config(text=text)


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


# Assign run_code to the button after defining it
run_button.config(command=run_code)

# Update physics status on startup
update_physics_status_label()

# Run the app
root.mainloop()