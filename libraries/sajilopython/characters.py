# sajilopython/characters.py

import sys
import os
import random
import pygame
from .shared import _game, game_content_used

# ✅ Base path for assets
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def asset_path(*parts):
    return os.path.join(BASE_DIR, "assets", *parts)

# ✅ Sound player
def play_sound(sound_path):
    if sound_path and os.path.exists(sound_path):
        sound = pygame.mixer.Sound(sound_path)
        sound.set_volume(0.5)
        sound.play()

# ✅ Base Character Class
class BaseCharacter:
    def __init__(self, name, image_path, start_pos=(100, 100), sound_effects=None):
        global game_content_used
        game_content_used = True
        self.name = name
        self.character = _game.character(parent=_game, type="image", image_path=image_path, org=start_pos)
        self.sounds = sound_effects or {}

    def move_left(self):
        global game_content_used
        game_content_used = True
        self.character.move_left()

    def move_right(self):
        global game_content_used
        game_content_used = True
        self.character.move_right()

    def jump(self):
        global game_content_used
        game_content_used = True
        x, y = self.character.find_position()
        self.character.update_position(ypos=y - 50)
        if "jump" in self.sounds:
            play_sound(self.sounds["jump"])

    def say(self, text):
        global game_content_used
        game_content_used = True
        _game.draw_text(text=text, xpos=self.character.xpos, ypos=self.character.ypos - 20)

    def dance(self):
        global game_content_used
        game_content_used = True
        moves = [self.move_left, self.move_right, self.jump]
        random.choice(moves)()

    def center(self):
        global game_content_used
        game_content_used = True
        self.character.update_position(xpos=_game.wwidth // 2, ypos=_game.wheight // 2)

    def top_right(self):
        global game_content_used
        game_content_used = True
        self.character.update_position(xpos=_game.wwidth - 100, ypos=0)

    def bottom_left(self):
        global game_content_used
        game_content_used = True
        self.character.update_position(xpos=0, ypos=_game.wheight - 100)

# 🐾 Animal-specific subclasses with unique actions

class Cat(BaseCharacter):
    def meow(self):
        if "meow" in self.sounds:
            play_sound(self.sounds["meow"])

cat = Cat("Cat", asset_path("animals", "cat.png"), sound_effects={"meow": asset_path("sounds", "meow.wav")})

class Dog(BaseCharacter):
    def bark(self):
        if "bark" in self.sounds:
            play_sound(self.sounds["bark"])

dog = Dog("Dog", asset_path("animals", "dog.png"), sound_effects={"bark": asset_path("sounds", "bark.wav")})

class Parrot(BaseCharacter):
    def fly(self):
        if "fly" in self.sounds:
            play_sound(self.sounds["fly"])

parrot = Parrot("Parrot", asset_path("animals", "parrot.png"), sound_effects={"fly": asset_path("sounds", "chirp.wav")})

class Elephant(BaseCharacter):
    def spray_water(self):
        if "spray_water" in self.sounds:
            play_sound(self.sounds["spray_water"])

elephant = Elephant("Elephant", asset_path("animals", "elephant.png"), sound_effects={"spray_water": asset_path("sounds", "spray_water.wav")})

class Rabbit(BaseCharacter):
    def hop(self):
        self.jump()
        if "hop" in self.sounds:
            play_sound(self.sounds["hop"])

rabbit = Rabbit("Rabbit", asset_path("animals", "rabbit.png"), sound_effects={"hop": asset_path("sounds", "hop.wav")})

class Fish(BaseCharacter):
    def swim(self):
        self.move_right()
        if "swim" in self.sounds:
            play_sound(self.sounds["swim"])

fish = Fish("Fish", asset_path("animals", "fish.png"), sound_effects={"swim": asset_path("sounds", "swim.wav")})

class Lion(BaseCharacter):
    def roar(self):
        if "roar" in self.sounds:
            play_sound(self.sounds["roar"])

lion = Lion("Lion", asset_path("animals", "lion.png"), sound_effects={"roar": asset_path("sounds", "roar.wav")})

class Zebra(BaseCharacter):
    def gallop(self):
        self.move_right()
        if "gallop" in self.sounds:
            play_sound(self.sounds["gallop"])

zebra = Zebra("Zebra", asset_path("animals", "zebra.png"), sound_effects={"gallop": asset_path("sounds", "gallop.wav")})

class Turtle(BaseCharacter):
    def crawl(self):
        self.move_right()
        if "crawl" in self.sounds:
            play_sound(self.sounds["crawl"])

turtle = Turtle("Turtle", asset_path("animals", "turtle.png"), sound_effects={"crawl": asset_path("sounds", "crawl.wav")})

class Owl(BaseCharacter):
    def hoot(self):
        if "hoot" in self.sounds:
            play_sound(self.sounds["hoot"])

owl = Owl("Owl", asset_path("animals", "owl.png"), sound_effects={"hoot": asset_path("sounds", "hoot.wav")})

class Cow(BaseCharacter):
    def moo(self):
        if "moo" in self.sounds:
            play_sound(self.sounds["moo"])

cow = Cow("Cow", asset_path("animals", "cow.png"), sound_effects={"moo": asset_path("sounds", "moo.wav")})

class Horse(BaseCharacter):
    def neigh(self):
        if "neigh" in self.sounds:
            play_sound(self.sounds["neigh"])

horse = Horse("Horse", asset_path("animals", "horse.png"), sound_effects={"neigh": asset_path("sounds", "neigh.wav")})

class Monkey(BaseCharacter):
    def swing(self):
        self.jump()
        if "swing" in self.sounds:
            play_sound(self.sounds["swing"])

    def laugh(self):
        if "laugh" in self.sounds:
            play_sound(self.sounds["laugh"])

monkey = Monkey("Monkey", asset_path("animals", "monkey.png"), sound_effects={"swing": asset_path("sounds", "swing.wav"), "laugh": asset_path("sounds", "laugh.wav")})

class Fox(BaseCharacter):
    def sneak(self):
        self.move_left()
        if "sneak" in self.sounds:
            play_sound(self.sounds["sneak"])

fox = Fox("Fox", asset_path("animals", "fox.png"), sound_effects={"sneak": asset_path("sounds", "sneak.wav")})

class Pigeon(BaseCharacter):
    def glide(self):
        if "fly" in self.sounds:
            play_sound(self.sounds["fly"])

pigeon = Pigeon("Pigeon", asset_path("animals", "pigeon.png"), sound_effects={"fly": asset_path("sounds", "glide.wav")})

class Swan(BaseCharacter):
    def float(self):
        self.move_right()
        if "float" in self.sounds:
            play_sound(self.sounds["float"])

swan = Swan("Swan", asset_path("animals", "swan.png"), sound_effects={"float": asset_path("sounds", "float.wav")})

class Dolphin(BaseCharacter):
    def jump(self):
        super().jump()
        if "jump" in self.sounds:
            play_sound(self.sounds["jump"])

dolphin = Dolphin("Dolphin", asset_path("animals", "dolphin.png"), sound_effects={"jump": asset_path("sounds", "jump.wav")})

class Snake(BaseCharacter):
    def slither(self):
        self.move_right()
        if "slither" in self.sounds:
            play_sound(self.sounds["slither"])

    def hiss(self):
        if "hiss" in self.sounds:
            play_sound(self.sounds["hiss"])

snake = Snake("Snake", asset_path("animals", "snake.png"), sound_effects={"slither": asset_path("sounds", "slither.wav"), "hiss": asset_path("sounds", "hiss.wav")})