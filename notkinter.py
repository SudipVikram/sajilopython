import pygame
import sys
import io
import threading

pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 700
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
FONT = pygame.font.SysFont('Courier', 18)

# Setup window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SajiloPython IDE")

# Editor and console area dimensions
editor_rect = pygame.Rect(10, 10, 600, 500)
run_button_rect = pygame.Rect(10, 520, 100, 40)
console_rect = pygame.Rect(10, 570, 980, 120)
game_area_rect = pygame.Rect(620, 10, 370, 500)

# Editor content
editor_text = ""
console_output = ""
cursor_visible = True
cursor_counter = 0

# Redirect stdout to capture print output
class ConsoleOutput(io.StringIO):
    def write(self, text):
        global console_output
        console_output += text

sys.stdout = ConsoleOutput()
sys.stderr = ConsoleOutput()

def draw_textbox(rect, text, bg_color, text_color=BLACK, multiline=True):
    pygame.draw.rect(screen, bg_color, rect)
    lines = text.split("\n") if multiline else [text]
    y = rect.y + 5
    for line in lines:
        txt_surface = FONT.render(line, True, text_color)
        screen.blit(txt_surface, (rect.x + 5, y))
        y += FONT.get_height() + 2

def run_user_code(code):
    global console_output
    console_output = ""
    try:
        exec(code, {})
    except Exception as e:
        print("Execution Error:", e)

running = True
while running:
    screen.fill(WHITE)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if editor_rect.collidepoint(pygame.mouse.get_pos()):
                if event.key == pygame.K_BACKSPACE:
                    editor_text = editor_text[:-1]
                elif event.key == pygame.K_RETURN:
                    editor_text += '\n'
                elif event.key == pygame.K_TAB:
                    editor_text += '    '
                elif event.key <= 127:
                    editor_text += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if run_button_rect.collidepoint(event.pos):
                threading.Thread(target=run_user_code, args=(editor_text,), daemon=True).start()

    # Draw UI
    draw_textbox(editor_rect, editor_text, GRAY)
    pygame.draw.rect(screen, (0, 150, 0), run_button_rect)
    screen.blit(FONT.render("Run", True, WHITE), (run_button_rect.x + 25, run_button_rect.y + 10))
    draw_textbox(console_rect, console_output, BLACK, WHITE)

    # Blinking cursor
    if cursor_visible:
        cursor_x = editor_rect.x + 5 + FONT.size(editor_text.split('\n')[-1])[0]
        cursor_y = editor_rect.y + 5 + len(editor_text.split('\n')[:-1]) * (FONT.get_height() + 2)
        pygame.draw.line(screen, BLACK, (cursor_x, cursor_y), (cursor_x, cursor_y + FONT.get_height()), 2)

    cursor_counter += 1
    if cursor_counter >= 30:
        cursor_visible = not cursor_visible
        cursor_counter = 0

    pygame.display.flip()
    pygame.time.Clock().tick(30)

pygame.quit()
