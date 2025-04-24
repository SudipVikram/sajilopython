# Characters module for sajilopython package
from sajilopygame import sajilopygame
import pygame
import random

# Shared game instance for all characters
_game = sajilopygame()
_game.window_title("SajiloPython")

# Sound player helper
def play_sound(sound_path):
    sound = pygame.mixer.Sound(sound_path)
    sound.set_volume(0.5)
    sound.play()

# Base Character class
class BaseCharacter:
    def __init__(self, name, image_path, start_pos=(100, 100), sound_effects={}):
        self.name = name
        self.character = _game.character(parent=_game, type="image", image_path=image_path, org=start_pos)
        self.sounds = sound_effects

    # Movement Methods
    def move_left(self):
        self.character.move_left()

    def move_right(self):
        self.character.move_right()

    def jump(self):
        x, y = self.character.find_position()
        self.character.update_position(ypos=y - 50)
        if "jump" in self.sounds:
            play_sound(self.sounds["jump"])

    def say(self, text):
        _game.draw_text(text=text, xpos=self.character.xpos, ypos=self.character.ypos - 20)

    def dance(self):
        moves = [self.move_left, self.move_right, self.jump]
        random.choice(moves)()

    # Preset Positions
    def center(self):
        self.character.update_position(xpos=_game.wwidth // 2, ypos=_game.wheight // 2)

    def top_right(self):
        self.character.update_position(xpos=_game.wwidth - 100, ypos=0)

    def bottom_left(self):
        self.character.update_position(xpos=0, ypos=_game.wheight - 100)

# ---- Specific Animal Implementations ---- #

# Cat
class Cat(BaseCharacter):
    def meow(self):
        if "meow" in self.sounds:
            play_sound(self.sounds["meow"])

cat = Cat("Cat", "assets/animals/cat.png", sound_effects={"meow": "assets/sounds/meow.wav"})

# Dog
class Dog(BaseCharacter):
    def bark(self):
        if "bark" in self.sounds:
            play_sound(self.sounds["bark"])

dog = Dog("Dog", "assets/animals/dog.png", sound_effects={"bark": "assets/sounds/bark.wav"})

# Parrot
class Parrot(BaseCharacter):
    def fly(self):
        x, y = self.character.find_position()
        self.character.update_position(ypos=y - 20)
        if "fly" in self.sounds:
            play_sound(self.sounds["fly"])

parrot = Parrot("Parrot", "assets/animals/parrot.png", sound_effects={"fly": "assets/sounds/chirp.wav"})

# Elephant
class Elephant(BaseCharacter):
    def spray_water(self):
        if "spray_water" in self.sounds:
            play_sound(self.sounds["spray_water"])

elephant = Elephant("Elephant", "assets/animals/elephant.png", sound_effects={"spray_water": "assets/sounds/spray_water.wav"})

# Rabbit
class Rabbit(BaseCharacter):
    def hop(self):
        self.jump()
        if "hop" in self.sounds:
            play_sound(self.sounds["hop"])

rabbit = Rabbit("Rabbit", "assets/animals/rabbit.png", sound_effects={"hop": "assets/sounds/hop.wav"})

# Fish
class Fish(BaseCharacter):
    def swim(self):
        self.move_right()
        if "swim" in self.sounds:
            play_sound(self.sounds["swim"])

fish = Fish("Fish", "assets/animals/fish.png", sound_effects={"swim": "assets/sounds/swim.wav"})

# Lion
class Lion(BaseCharacter):
    def roar(self):
        if "roar" in self.sounds:
            play_sound(self.sounds["roar"])

lion = Lion("Lion", "assets/animals/lion.png", sound_effects={"roar": "assets/sounds/roar.wav"})

# Zebra
class Zebra(BaseCharacter):
    def gallop(self):
        self.move_right()
        if "gallop" in self.sounds:
            play_sound(self.sounds["gallop"])

zebra = Zebra("Zebra", "assets/animals/zebra.png", sound_effects={"gallop": "assets/sounds/gallop.wav"})

# Turtle
class Turtle(BaseCharacter):
    def crawl(self):
        self.move_right()
        if "crawl" in self.sounds:
            play_sound(self.sounds["crawl"])

turtle = Turtle("Turtle", "assets/animals/turtle.png", sound_effects={"crawl": "assets/sounds/crawl.wav"})

# Owl
class Owl(BaseCharacter):
    def hoot(self):
        if "hoot" in self.sounds:
            play_sound(self.sounds["hoot"])

owl = Owl("Owl", "assets/animals/owl.png", sound_effects={"hoot": "assets/sounds/hoot.wav"})

# Cow
class Cow(BaseCharacter):
    def moo(self):
        if "moo" in self.sounds:
            play_sound(self.sounds["moo"])

cow = Cow("Cow", "assets/animals/cow.png", sound_effects={"moo": "assets/sounds/moo.wav"})

# Horse
class Horse(BaseCharacter):
    def neigh(self):
        if "neigh" in self.sounds:
            play_sound(self.sounds["neigh"])

horse = Horse("Horse", "assets/animals/horse.png", sound_effects={"neigh": "assets/sounds/neigh.wav"})

# Monkey
class Monkey(BaseCharacter):
    def swing(self):
        self.jump()
        if "swing" in self.sounds:
            play_sound(self.sounds["swing"])
    def laugh(self):
        if "laugh" in self.sounds:
            play_sound(self.sounds["laugh"])

monkey = Monkey("Monkey", "assets/animals/monkey.png", sound_effects={"swing": "assets/sounds/swing.wav", "laugh": "assets/sounds/laugh.wav"})

# Fox
class Fox(BaseCharacter):
    def sneak(self):
        self.move_left()
        if "sneak" in self.sounds:
            play_sound(self.sounds["sneak"])

fox = Fox("Fox", "assets/animals/fox.png", sound_effects={"sneak": "assets/sounds/sneak.wav"})

# Pigeon
class Pigeon(BaseCharacter):
    def glide(self):
        self.fly()

pigeon = Pigeon("Pigeon", "assets/animals/pigeon.png", sound_effects={"fly": "assets/sounds/glide.wav"})

# Swan
class Swan(BaseCharacter):
    def float(self):
        self.move_right()
        if "float" in self.sounds:
            play_sound(self.sounds["float"])

swan = Swan("Swan", "assets/animals/swan.png", sound_effects={"float": "assets/sounds/float.wav"})

# Dolphin
class Dolphin(BaseCharacter):
    def jump(self):
        super().jump()
        if "jump" in self.sounds:
            play_sound(self.sounds["jump"])

dolphin = Dolphin("Dolphin", "assets/animals/dolphin.png", sound_effects={"jump": "assets/sounds/jump.wav"})

# Snake
class Snake(BaseCharacter):
    def slither(self):
        self.move_right()
        if "slither" in self.sounds:
            play_sound(self.sounds["slither"])
    def hiss(self):
        if "hiss" in self.sounds:
            play_sound(self.sounds["hiss"])

snake = Snake("Snake", "assets/animals/snake.png", sound_effects={"slither": "assets/sounds/slither.wav", "hiss": "assets/sounds/hiss.wav"})
