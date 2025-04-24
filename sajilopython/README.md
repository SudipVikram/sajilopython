
# SajiloPython Library

SajiloPython is a beginner-friendly Python game library built on top of SajiloPyGame, designed to introduce kids to coding through fun and interactive animal characters.

## 📦 Features
- 18 Animal characters, each with unique actions (e.g., `cat.meow()`, `dog.bark()`, `parrot.fly()`)
- Preset backgrounds (`dawn`, `dusk`, `sunshine`)
- Drawing tools (`draw.line()`, `draw.rect()`)
- Easy-to-use syntax for kids: No imports needed from SajiloPyGame, only `from sajilopython import *`

## 🐾 Available Animals & Actions
| Animal     | Action(s)        |
|------------|------------------|
| Cat        | `meow()`         |
| Dog        | `bark()`         |
| Parrot     | `fly()`          |
| Elephant   | `spray_water()`  |
| Rabbit     | `hop()`          |
| Fish       | `swim()`         |
| Lion       | `roar()`         |
| Zebra      | `gallop()`       |
| Turtle     | `crawl()`        |
| Owl        | `hoot()`         |
| Cow        | `moo()`          |
| Horse      | `neigh()`        |
| Monkey     | `swing()`, `laugh()` |
| Fox        | `sneak()`        |
| Pigeon     | `glide()`        |
| Swan       | `float()`        |
| Dolphin    | `jump()`         |
| Snake      | `slither()`, `hiss()` |

## 🚀 Example Usage
```python
from sajilopython import cat, dog, parrot, background, draw

background.load("dawn")

cat.meow()
dog.bark()
parrot.fly()
parrot.say("Hello!")

draw.line((100, 100), (200, 200))
draw.rect((50, 50), 100, 50)
```

## 📂 Folder Structure
```
sajilopython/
│
├── assets/
│   ├── animals/           # Character images
│   ├── backgrounds/       # Background images
│   └── sounds/            # Sound effects
├── characters.py          # Character actions and methods
├── background.py          # Background loader
├── draw.py                # Drawing utilities
├── example.py             # Demo usage file
├── __init__.py            # Easy import setup
└── README.md              # This file
```

## 📃 License
MIT License. Use freely in educational projects.
