import turtle


# Function to draw a triangle
def draw_triangle(points, color, t):
    t.fillcolor(color)
    t.penup()
    t.goto(points[0][0], points[0][1])
    t.pendown()
    t.begin_fill()
    t.goto(points[1][0], points[1][1])
    t.goto(points[2][0], points[2][1])
    t.goto(points[0][0], points[0][1])
    t.end_fill()


# Recursive function to create the Sierpinski Gasket
def sierpinski(points, degree, t):
    colormap = [
        "blue",
        "red",
        "green",
        "white",
        "yellow",
        "violet",
        "orange",
    ]  # List of colors
    draw_triangle(points, colormap[degree], t)  # Draws the main triangle
    if degree > 0:
        # Calculate the midpoints of each side of the triangle
        mid1 = midpoint(points[0], points[1])
        mid2 = midpoint(points[1], points[2])
        mid3 = midpoint(points[2], points[0])

        # Recursively draw the three smaller triangles
        sierpinski([points[0], mid1, mid3], degree - 1, t)
        sierpinski([points[1], mid1, mid2], degree - 1, t)
        sierpinski([points[2], mid2, mid3], degree - 1, t)


# Function to calculate the midpoint between two points
def midpoint(point1, point2):
    return [(point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2]


# Set up the turtle
t = turtle.Turtle()
t.speed(0)
window = turtle.Screen()
window.bgcolor("white")

# Define the vertices of the large outer triangle
points = [[-200, -100], [0, 200], [200, -100]]

# Draw the Sierpinski Gasket with a specified depth (degree of recursion)
sierpinski(points, 5, t)

# Close window on click
window.exitonclick()
