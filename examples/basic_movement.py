from sajilopython import cat, dog, background, draw, start

background.color('skyblue')
draw.grid()

cat.load()
cat.keys()               # Arrow key control

dog.load()
dog.wasd()               # WASD control

cat.say("I'm the Cat!")
dog.say("I'm the Dog!")

start()
