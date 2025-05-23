"""
------------------------------------------------------------------------------
Maze SubLibrary for SajiloPython
Author       : Sudip Vikram Adhikari
Company      : Beyond Apogee
Description  : This module provides the MazeGame class and related functions
               for loading, running, and tracking maze-based coding challenges
               in the SajiloPython framework.

Short Desc   : Maze engine with levels, collectibles, player progress, and score tracking.

Features     :
- Multiple maze levels with walls, paths, start/end points.
- Collectibles system (stars, coins, cherries).
- Command queue system for student-controlled movements.
- Player name registration with high-score protection.
- JSON file storage for player records and scores.
- Sound effects and dynamic graphics.

License      : MIT License
------------------------------------------------------------------------------
"""

import pygame
import os
from . import screen
import json

# Tile Definitions
WALL = "1"
PATH = "0"
START = "S"
END = "E"
COIN = "$"
STAR = "*"
CHERRY = "C"

# Example Mazes
maze1 = [
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1"],
    ["1","S","0","0","0","*","0","0","$","0","C","0","1","1"],
    ["1","1","1","0","1","1","1","0","1","1","1","1","1","1"],
    ["1","$","0","0","C","0","*","0","$","0","C","1","1","1"],
    ["1","1","0","1","1","1","1","1","1","1","0","1","1","1"],
    ["1","*","0","0","0","$","0","0","*","0","0","1","1","1"],
    ["1","1","1","1","0","1","1","1","1","0","1","1","1","1"],
    ["1","C","0","0","0","C","0","0","$","0","E","1","1","1"],
    ["1","1","1","0","1","1","1","0","1","1","1","1","1","1"],
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1"]
]

maze2 = [
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1"],
    ["1","S","0","$","0","*","1","0","C","0","0","0","1","1"],
    ["1","0","1","0","1","1","1","0","1","1","1","0","1","1"],
    ["1","0","0","0","0","$","0","0","*","0","1","0","1","1"],
    ["1","1","1","1","0","1","1","1","1","0","1","1","1","1"],
    ["1","*","0","0","0","0","0","C","0","0","0","0","1","1"],
    ["1","1","0","1","1","1","1","1","1","1","1","0","1","1"],
    ["1","C","0","0","0","0","*","0","$","0","E","0","1","1"],
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1"],
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1"]
]

maze3 = [
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1"],
    ["1","S","0","1","0","*","1","0","C","1","0","0","E","1"],
    ["1","0","1","0","1","1","1","0","1","1","1","0","1","1"],
    ["1","0","0","0","0","$","0","0","*","0","1","0","1","1"],
    ["1","1","1","1","0","1","1","1","1","0","1","1","1","1"],
    ["1","*","0","0","0","0","0","C","0","0","0","0","1","1"],
    ["1","1","0","1","1","1","1","1","1","1","1","0","1","1"],
    ["1","C","0","0","0","0","*","0","$","0","E","0","1","1"],
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1"],
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1"]
]

maze4 = [
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1"],
    ["1","S","0","0","*","0","1","0","$","0","C","0","0","1"],
    ["1","1","1","0","1","1","1","0","1","1","1","0","1","1"],
    ["1","$","0","0","C","0","*","0","$","0","C","0","1","1"],
    ["1","1","0","1","1","1","1","1","1","1","0","1","1","1"],
    ["1","*","0","0","0","$","0","0","*","0","0","1","1","1"],
    ["1","1","1","1","0","1","1","1","1","0","1","1","1","1"],
    ["1","C","0","0","0","C","0","0","$","0","E","0","0","1"],
    ["1","1","1","0","1","1","1","0","1","1","1","1","1","1"],
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1"]
]

