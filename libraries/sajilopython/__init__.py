import pygame
import sys

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SajiloPython")
clock = pygame.time.Clock()

# Global content list to draw
characters = []


class Character:
    def __init__(self, name, org=(100, 100), width=64, height=64, use_image=True):
        self.name = name
        self.color = (255, 255, 255)  # Color kept for compatibility but not used for drawing
        self.x, self.y = org
        self.width = width
        self.height = height
        self.speed = 5
        self.text = ""
        self.jumping = False
        self.jump_height = 50
        self.jump_direction = -1  # -1 for up, 1 for down
        self.jump_progress = 0
        image_path = f"libraries/sajilopython/assets/characters/{self.name}.png"
        if os.path.exists(image_path):
            self.image = pygame.image.load(image_path).convert_alpha()
        else:
            self.image = None

    def center(self):
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT // 2 - self.height // 2

    def move_left(self, speed=5):
        if isinstance(speed, int):
            self.x -= speed
        else:
            self.keep_moving = 'left'
        self.x -= speed

    def forward(self, speed=5):
        if isinstance(speed, int):
            self.x += speed
        else:
            self.keep_moving = 'right'

    def move_right(self, speed=5):
        if isinstance(speed, int):
            self.x += speed
        else:
            self.keep_moving = 'right'
        if isinstance(speed, int):
            self.x += speed
        else:
            self.keep_moving = 'right'
        self.x += speed

    def goto(self, x, y):
        self.x, self.y = x, y

    def say(self, text="Hi!"):
        self.text = text

    def jump(self, height=None):
        if not self.jumping:
            if height is not None:
                self.jump_height = height
            self.jumping = True
            self.jump_progress = 0
            self.jump_direction = -1

    def load(self):
        if self not in characters:
            characters.append(self)
        screen.blit(self.image, (self.x, self.y))
        if self.text:
            font = pygame.font.SysFont("comicsansms", 20)
            label = font.render(self.text, True, (255, 255, 255))
            screen.blit(label, (self.x, self.y - 30))

    def hide(self):
        if self in characters:
            characters.remove(self)

    def dance(self, speed=100):
        # Simple dance: move left and right quickly
        for _ in range(5):
            self.x += 10
            self._refresh()
            pygame.time.delay(speed)
            self.x -= 10
            self._refresh()
            pygame.time.delay(speed)

    def spin(self, speed=100):
        # Simple spin: temporarily change width and height to simulate spin effect
        original_width, original_height = self.width, self.height
        for size in range(5):
            self.width = original_width + size * 5
            self.height = original_height - size * 5
            self._refresh()
            pygame.time.delay(speed)
        self.width, self.height = original_width, original_height

    def _refresh(self):
        if isinstance(background_current, pygame.Surface):
            temp_bg = background_current.copy()
            temp_bg.set_alpha(background_alpha)
            screen.blit(temp_bg, (0, 0))
        elif isinstance(background_current, tuple):
            screen.fill(background_current)
        else:
            screen.fill((0, 0, 0))
        for char in characters:
            char.load()
        pygame.display.update()

    def bounce(self, speed=100):
        # Simple bounce: up and down repeatedly
        for _ in range(3):
            self.y -= 20
            self._refresh()
            pygame.time.delay(speed)
            self.y += 20
            self._refresh()
            pygame.time.delay(speed)

    def wiggle(self, speed=100):
        # Simple wiggle: quick small left-right shake
        for _ in range(6):
            self.x += 5
            self._refresh()
            pygame.time.delay(speed // 2)
            self.x -= 10
            self._refresh()
            pygame.time.delay(speed // 2)
            self.x += 5
            self._refresh()

    def flip(self):
        # Flip horizontally by swapping width and height visually
        self.width, self.height = self.height, self.width
        self._refresh()
        pygame.time.delay(150)
        self.width, self.height = self.height, self.width

    def grow(self, amount=10, speed=100):
        self.width += amount
        self.height += amount
        self._refresh()
        pygame.time.delay(speed)

    def shrink(self, amount=10, speed=100):
        self.width = max(10, self.width - amount)
        self.height = max(10, self.height - amount)
        self._refresh()
        pygame.time.delay(speed)

    def keys(self):
        self.control_scheme = 'arrows'

    def wasd(self):
        self.control_scheme = 'wasd'

    def handle_keys(self):
        keys = pygame.key.get_pressed()
        if hasattr(self, 'control_scheme') and self.control_scheme == 'arrows':
            if keys[pygame.K_LEFT]:
                self.move_left(5)
            if keys[pygame.K_RIGHT]:
                self.forward(5)
            if keys[pygame.K_UP]:
                self.y -= 5
            if keys[pygame.K_DOWN]:
                self.y += 5
        elif hasattr(self, 'control_scheme') and self.control_scheme == 'wasd':
            if keys[pygame.K_a]:
                self.move_left(5)
            if keys[pygame.K_d]:
                self.forward(5)
            if keys[pygame.K_w]:
                self.y -= 5
            if keys[pygame.K_s]:
                self.y += 5

    def bound(self):
        self.bound_to_window = True

    def keep_moving_left(self):
        self.keep_moving = 'left'

    def keep_moving_right(self):
        self.keep_moving = 'right'

    def goto_random(self):
        import random
        self.x = random.randint(0, WIDTH - self.width)
        self.y = random.randint(0, HEIGHT - self.height)

    def keep_moving_up(self):
        self.keep_moving = 'up'

    def keep_moving_down(self):
        self.keep_moving = 'down'

    def loop_left(self):
        self.loop_direction = 'left'

    def loop_right(self):
        self.loop_direction = 'right'

    def loop_up(self):
        self.loop_direction = 'up'

    def loop_down(self):
        self.loop_direction = 'down'

    def stop_loop(self):
        if hasattr(self, 'loop_direction'):
            del self.loop_direction

    def unbind(self):
        if hasattr(self, 'bound_to_window'):
            del self.bound_to_window

    def update(self):
        # Movement (keep moving)
        if hasattr(self, 'keep_moving'):
            if self.keep_moving == 'left':
                self.x -= self.speed
            elif self.keep_moving == 'right':
                self.x += self.speed
            elif self.keep_moving == 'up':
                self.y -= self.speed
            elif self.keep_moving == 'down':
                self.y += self.speed

        # Looping logic (wrapping around the screen)
        if hasattr(self, 'loop_direction'):
            if self.loop_direction == 'left':
                self.x -= self.speed
                if self.x + self.width < 0:
                    self.x = WIDTH
            elif self.loop_direction == 'right':
                self.x += self.speed
                if self.x > WIDTH:
                    self.x = -self.width
            elif self.loop_direction == 'up':
                self.y -= self.speed
                if self.y + self.height < 0:
                    self.y = HEIGHT
            elif self.loop_direction == 'down':
                self.y += self.speed
                if self.y > HEIGHT:
                    self.y = -self.height

        # Bounding (only apply if NOT looping)
        if hasattr(self, 'bound_to_window') and self.bound_to_window and not hasattr(self, 'loop_direction'):
            self.x = max(0, min(WIDTH - self.width, self.x))
            self.y = max(0, min(HEIGHT - self.height, self.y))

        # Jumping logic
        if self.jumping:
            if self.jump_direction == -1:  # Going up
                self.y -= 5
                self.jump_progress += 5
                if self.jump_progress >= self.jump_height:
                    self.jump_direction = 1  # Start going down
            elif self.jump_direction == 1:  # Coming down
                self.y += 5
                self.jump_progress -= 5
                if self.jump_progress <= 0:
                    self.jumping = False
                    self.jump_direction = -1  # Reset for next jump


import os

# Auto-detect and create Animal objects based on 64x64 images in the characters folder
character_folder = "libraries/sajilopython/assets/characters/"
for filename in os.listdir(character_folder):
    if filename.endswith(".png") or filename.endswith(".gif"):
        name = os.path.splitext(filename)[0]  # remove .png or .gif
        image_path = os.path.join(character_folder, filename)
        image = pygame.image.load(image_path)
        if image.get_width() == 64 and image.get_height() == 64:
            globals()[name] = Character(name=name)


def delay(ms):
    pygame.time.delay(ms)


import os

# Background handling
background_images = {}
background_current = None
background_alpha = 255

# Load backgrounds from the backgrounds folder
background_folder = "libraries/sajilopython/assets/backgrounds/"
for filename in os.listdir(background_folder):
    if filename.endswith(".png") or filename.endswith(".gif") or filename.endswith(".jpg"):
        name = os.path.splitext(filename)[0]
        image = pygame.image.load(os.path.join(background_folder, filename)).convert()
        background_images[name] = image


class Background:
    def load(self, name):
        global background_current
        if name in background_images:
            background_current = background_images[name]

    def opacity(self, alpha):
        global background_alpha
        background_alpha = max(0, min(255, alpha))

    def color(self, colorname):
        global background_current
        color_dict = pygame.color.THECOLORS
        background_current = color_dict.get(colorname.lower(), (0, 0, 0))


background = Background()

import pygame.mixer

# Sound handling
pygame.mixer.init()
sound_files = {}
sound_channel = pygame.mixer.Channel(0)
current_sound = None

# Load sounds from the sounds folder
sound_folder = "libraries/sajilopython/assets/sounds/"
for filename in os.listdir(sound_folder):
    if filename.endswith(".wav") or filename.endswith(".mp3"):
        name = os.path.splitext(filename)[0]
        sound_files[name] = pygame.mixer.Sound(os.path.join(sound_folder, filename))


class Sound:
    def load(self, name):
        global current_sound
        if name in sound_files:
            current_sound = sound_files[name]
            sound_channel.play(current_sound)

    def loop(self, name):
        global current_sound
        if name in sound_files:
            current_sound = sound_files[name]
            sound_channel.play(current_sound, loops=-1)

    def volume(self, level):
        volume = max(0.0, min(1.0, level / 10))
        sound_channel.set_volume(volume)

    def stop(self):
        sound_channel.stop()


sound = Sound()


# Drawing shapes and grid
class Shape(Character):
    def __init__(self, shape_type, position=(100, 100), size=(64, 64), color='white'):
        super().__init__(name=shape_type)
        self.shape_type = shape_type
        self.position = position
        self.size = size
        self.color = pygame.color.THECOLORS.get(color.lower(), (255, 255, 255))
        super().__init__(name=shape_type, use_image=False)
        self.shape_type = shape_type
        self.position = position
        self.size = size
        self.color = pygame.color.THECOLORS.get(color.lower(), (255, 255, 255))
        self.image = None

    def load(self):
        if self not in characters:
            characters.append(self)
        if self.shape_type == 'rectangle':
            pygame.draw.rect(screen, self.color, (self.x, self.y, *self.size))
        elif self.shape_type == 'circle':
            pygame.draw.circle(screen, self.color, (self.x + self.size[0] // 2, self.y + self.size[1] // 2),
                               self.size[0] // 2)
        if self.text:
            font = pygame.font.SysFont("comicsansms", 20)
            label = font.render(self.text, True, (255, 255, 255))
            screen.blit(label, (self.x, self.y - 30))


class Draw:
    def line(self, start, end, color='white', width=2):
        color = pygame.color.THECOLORS.get(color.lower(), (255, 255, 255))
        pygame.draw.line(screen, color, start, end, width)

    def rectangle(self, rect, color='white', width=2, fill=False):
        color = pygame.color.THECOLORS.get(color.lower(), (255, 255, 255))
        if fill:
            pygame.draw.rect(screen, color, rect)
        else:
            pygame.draw.rect(screen, color, rect, width)
        pygame.draw.rect(screen, color, rect, width)

    def circle(self, center, radius, color='white', width=2, fill=False):
        color = pygame.color.THECOLORS.get(color.lower(), (255, 255, 255))
        if fill:
            pygame.draw.circle(screen, color, center, radius)
        else:
            pygame.draw.circle(screen, color, center, radius, width)
        pygame.draw.circle(screen, color, center, radius, width)

    def ellipse(self, rect, color='white', width=2):
        color = pygame.color.THECOLORS.get(color.lower(), (255, 255, 255))
        pygame.draw.ellipse(screen, color, rect, width)

    def arc(self, rect, start_angle, end_angle, color='white', width=2):
        color = pygame.color.THECOLORS.get(color.lower(), (255, 255, 255))
        pygame.draw.arc(screen, color, rect, start_angle, end_angle, width)

    def polygon(self, points, color='white', width=2):
        color = pygame.color.THECOLORS.get(color.lower(), (255, 255, 255))
        pygame.draw.polygon(screen, color, points, width)

    def grid(self, spacing=50, color=(0, 255, 0)):
        font = pygame.font.SysFont("comicsansms", 12)
        for x in range(0, WIDTH, spacing):
            pygame.draw.line(screen, color, (x, 0), (x, HEIGHT))
            label = font.render(str(x), True, color)
            screen.blit(label, (x + 2, 2))
        for y in range(0, HEIGHT, spacing):
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))
            label = font.render(str(y), True, color)
            screen.blit(label, (2, y + 2))


draw = Draw()


# Start function to manually begin the game loop
def start():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Proper background handling
        if isinstance(background_current, pygame.Surface):
            temp_bg = background_current.copy()
            temp_bg.set_alpha(background_alpha)
            screen.blit(temp_bg, (0, 0))
        elif isinstance(background_current, tuple):
            screen.fill(background_current)
        else:
            screen.fill((0, 0, 0))

        # Character updates and drawing
        for char in characters:
            char.update()
            char.load()

        pygame.display.update()

        # Handle keys after drawing
        for char in characters:
            char.handle_keys()

        clock.tick(60)
