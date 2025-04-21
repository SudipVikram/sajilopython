import tkinter as tk
from tkinter import ttk
import subprocess
import tempfile
import sys
import os

previous_process = None
file_offsets = {}  # Tracks file position per output file

def is_pygame_code(code):
    lowered = code.lower()
    return "import pygame" in lowered or "from pygame" in lowered or "pygame." in lowered

def run_code():
    global previous_process

    code = editor.get("1.0", tk.END)
    is_pygame = is_pygame_code(code)

    # Clear shell output
    shell_output.config(state="normal")
    shell_output.delete("1.0", tk.END)
    if is_pygame:
        shell_output.insert(tk.END, "🔄 Running your code...\n")
    shell_output.config(state="disabled")

    # Kill previous process if it exists
    if previous_process and previous_process.poll() is None:
        try:
            previous_process.kill()
        except Exception as e:
            print("Failed to kill previous process:", e)

    # Write code to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as tmp_file:
        tmp_file.write(code)
        temp_path = tmp_file.name

    # Output capture file
    output_file = tempfile.NamedTemporaryFile(delete=False, mode="w+", encoding="utf-8")
    output_path = output_file.name
    output_file.close()

    # Reset offset tracker
    file_offsets[output_path] = 0

    try:
        previous_process = subprocess.Popen(
            [sys.executable, temp_path],
            stdout=open(output_path, "w"),
            stderr=subprocess.STDOUT,
            start_new_session=True
        )

        if is_pygame:
            status_label.config(text="✅ Running in separate Pygame window. Output below:")
        else:
            status_label.config(text="✅ Code is running...")

        read_output(output_path)
    except Exception as e:
        shell_output.config(state="normal")
        shell_output.insert(tk.END, f"❌ Error launching code: {e}\n")
        shell_output.config(state="disabled")
        status_label.config(text="❌ Run failed.")

def read_output(output_path):
    try:
        # Set initial offset if not already set
        if output_path not in file_offsets:
            file_offsets[output_path] = 0

        with open(output_path, "r") as f:
            f.seek(file_offsets[output_path])  # Jump to last read position
            new_output = f.read()
            file_offsets[output_path] = f.tell()  # Update position

        if new_output:
            shell_output.config(state="normal")
            shell_output.insert(tk.END, new_output)
            shell_output.config(state="disabled")
            shell_output.see("end")
    except Exception as e:
        shell_output.config(state="normal")
        shell_output.insert(tk.END, f"❌ Error reading output: {e}\n")
        shell_output.config(state="disabled")

    # Reschedule
    root.after(500, lambda: read_output(output_path))

# --- GUI Setup ---

root = tk.Tk()
root.title("Sajilo Python Playground")
root.geometry("800x700")

# Editor Frame
editor = tk.Text(root, font=("Consolas", 12), height=20)
editor.pack(fill="both", expand=True, padx=10, pady=(10, 0))

# Shell Output Frame
shell_output = tk.Text(root, height=10, bg="#111", fg="#0f0", insertbackground="white", font=("Consolas", 11))
shell_output.pack(fill="both", expand=False, padx=10, pady=(5, 5))
shell_output.insert(tk.END, "💡 Shell output will appear here...\n")
shell_output.config(state="disabled")

# Bottom Bar
bottom_bar = ttk.Frame(root)
bottom_bar.pack(fill="x", padx=10, pady=(0, 10))

run_button = ttk.Button(bottom_bar, text="▶️ Run", command=run_code)
run_button.pack(side="left")

status_label = ttk.Label(bottom_bar, text="💡 Write your code and press Run.")
status_label.pack(side="left", padx=10)

root.mainloop()
