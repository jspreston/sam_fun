import argparse
import turtle


def koch_curve(t, order, size):
    if order == 0:
        t.forward(size)
    else:
        size /= 3.0
        koch_curve(t, order - 1, size)
        t.left(60)
        koch_curve(t, order - 1, size)
        t.right(120)
        koch_curve(t, order - 1, size)
        t.left(60)
        koch_curve(t, order - 1, size)


def koch_snowflake(t, order, size):
    for _ in range(3):
        koch_curve(t, order, size)
        t.right(120)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--order", default=3, type=int)
    args = parser.parse_args()

    # Set up the turtle
    t = turtle.Turtle()
    t.speed(0)  # Fastest speed
    window = turtle.Screen()
    window.bgcolor("white")

    # Set window size
    window.setup(width=600, height=600)

    # Adjust turtle position to center the fractal
    start = (-window.window_width() / 2, window.window_height() / 2)
    size = 200
    t.penup()
    t.goto(
        start[0] + size, start[1] - size
    )  # Move to a more centered starting position
    t.pendown()

    colors = ["red", "blue", "green", "orange", "purple", "yellow", "cyan", "magenta"]
    # Draw a Koch snowflake of order 3 and size 300
    for order in range(args.order):
        color = colors[order % len(colors)]
        t.color(color)
        koch_snowflake(t, order, size)

    # Close window on click
    window.exitonclick()
