# Draw utilities module for sajilopython package
from sajilopygame import sajilopygame

# Shared game instance
_game = sajilopygame()

class DrawTools:
    def line(self, start, end, color=(255, 255, 255), width=1):
        """
        Draw a line from 'start' to 'end' points.
        Args:
            start (tuple): Starting point (x, y).
            end (tuple): Ending point (x, y).
            color (tuple): RGB color (default: white).
            width (int): Thickness of the line.
        """
        _game.draw_line(start=start, end=end, color=color, width=width)

    def rect(self, org, width, height, color=(255, 255, 255), border_thickness=0, border_radius=0):
        """
        Draw a rectangle.
        Args:
            org (tuple): Top-left corner (x, y).
            width (int): Width of the rectangle.
            height (int): Height of the rectangle.
            color (tuple): RGB color.
            border_thickness (int): Thickness of the border. 0 means filled.
            border_radius (int): Rounded corner radius.
        """
        _game.draw_rect(color=color, org=org, width=width, height=height,
                        border_thickness=border_thickness, border_radius=border_radius)

    def arc(self, org, width, height, start_angle, stop_angle, color=(255, 255, 255), border_thickness=1):
        """
        Draw an arc.
        Args:
            org (tuple): Top-left corner of the bounding rectangle.
            width (int): Width of the bounding rectangle.
            height (int): Height of the bounding rectangle.
            start_angle (float): Start angle in degrees.
            stop_angle (float): Stop angle in degrees.
            color (tuple): RGB color.
            border_thickness (int): Thickness of the arc line.
        """
        _game.draw_arc(color=color, org=org, width=width, height=height,
                       start_angle=start_angle, stop_angle=stop_angle, border_thickness=border_thickness)

    def polygon(self, points, color=(255, 255, 255), border_thickness=0):
        """
        Draw a polygon.
        Args:
            points (list of tuples): List of (x, y) points.
            color (tuple): RGB color.
            border_thickness (int): Thickness of the border. 0 means filled.
        """
        _game.draw_polygon(color=color, points=points, border_thickness=border_thickness)

# Instance of the drawing tool to be directly used
draw = DrawTools()
