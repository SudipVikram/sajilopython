import tkinter as tk
from tkinter import ttk, Menu, scrolledtext
import pygame
import threading
import os
import sys
import time

class Redirector:
    def __init__(self, text_area):
        self.text_area = text_area

    def write(self, string):
        self.text_area.insert(tk.END, string)
        self.text_area.see(tk.END)

    def flush(self):
        pass

class SajiloApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SajiloPython IDE")
        self.root.geometry("1000x700")

        self.create_menu()
        self.create_layout()
        self.setup_console()
        self.root.after(1000, self.embed_pygame)

    def create_menu(self):
        menubar = Menu(self.root)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="New")
        filemenu.add_command(label="Open")
        filemenu.add_command(label="Save")
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo")
        editmenu.add_command(label="Redo")
        menubar.add_cascade(label="Edit", menu=editmenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About")
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.root.config(menu=menubar)

    def create_layout(self):
        self.left_frame = tk.Frame(self.root, width=500, bg='gray')
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.line_numbers = tk.Text(self.left_frame, width=4, padx=4, takefocus=0, border=0,
                                    background='lightgray', state='disabled')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        editor_frame = tk.Frame(self.left_frame, bg='gray')
        editor_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        self.editor = tk.Text(editor_frame, font=("Courier", 12), bg='gray', fg='black', insertbackground='black')
        self.editor.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
        self.editor.bind("<KeyRelease>", self.update_line_numbers)

        self.run_button = tk.Button(editor_frame, text="Run", command=self.execute_editor_code)
        self.run_button.pack(fill=tk.X, side=tk.BOTTOM)

        self.right_frame = tk.Frame(self.root, width=500)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.pygame_canvas = tk.Canvas(self.right_frame, width=500, height=600, bg='black')
        self.pygame_canvas.pack()

        self.console = scrolledtext.ScrolledText(self.root, height=8, bg='black', fg='white')
        self.console.pack(fill=tk.X, side=tk.BOTTOM)

    def update_line_numbers(self, event=None):
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        line_count = self.editor.index('end-1c').split('.')[0]
        lines = "\n".join(str(i+1) for i in range(int(line_count)))
        self.line_numbers.insert('1.0', lines)
        self.line_numbers.config(state='disabled')

    def setup_console(self):
        sys.stdout = Redirector(self.console)
        sys.stderr = Redirector(self.console)
        self.console.insert(tk.END, "# Python Console Ready\n")

    def embed_pygame(self):
        self.pygame_thread = threading.Thread(target=self.start_pygame)
        self.pygame_thread.daemon = True
        self.pygame_thread.start()

    def start_pygame(self):
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()

        try:
            screen = pygame.display.set_mode((500, 600))
            pygame.display.set_caption("Sajilo Playground")

            character_image = pygame.image.load("/mnt/data/alien.png").convert_alpha()
            move_sound = pygame.mixer.Sound("/mnt/data/move.mp3")
            pygame.mixer.music.load("/mnt/data/background_sound.mp3")
            pygame.mixer.music.play(-1)
        except Exception as e:
            print("Error loading media:", e)
            return

        x, y = 100, 100
        speed = 5
        clock = pygame.time.Clock()
        running = True

        while running:
            screen.fill((255, 255, 255))
            screen.blit(character_image, (x, y))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                x += speed
                move_sound.play()
            elif keys[pygame.K_LEFT]:
                x -= speed
                move_sound.play()
            elif keys[pygame.K_UP]:
                y -= speed
                move_sound.play()
            elif keys[pygame.K_DOWN]:
                y += speed
                move_sound.play()

            clock.tick(30)

        pygame.quit()

    def execute_editor_code(self):
        user_code = self.editor.get("1.0", tk.END)
        try:
            exec(user_code, globals())
        except Exception as e:
            print("Execution Error:", e)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = SajiloApp(root)
    app.run()
