from sajilopython import start
from sajilopython.mazes import maze, maze1

maze.load()

# Queue commands
maze.command("move_forward", 2)
maze.command("turn_right")
maze.command("move_forward", 2)
maze.command("turn_left")
maze.command("move_forward", 7)
maze.command("turn_right")
maze.command("move_forward", 2)
maze.command("turn_right")
maze.command("move_forward", 1)
maze.command("turn_left")
maze.command("move_forward", 2)
maze.command("turn_left")
maze.command("move_forward", 1)

#level 1 completed, now starting with level 2
maze.command("move_forward",4)
maze.command("turn_left")
maze.command("turn_left")
maze.command("move_forward",2)
maze.command("turn_left")
maze.command("move_forward",2)


start()
