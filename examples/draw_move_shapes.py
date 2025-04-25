from sajilopython import Shape, background, draw, start

background.color('black')

myrect = Shape('rectangle', position=(200, 200), size=(100, 60), color='red')
myrect.load()
myrect.keep_moving_right()
myrect.bound()

mycircle = Shape('circle', position=(400, 300), size=(80, 80), color='blue')
mycircle.load()
mycircle.loop_left()

draw.grid()

start()