maze5 = [
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1"],
    ["1","S","0","$","0","*","1","0","C","0","0","0","0","1"],
    ["1","0","1","0","1","1","1","0","1","1","1","0","1","1"],
    ["1","0","0","0","0","$","0","0","*","0","1","0","1","1"],
    ["1","1","1","1","0","1","1","1","1","0","1","1","1","1"],
    ["1","*","0","0","0","0","0","C","0","0","0","0","1","1"],
    ["1","1","0","1","1","1","1","1","1","1","1","0","1","1"],
    ["1","C","0","0","0","0","*","0","$","0","E","0","1","1"],
    ["1","1","1","0","1","1","1","0","1","1","1","1","1","1"],
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1"]
]

maze6 = [
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1"],
    ["1","S","0","0","0","*","0","0","$","0","C","0","0","1"],
    ["1","0","1","1","1","1","1","1","1","1","1","1","0","1"],
    ["1","0","0","*","0","C","0","0","0","*","0","0","0","1"],
    ["1","1","1","0","1","1","1","1","1","0","1","1","1","1"],
    ["1","$","0","0","$","0","C","0","*","0","$","0","1","1"],
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1"],
    ["1","C","0","0","0","0","0","0","0","0","E","0","0","1"],
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1"],
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1"]
]

maze7 = [
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1"],
    ["1","S","0","*","0","0","1","0","$","0","C","0","0","1"],
    ["1","0","1","1","1","0","1","1","1","1","1","0","1","1"],
    ["1","0","0","0","C","0","*","0","$","0","C","0","1","1"],
    ["1","1","0","1","1","1","1","1","1","1","0","1","1","1"],
    ["1","*","0","0","0","$","0","0","*","0","0","0","1","1"],
    ["1","1","1","1","0","1","1","1","1","0","1","0","1","1"],
    ["1","C","0","0","0","C","0","0","$","0","E","0","0","1"],
    ["1","1","1","0","1","1","1","0","1","1","1","1","1","1"],
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1"]
]

maze8 = [
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1"],
    ["1","S","0","0","0","*","0","0","$","0","C","0","0","1"],
    ["1","1","1","1","1","0","1","1","1","1","1","0","1","1"],
    ["1","$","0","0","C","0","*","0","$","0","C","0","1","1"],
    ["1","1","0","1","1","1","1","1","1","1","0","1","1","1"],
    ["1","*","0","0","0","$","0","0","*","0","0","0","1","1"],
    ["1","1","1","1","0","1","1","1","1","0","1","0","1","1"],
    ["1","C","0","0","0","C","0","0","$","0","E","0","0","1"],
    ["1","1","1","0","1","1","1","0","1","1","1","1","1","1"],
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1"]
]

maze9 = [
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1"],
    ["1","S","0","*","0","0","1","0","$","0","C","0","0","1"],
    ["1","0","1","0","1","1","1","0","1","1","1","0","1","1"],
    ["1","0","0","0","0","$","0","0","*","0","1","0","1","1"],
    ["1","1","1","1","0","1","1","1","1","0","1","1","1","1"],
    ["1","*","0","0","0","0","0","C","0","0","0","0","1","1"],
    ["1","1","0","1","1","1","1","1","1","1","1","0","1","1"],
    ["1","C","0","0","0","0","*","0","$","0","E","0","1","1"],
    ["1","1","1","0","1","1","1","0","1","1","1","1","1","1"],
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1"]
]

maze10 = [
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1"],
    ["1","S","0","0","*","0","1","0","$","0","C","0","0","1"],
    ["1","0","1","1","1","0","1","1","1","1","1","0","1","1"],
    ["1","0","0","0","C","0","*","0","$","0","C","0","1","1"],
    ["1","1","1","0","1","1","1","1","1","1","0","1","1","1"],
    ["1","*","0","0","0","$","0","0","*","0","0","0","1","1"],
    ["1","1","1","1","0","1","1","1","1","0","1","0","1","1"],
    ["1","C","0","0","0","C","0","0","$","0","E","0","0","1"],
    ["1","1","1","0","1","1","1","0","1","1","1","1","1","1"],
    ["1","1","1","1","1","1","1","1","1","1","1","1","1","1"]
]


TILE_SIZE = 64

# Getting the absolute path to the folder containing this script
base_path = os.path.dirname(os.path.abspath(__file__))

