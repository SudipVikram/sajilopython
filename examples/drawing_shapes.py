from sajilopython import background, draw, start

background.color('darkblue')

# Drawing shapes manually
draw.line((100, 100), (300, 100), color='yellow')
draw.rectangle((150, 150, 200, 100), color='green', fill=True)
draw.circle((400, 400), 50, color='red', fill=True)
draw.ellipse((500, 200, 100, 50), color='white')
draw.arc((600, 300, 80, 60), 0, 3.14, color='orange')
draw.polygon([(650, 100), (700, 150), (750, 100)], color='pink')

draw.grid()

start()
