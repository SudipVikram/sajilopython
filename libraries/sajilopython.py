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


class Animal:
    def __init__(self, color, org=(100, 100), width=60, height=60):
        self.color = color
        self.x, self.y = org
        self.width = width
        self.height = height
        self.speed = 5
        self.text = ""
        self.jumping = False
        self.jump_height = 50
        self.jump_direction = -1  # -1 for up, 1 for down
        self.jump_progress = 0

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
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
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


# Predefined animals
cat = Animal(color=(255, 100, 100))
dog = Animal(color=(100, 100, 255))


def delay(ms):
    pygame.time.delay(ms)


# Start function to manually begin the game loop
def start():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0))
        for char in characters:
            char.update()
            char.load()

        pygame.display.update()
        for char in characters:
            char.handle_keys()

        clock.tick(60)
