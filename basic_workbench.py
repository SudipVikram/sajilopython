import tkinter as tk
import subprocess
import tempfile
import sys
import os
import json
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# --- Config Persistence ---
CONFIG_FILE = "sajilopython_workbench_config.json"


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {
        "theme": "flatly",
        "physics": {
            "enabled": False,
            "gravity": False,
            "wall": False,
            "collision": False,
            "boundary": False
        }
    }


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)


# --- Globals ---
previous_process = None
file_offsets = {}
output_path_active = None
kill_requested = False

# --- Initialize App ---
config = load_config()
root = tb.Window(themename=config.get("theme", "flatly"))
root.title("Sajilo Python Playground")
root.geometry("900x700")


# --- Physics Status Label Function ---
def update_physics_status_label():
    physics = config.get("physics", {})
    if physics.get("enabled", False):
        active = [k.capitalize() for k, v in physics.items()
                  if k != "enabled" and v]
        text = "Physics: " + (", ".join(active) if active else "Enabled with no components")
        physics_state_label.config(text=text, bootstyle=SUCCESS)
    else:
        physics_state_label.config(text="Physics: Disabled", bootstyle=SECONDARY)


# --- UI Elements ---
# Editor
editor = tk.Text(root, font=("Consolas", 12), height=20)
editor.pack(fill=BOTH, expand=True, padx=10, pady=(10, 0))

# Shell Output
shell_output = tk.Text(
    root,
    height=10,
    bg="#222",
    fg="#ddd",
    insertbackground="white",
    font=("Consolas", 11)
)
shell_output.pack(fill=BOTH, expand=False, padx=10, pady=5)
shell_output.insert(END, "💡 Shell output will appear here...\n")
shell_output.config(state=DISABLED)

# Physics State Bar
physics_state_label = tb.Label(root, text="")
physics_state_label.pack(fill=X, padx=10)

# Bottom Controls
bottom_bar = tb.Frame(root)
bottom_bar.pack(fill=X, padx=10, pady=(0, 10))

run_button = tb.Button(
    bottom_bar,
    text="▶️ Run",
    bootstyle=(OUTLINE, SUCCESS),
    command=lambda: run_code()
)
run_button.pack(side=LEFT)

status_label = tb.Label(bottom_bar, text="💡 Write your code and press Run.")
status_label.pack(side=LEFT, padx=10)

# Settings Menu
settings_menu = tk.Menu(root, tearoff=0)


def open_physics_settings():
    if hasattr(root, "active_dialog") and root.active_dialog:
        return

    dialog = tb.Toplevel(root)
    dialog.title("Physics Engine Settings")
    dialog.geometry("400x300")
    dialog.grab_set()
    root.active_dialog = dialog

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

    physics_frame = tb.Frame(dialog)
    physics_frame.pack(pady=10)

    tb.Checkbutton(
        physics_frame,
        text="Activate Physics Engine",
        variable=physics_var,
        command=sync_all_with_main,
        bootstyle="round-toggle"
    ).pack()

    tb.Checkbutton(
        physics_frame,
        text="Gravity",
        variable=gravity_var,
        command=update_active_state,
        bootstyle="round-toggle"
    ).pack(anchor=W)

    tb.Checkbutton(
        physics_frame,
        text="Wall",
        variable=wall_var,
        command=update_active_state,
        bootstyle="round-toggle"
    ).pack(anchor=W)

    tb.Checkbutton(
        physics_frame,
        text="Collision",
        variable=collision_var,
        command=update_active_state,
        bootstyle="round-toggle"
    ).pack(anchor=W)

    tb.Checkbutton(
        physics_frame,
        text="Boundary",
        variable=boundary_var,
        command=update_active_state,
        bootstyle="round-toggle"
    ).pack(anchor=W)

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
        dialog.destroy()
        root.active_dialog = None

    tb.Button(
        dialog,
        text="Save",
        command=save_and_close,
        bootstyle=SUCCESS
    ).pack(pady=10)

    dialog.protocol("WM_DELETE_WINDOW", save_and_close)


def open_theme_settings():
    if hasattr(root, "active_dialog") and root.active_dialog:
        return

    dialog = tb.Toplevel(root)
    dialog.title("Theme Settings")
    dialog.geometry("300x200")
    dialog.grab_set()
    root.active_dialog = dialog

    current_theme = root.style.theme_use()
    theme_var = tk.StringVar(value=current_theme)

    tb.Label(dialog, text="Select Theme:").pack(pady=5)

    theme_menu = tb.OptionMenu(
        dialog,
        theme_var,
        current_theme,
        *root.style.theme_names(),
        command=lambda t: apply_theme_and_save(t)
    )
    theme_menu.pack()

    tb.Button(
        dialog,
        text="Close",
        command=lambda: dialog.destroy(),
        bootstyle=PRIMARY
    ).pack(pady=15)

    dialog.protocol("WM_DELETE_WINDOW", lambda: dialog.destroy())


def apply_theme_and_save(theme):
    root.style.theme_use(theme)
    config["theme"] = theme
    save_config(config)


settings_menu.add_command(label="Theme", command=open_theme_settings)
settings_menu.add_command(label="Physics Engine", command=open_physics_settings)

settings_button = tb.Menubutton(
    bottom_bar,
    text="⚙️ Settings",
    menu=settings_menu,
    bootstyle="primary"  # note the correct way is lowercase string, or use constant if defined
)

settings_button.pack(side=RIGHT)
settings_button["menu"] = settings_menu


# --- Code Execution Functions ---
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

    code = editor.get("1.0", END)
    is_pygame = is_pygame_code(code)

    shell_output.config(state=NORMAL)
    shell_output.delete("1.0", END)
    if is_pygame:
        shell_output.insert(END, "🔄 Running your code...\n")
    shell_output.config(state=DISABLED)

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
            text="✅ Running in separate Pygame window. Output below:" if is_pygame
            else "✅ Code is running..."
        )
        run_button.config(text="❌ Kill", command=kill_process)

        read_output(output_path)
    except Exception as e:
        shell_output.config(state=NORMAL)
        shell_output.insert(END, f"❌ Error launching code: {e}\n")
        shell_output.config(state=DISABLED)
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
            shell_output.config(state=NORMAL)
            shell_output.insert(END, new_output)
            shell_output.config(state=DISABLED)
            shell_output.see(END)

    except Exception as e:
        shell_output.config(state=NORMAL)
        shell_output.insert(END, f"❌ Error reading output: {e}\n")
        shell_output.config(state=DISABLED)

    root.after(500, lambda: read_output(output_path))


# Initialize physics status
update_physics_status_label()

# Run the app
root.mainloop()