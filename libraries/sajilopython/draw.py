# sajilopython/draw.py

from .shared import _game, game_content_used

# ✅ Enable content flag to trigger the auto loop
game_content_used = True

class DrawTools:
    def line(self, start, end, color=(255, 255, 255), width=1):
        """
        Draw a line from 'start' to 'end' points.
        """
        global game_content_used
        game_content_used = True  # ✅ Mark that drawing is being used
        _game.draw_line(start=start, end=end, color=color, width=width)

    def rect(self, org, width, height, color=(255, 255, 255), border_thickness=0, border_radius=0):
        """
        Draw a rectangle.
        """
        global game_content_used
        game_content_used = True
        _game.draw_rect(color=color, org=org, width=width, height=height,
                        border_thickness=border_thickness, border_radius=border_radius)

    def arc(self, org, width, height, start_angle, stop_angle, color=(255, 255, 255), border_thickness=1):
        """
        Draw an arc.
        """
        global game_content_used
        game_content_used = True
        _game.draw_arc(color=color, org=org, width=width, height=height,
                       start_angle=start_angle, stop_angle=stop_angle, border_thickness=border_thickness)

    def polygon(self, points, color=(255, 255, 255), border_thickness=0):
        """
        Draw a polygon.
        """
        global game_content_used
        game_content_used = True
        _game.draw_polygon(color=color, points=points, border_thickness=border_thickness)

# ✅ Create the instance that will be imported as 'draw'
draw = DrawTools()