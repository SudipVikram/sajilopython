import pygame
import sys
import time

# Set up window
pygame.init()
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kid's Python Interpreter")

# Character setup
character = pygame.Rect(100, 500, 50, 50)
color = (100, 200, 255)

font = pygame.font.SysFont('Arial', 24)

# Text log
message_log = []

# Python commands dictionary
def move_right():
    character.x += 50

def move_left():
    character.x -= 50

def jump():
    character.y -= 80
    redraw()
    time.sleep(0.3)
    character.y += 80

def say(msg):
    message_log.append(str(msg))
    if len(message_log) > 5:
        message_log.pop(0)

def redraw():
    win.fill((30, 30, 30))
    pygame.draw.rect(win, color, character)

    # Display messages
    y = 20
    for msg in message_log:
        text = font.render(str(msg), True, (255, 255, 255))
        win.blit(text, (10, y))
        y += 30

    pygame.display.update()

def safe_exec(user_code):
    try:
        # Only expose safe functions
        exec(user_code, {
            'move_right': move_right,
            'move_left': move_left,
            'jump': jump,
            'say': say
        })
    except Exception as e:
        say("Error!")

# Game loop
running = True
code = ""

while running:
    redraw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle key typing
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                safe_exec(code)
                code = ""
            elif event.key == pygame.K_BACKSPACE:
                code = code[:-1]
            else:
                code += event.unicode

    # Show current typed code
    text_input = font.render(">>> " + code, True, (0, 255, 0))
    win.blit(text_input, (10, HEIGHT - 40))
    pygame.display.update()

pygame.quit()
sys.exit()
