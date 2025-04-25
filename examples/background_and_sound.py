from sajilopython import background, sound, cat, start

background.load('green')         # Assuming green.jpg is in assets/backgrounds
background.opacity(200)

sound.loop('background_music')   # Assuming background_music.mp3 in assets/sounds
sound.volume(5)

cat.load()
cat.keys()

start()
