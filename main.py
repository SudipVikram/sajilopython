from sajilopython import background, cat, start, Shape

# Set a background color or image
background.color('black')
background.load('green')       # If you have 'green.jpg' in your backgrounds folder

# Load the cat character and give it arrow key controls
cat.load()
cat.keys()
cat.say("I'm the Cat!")

# Create a rectangle shape behaving like a character
myrect = Shape('circle')
myrect.load()
myrect.keep_moving_right()
myrect.bound()                  # Keeps the rectangle inside the screen boundary
myrect.jump()
myrect.say("hello there")

# Create a circle shape behaving like a character
mycircle = Shape('circle', position=(500, 400), size=(80, 80), color='blue')
mycircle.load()
mycircle.jump(150)              # The circle jumps once at the start
mycircle.loop_left()           # Circle keeps looping left

# Start the game loop
start()