# Building the absolute path to the assets folder
assets_folder = os.path.join(base_path, "assets")

render_enabled = False

# Load images and sounds
wall_img = pygame.image.load(os.path.join(assets_folder, "tiles/wall.png")).convert_alpha()
coin_img = pygame.image.load(os.path.join(assets_folder, "tiles/coin.png")).convert_alpha()
star_img = pygame.image.load(os.path.join(assets_folder, "tiles/star.png")).convert_alpha()
cherry_img = pygame.image.load(os.path.join(assets_folder, "tiles/cherry.png")).convert_alpha()

pygame.mixer.init()
collect_sound = pygame.mixer.Sound(os.path.join(assets_folder, "sounds/collect.mp3"))
win_sound = pygame.mixer.Sound(os.path.join(assets_folder, "sounds/win.mp3"))

# Points for each item
POINTS = {COIN: 5, STAR: 10, CHERRY: 20}

all_mazes = [maze1, maze2, maze3, maze4, maze5, maze6, maze7, maze8, maze9, maze10]
current_level_index = 0
current_maze = None

# Persistent Score
total_score = 0

class MazeGame:
    def __init__(self, maze_map):
        self.maze_map = maze_map
        self.screen = screen
        self.collectibles = []
        self.start_pos = (0, 0)
        self.end_pos = (0, 0)
        self.level_score = 0
        self.won = False
        self.stars_collected = 0
        self.coins_collected = 0
        self.cherries_collected = 0
        self.character_x = 0
        self.character_y = 0
        self.character_direction = 1   # right, e.g., 0=up,1=right,2=down,3=left
        self.visited_tiles = set()
        #base_path = os.path.join(assets_folder, "characters")
        #self.char_img = pygame.image.load(os.path.join(base_path, "char.png")).convert_alpha()
        self.base_path = os.path.join(assets_folder, "characters")
        self.character_images = {
            0: pygame.image.load(os.path.join(self.base_path, "maze_player_up.png")).convert_alpha(),
            1: pygame.image.load(os.path.join(self.base_path, "maze_player_right.png")).convert_alpha(),
            2: pygame.image.load(os.path.join(self.base_path, "maze_player_down.png")).convert_alpha(),
            3: pygame.image.load(os.path.join(self.base_path, "maze_player_left.png")).convert_alpha(),
        }
        self.find_positions()
        self.character_x, self.character_y = self.start_pos
        self.visited_tiles.add(self.start_pos)
        self.render_enabled = False
        self.command_queue = []  # ← NEW
        self.command_delay = 10  # frames between steps
        self.command_timer = 0   # counter
        self.animation_speed = 5 # pixels per frame for smooth movement
        self.target_x = self.character_x
        self.target_y = self.character_y
        self.icon_star = pygame.transform.scale(pygame.image.load(os.path.join(assets_folder, "tiles/star.png")),
                                                (20, 20))
        self.icon_coin = pygame.transform.scale(pygame.image.load(os.path.join(assets_folder, "tiles/coin.png")),
                                                (20, 20))
        self.icon_cherry = pygame.transform.scale(pygame.image.load(os.path.join(assets_folder, "tiles/cherry.png")),
                                                  (20, 20))
        self.icon_score = pygame.transform.scale(pygame.image.load(os.path.join(assets_folder, "tiles/score.png")),
                                                 (20, 20))
        self.icon_level = pygame.transform.scale(pygame.image.load(os.path.join(assets_folder, "tiles/level.png")),
                                                 (20, 20))
        self.load_scores()
        # the player's name
        self.current_player = None
        self.move_sound = pygame.mixer.Sound(os.path.join(assets_folder, "sounds/boing.mp3"))
        self.turn_sound = pygame.mixer.Sound(os.path.join(assets_folder, "sounds/newlevel.mp3"))

    class Player:
        def __init__(self,parent):
            self.parent = parent
            self.command = None

        def move_forward(self,arg=None):
            self.command = "move_forward"
            self.parent.command_queue.append((self.command, arg))
        def turn_left(self,arg=None):
            self.command = "turn_left"
            self.parent.command_queue.append((self.command, arg))
        def turn_right(self,arg=None):
            self.command = "turn_right"
            self.parent.command_queue.append((self.command, arg))

    def command(self, command, arg=None):
        self.command_queue.append((command, arg))

    def has_pending_commands(self):
        return len(self.command_queue) > 0

    def execute_next_command(self):
        if self.command_timer > 0:
            self.command_timer -= 1
            return

        if self.has_pending_commands():
            command, arg = self.command_queue.pop(0)
            if command == "move_forward":
                if arg is None or arg <= 0:
                    return  # skip invalid or zero steps
                self.move_forward(1)
                if arg > 1:
                    self.command_queue.insert(0, ("move_forward", arg - 1))
            elif command == "turn_left":
                self.turn_left()
            elif command == "turn_right":
                self.turn_right()
            self.command_timer = self.command_delay

    # for score updates
    def load_scores(self):
        try:
            with open("maze_scores.json", "r") as f:
                self.scores = json.load(f)
        except FileNotFoundError:
            self.scores = {
                "player_name": "",
                "highest_total_score": 0,
                "levels_completed": [],
                "collectibles": {"stars": 0, "coins": 0, "cherries": 0}
            }

    def save_scores(self):
        with open("maze_scores.json", "w") as f:
            json.dump(self.scores, f, indent=4)

    # player name check
    def player_name(self, name):
        if name == self.scores["player_name"]:
            print("This name already holds the highest score! Please choose a different name.")
            return
        if name.strip() == "":
            print("Player name cannot be empty!")
            return
        self.current_player = name

    def has_player_name(self):
        return self.current_player is not None and str(self.current_player).strip() != ""

    def draw_error_message(self, message):
        font = pygame.font.SysFont("Arial", 20)
        text_surface = font.render(message, True, (255, 0, 0))
        screen_width = self.screen.get_width()
        text_rect = text_surface.get_rect(center=(screen_width // 2, self.screen.get_height() // 2))
        self.screen.blit(text_surface, text_rect)

    def load(self):
        self.render_enabled = True
        '''global current_maze
        current_maze = self.maze_map
        return self.maze_map'''
        load_maze(self.maze_map)
        return  self.maze_map

    def is_render_enabled(self):
        return self.render_enabled

    def show_maze(self):
        self.render_enabled = True

    def hide_maze(self):
        self.render_enabled = False

    def find_positions(self):
        for y, row in enumerate(self.maze_map):
            for x, cell in enumerate(row):
                if cell == START:
                    self.start_pos = (x, y)
                if cell == END:
                    self.end_pos = (x, y)
                if cell in [COIN, STAR, CHERRY]:
                    self.collectibles.append((x, y, cell))

    def draw_maze(self):
        for y, row in enumerate(self.maze_map):
            for x, cell in enumerate(row):
                px, py = x * TILE_SIZE, y * TILE_SIZE
                if cell == WALL:
                    self.screen.blit(wall_img, (px, py))
                elif cell in [PATH, START, END]:
                    pygame.draw.rect(self.screen, (0, 0, 0), (px, py, TILE_SIZE, TILE_SIZE))
                if cell == END:
                    pygame.draw.rect(self.screen, (0, 255, 0), (px, py, TILE_SIZE, TILE_SIZE))
        # Draw collectibles
        for x, y, item in self.collectibles:
            px, py = x * TILE_SIZE, y * TILE_SIZE
            if item == COIN:
                self.screen.blit(coin_img, (px, py))
            elif item == STAR:
                self.screen.blit(star_img, (px, py))
            elif item == CHERRY:
                self.screen.blit(cherry_img, (px, py))
        # Draw trace dots
        for x, y in self.visited_tiles:
            center_x = x * TILE_SIZE + TILE_SIZE // 2
            center_y = y * TILE_SIZE + TILE_SIZE // 2
            pygame.draw.circle(self.screen, (200, 200, 200), (center_x, center_y), 4)
        # Draw character
        '''char_px, char_py = self.character_x * TILE_SIZE, self.character_y * TILE_SIZE
        self.screen.blit(self.char_img, (char_px, char_py))'''
        char_px, char_py = self.character_x * TILE_SIZE, self.character_y * TILE_SIZE
        char_img = self.character_images[self.character_direction]
        self.screen.blit(char_img, (char_px, char_py))

    def move_forward(self, steps=1):
        for _ in range(steps):
            next_x, next_y = self.character_x, self.character_y
            if self.character_direction == 0:
                next_y -= 1
            elif self.character_direction == 1:
                next_x += 1
            elif self.character_direction == 2:
                next_y += 1
            elif self.character_direction == 3:
                next_x -= 1
            if 0 <= next_x < len(self.maze_map[0]) and 0 <= next_y < len(self.maze_map):
                if self.maze_map[next_y][next_x] != WALL:
                    self.character_x, self.character_y = next_x, next_y
                    self.visited_tiles.add((next_x, next_y))
                    self.check_collectibles(next_x, next_y)
                    self.check_goal(next_x, next_y)
                    print(f"Moving Forward to ({next_x}, {next_y}), cell={self.maze_map[next_y][next_x]}")
                    self.move_sound.play()  #  play boing sound

    def turn_left(self):
        self.character_direction = (self.character_direction - 1) % 4
        print("Turning Left")
        self.turn_sound.play()  #  play drop sound

    def turn_right(self):
        self.character_direction = (self.character_direction + 1) % 4
        print("Turning Right")
        self.turn_sound.play()  #  play drop sound

    def check_collectibles(self, player_x, player_y):
        collected = None
        for collectible in self.collectibles:
            x, y, item = collectible
            if x == player_x and y == player_y:
                collected = collectible
                self.level_score += POINTS[item]
                collect_sound.play()
                if item == STAR:
                    self.stars_collected += 1
                elif item == COIN:
                    self.coins_collected += 1
                elif item == CHERRY:
                    self.cherries_collected += 1
                break
        if collected:
            self.collectibles.remove(collected)

    def check_goal(self, player_x, player_y):
        if (player_x, player_y) == self.end_pos and not self.won:
            win_sound.play()
            self.won = True
            print("Congratulations! Level completed!")
            print(f"Level {current_level_index + 1} complete! Loading next level...")
            total = total_score + self.level_score
            if total > self.scores["highest_total_score"]:
                self.scores["player_name"] = self.current_player
                self.scores["highest_total_score"] = total
                self.scores["levels_completed"] = list(range(1, current_level_index + 2))  # include next level

                self.scores["collectibles"]["stars"] = self.stars_collected
                self.scores["collectibles"]["coins"] = self.coins_collected
                self.scores["collectibles"]["cherries"] = self.cherries_collected

                self.save_scores()
            self.next_level()  # letting this to be called by the user

    # bottom info
    def draw_bottom_info(self):
        pygame.draw.rect(self.screen, (0, 30, 30), (125, 550, 550, 80))  # larger box
        font = pygame.font.SysFont("Arial", 20)
        text = (f"Player: {self.current_player} | "
                f"Highest Scorer: {self.scores['player_name']} | Highest Score: {self.scores['highest_total_score']}")
        text_surface = font.render(text, True, (255, 255, 255))
        screen_width = self.screen.get_width()
        text_rect = text_surface.get_rect(center=(screen_width // 2, self.screen.get_height() - 20))
        self.screen.blit(text_surface, text_rect)

        # Collectible icons and counts
        x_start = screen_width // 2 - 60
        y = self.screen.get_height() - 50
        self.screen.blit(self.icon_level, (x_start-50, y))
        self.screen.blit(self.icon_star, (x_start, y))
        self.screen.blit(self.icon_coin, (x_start + 50, y))
        self.screen.blit(self.icon_cherry, (x_start + 100, y))

        level_count = font.render(str(len(self.scores.get('levels_completed', []))), True, (255, 255, 255))
        star_count = font.render(str(self.scores['collectibles']['stars']), True, (255, 255, 255))
        coin_count = font.render(str(self.scores['collectibles']['coins']), True, (255, 255, 255))
        cherry_count = font.render(str(self.scores['collectibles']['cherries']), True, (255, 255, 255))

        self.screen.blit(level_count, (x_start-25, y))
        self.screen.blit(star_count, (x_start + 25, y))
        self.screen.blit(coin_count, (x_start + 75, y))
        self.screen.blit(cherry_count, (x_start + 125, y))

    def next_level(self):
        '''global current_level_index, current_maze
        current_level_index += 1
        if current_level_index < len(all_mazes):
            current_maze = load_maze(all_mazes[current_level_index])
        else:
            print("All levels complete!")'''
        if not self.won:
            print("X You must finish the current level before moving on!")
            return
        global total_score, current_level_index, all_mazes, current_maze
        total_score += self.get_score()
        current_level_index += 1
        if current_level_index >= len(all_mazes):
            print("All levels completed! Final Score:", total_score)
            return
        #current_maze = MazeGame(all_mazes[current_level_index])
        self.maze_map = all_mazes[current_level_index]  # loading map for the next level
        '''self.character_x, self.character_y = self.start_pos # resetting the character to the starting point
        self.character_direction = 1  # right # setting the current start direction
        self.visited_tiles = set()  # clearing all the set tiles from before
        self.visited_tiles.add(self.start_pos)'''
        self.reset()
        self.load()
        print(f"Welcome to Level {current_level_index + 1}!")

    def reset(self):
        self.character_x, self.character_y = self.start_pos
        self.character_direction = 1  # right
        self.visited_tiles = set()
        self.visited_tiles.add(self.start_pos)
        self.won = False

    def get_score(self):
        return self.level_score

    def has_won(self):
        return self.won

    def render_scoreboard(self):
        pygame.draw.rect(self.screen, (30, 30, 30), (5, 5, 80, 150))  # larger box

        font = pygame.font.SysFont("Arial", 20)
        y_start = 20

        # Total score icon and count
        self.screen.blit(self.icon_score, (10, y_start))
        total = total_score + self.level_score
        total_text = font.render(str(total), True, (255, 255, 255))
        self.screen.blit(total_text, (40, y_start))

        # Level icon and count
        self.screen.blit(self.icon_level, (10, y_start + 25))
        level_text = font.render(str(current_level_index + 1), True, (255, 255, 255))
        self.screen.blit(level_text, (40, y_start + 25))

        # Collectible indicators with icons and counts
        y_start = 70
        self.screen.blit(self.icon_star, (10, y_start))
        self.screen.blit(self.icon_coin, (10, y_start + 25))
        self.screen.blit(self.icon_cherry, (10, y_start + 50))

        font = pygame.font.SysFont("Arial", 20)
        star_text = font.render(str(self.stars_collected), True, (255, 255, 255))
        coin_text = font.render(str(self.coins_collected), True, (255, 255, 255))
        cherry_text = font.render(str(self.cherries_collected), True, (255, 255, 255))

        self.screen.blit(star_text, (40, y_start))
        self.screen.blit(coin_text, (40, y_start + 25))
        self.screen.blit(cherry_text, (40, y_start + 50))


maze = MazeGame(maze1)
player = maze.Player(maze)

def get_current_maze():
    global current_maze
    return current_maze

def load_maze(maze, render=True):
    global current_maze, render_enabled
    current_maze = MazeGame(maze)
    render_enabled = render
    return current_maze

def next_level():
    global current_level_index, current_maze, total_score
    if not current_maze.has_won():
        print("X You must finish the current level before moving on!")
        return
    total_score += current_maze.get_score()
    current_level_index += 1
    if current_level_index >= len(all_mazes):
        print("All levels completed! Final Score:", total_score)
        return
    current_maze = MazeGame(all_mazes[current_level_index], current_maze.screen)
    print(f"Welcome to Level {current_level_index + 1}!")
