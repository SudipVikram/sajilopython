
# SajiloPython Full Tutorial 🐍🚀

Welcome to **SajiloPython**, your fun way to learn Python with animations, characters, sounds, and creative effects! This tutorial will guide you from the basics to awesome effects.

---

## 🟢 Getting Started

- What is SajiloPython?
- Why learning to code is fun?
- Install Python and Pygame.
- Folder structure overview.

```python
print("Hello, SajiloPython World!")
```

---

## 🐾 Meet Your First Character

```python
from sajilopython import cat, start
cat.load()
start()
```

---

## 🚶 Moving the Character

```python
cat.load()
cat.keys()  # Control using arrow keys
start()
```

---

## 👫 Adding Another Friend

```python
from sajilopython import cat, dog, start
cat.load()
cat.keys()
dog.load()
dog.wasd()  # WASD control
start()
```

---

## 💬 Talking Characters

```python
cat.say("Hi, I'm the Cat!")
dog.say("Hello, I'm the Dog!")
```

---

## 🌄 Background Magic

```python
from sajilopython import background
background.color('lightblue')
```

---

## 🎶 Playing Music and Sounds

```python
from sajilopython import sound
sound.loop('background_music')
sound.volume(5)
```

---

## 🦘 Jump Like a Hero!

```python
cat.jump(150)
```

---

## 🕺 Dancing and Spinning

```python
cat.dance(speed=100)
cat.spin(speed=80)
```

---

## 🎉 Amazing Bounce and Flip

```python
cat.bounce(speed=120)
cat.flip()
```

---

## 🔄 Move and Loop Forever

```python
dog.keep_moving_right()
dog.loop_right()
```

---

## 🖌️ Draw Your World (Shapes!)

```python
from sajilopython import draw
draw.line((100, 100), (300, 100), color='yellow')
```

---

## 🟩 Add a Grid for Easy Positioning

```python
draw.grid()
```

---

## 🔳 Filled Shapes

```python
draw.rectangle((150, 150, 200, 100), color='green', fill=True)
draw.circle((300, 300), 50, color='red', fill=True)
```

---

## 🔲 Shapes That Move Like Characters

```python
from sajilopython import Shape
myrect = Shape('rectangle', position=(200, 200), size=(100, 60), color='red')
myrect.load()
myrect.keep_moving_right()
```

---

## 🟠 Shape Jumping and Looping

```python
mycircle = Shape('circle', position=(400, 300), size=(80, 80), color='blue')
mycircle.load()
mycircle.loop_left()
```

---

## 🎲 Random Movements

```python
cat.goto_random()
```

---

## 🔊 Volume Control and Sound Effects

```python
sound.volume(5)
```

---

## 🎭 Combining Everything for a Mini Show

```python
background.color('darkblue')
cat.dance()
myrect.loop_right()
sound.loop('music')
```

---

## 🏆 Final Challenge!

Try to create your own scene mixing:
- Characters
- Shapes
- Sounds
- Backgrounds
- Grids

**Congratulations, you've completed the SajiloPython tutorial! 🎉**

