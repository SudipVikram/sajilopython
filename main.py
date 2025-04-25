from sajilopython import cat, dog, start, delay, shark, sun, spaceship, background, green


background.color('lightgreen')
# Load both animals
cat.load()
dog.load()
shark.goto(200,300)
shark.load()
sun.load()
spaceship.load()

# Assign control keys
cat.keys()              # Arrow keys for cat
dog.wasd()              # WASD keys for dog

# Looping: the cat will loop right, dog will loop down
cat.loop_right()
dog.loop_down()

# Uncomment these lines if you also want to test bounding:
# cat.bound()
# dog.bound()

# Move cat to a random position at the start
cat.goto_random()
background.load('green')

# Dog performs a dance before the game starts
dog.dance(speed=80)

# Delay to see the dance before entering the loop
delay(1000)

# Start the game loop
start()


