"""import sys,time
lyrics=['🎶sunn le yehi sadaa....',
        '💖kaisi dillagi hai tu....',
        '🤗kaisi bebasi hai tu....',
        '🙌meri jindagi hai tu....',
        '💖meri jindagi hai tu....',
        '(❁´◡`❁)......(^///^)⁕₳............']
delays=[0.9,4.2,4.2,4.6,0.8,4.0]
def type_line(line):
    for char in line :
        print(char,end='',flush=True)
        time.sleep(0.05)
    print()
time.sleep(2)
for i in range(len(lyrics)):
    type_line(lyrics[i])
    time.sleep(delays[i])"""








"""import turtle

screen = turtle.Screen()
screen.bgcolor("white")

t = turtle.Turtle()
t.speed(0)
t.width(2)

colors = ["red", "blue", "green", "orange", "purple", "pink", "yellow"]

# Draw petals
for i in range(36):
    t.color(colors[i % len(colors)])
    t.circle(100)
    t.left(10)

# Draw inner circle
t.penup()
t.goto(0, -50)
t.pendown()
t.color("gold")
t.begin_fill()
t.circle(50)
t.end_fill()

# Draw small decorative dots
t.penup()
for angle in range(0, 360, 30):
    t.goto(0, 0)
    t.setheading(angle)
    t.forward(120)
    t.dot(12, colors[(angle // 30) % len(colors)])

t.hideturtle()
turtle.done()"""







"""import turtle

# Create Screen
screen = turtle.Screen()
screen.bgcolor("black")
screen.title("Beautiful Rangoli")

# Create Turtle
t = turtle.Turtle()
t.speed(0)
t.width(2)

# Rangoli Colors
colors = ["red", "yellow", "green", "cyan", "blue", "magenta", "orange", "white"]

# Draw Rangoli Design
for i in range(72):
    t.pencolor(colors[i % len(colors)])
    t.forward(200)
    t.backward(200)
    t.left(5)

# Draw Flower Pattern
t.penup()
t.goto(0, -50)
t.pendown()

for i in range(36):
    t.pencolor(colors[i % len(colors)])
    t.circle(80)
    t.left(10)

# Draw Center Circle
t.penup()
t.goto(0, -20)
t.pendown()
t.color("gold")
t.begin_fill()
t.circle(20)
t.end_fill()

# Draw Decorative Dots
t.penup()
for angle in range(0, 360, 30):
    t.goto(0, 0)
    t.setheading(angle)
    t.forward(140)
    t.dot(15, colors[(angle // 30) % len(colors)])

t.hideturtle()
turtle.done()"""








"""import turtle

# Screen setup
screen = turtle.Screen()
screen.bgcolor("black")
screen.title("Beautiful Flower Rangoli")

# Turtle setup
t = turtle.Turtle()
t.speed(0)
t.width(2)

colors = ["red", "orange", "yellow", "green",
          "cyan", "blue", "purple", "pink"]

# Draw flower petals
for i in range(180):
    t.pencolor(colors[i % len(colors)])
    t.circle(120)
    t.left(2)

# Draw second layer
for i in range(90):
    t.pencolor(colors[(i + 3) % len(colors)])
    t.circle(70)
    t.left(4)

# Center design
t.penup()
t.goto(0, -25)
t.pendown()

t.color("gold")
t.begin_fill()
t.circle(25)
t.end_fill()

# Decorative dots
t.penup()
for angle in range(0, 360, 15):
    t.goto(0, 0)
    t.setheading(angle)
    t.forward(170)
    t.dot(10, colors[(angle // 15) % len(colors)])

t.hideturtle()
turtle.done()"""







"""import turtle

t = turtle.Turtle()
t.speed(0)
t.pensize(3)
screen = turtle.Screen()
screen.bgcolor("white")

# Face
t.penup()
t.goto(0, -120)
t.pendown()
t.circle(120)

# Left Eye
t.penup()
t.goto(-40, 40)
t.pendown()
t.dot(15, "black")

# Right Eye
t.penup()
t.goto(40, 40)
t.pendown()
t.dot(15, "black")

# Mouth
t.penup()
t.goto(-35, -40)
t.setheading(-60)
t.pendown()
t.circle(40, 120)

# Tilak
t.penup()
t.goto(0, 80)
t.setheading(-90)
t.pendown()
t.color("red")
t.forward(50)

t.hideturtle()
turtle.done()"""










"""import turtle

# Screen Setup
screen = turtle.Screen()
screen.setup(800, 800)
screen.bgcolor("white")
screen.title("Hanuman Ji Sketch")

# Turtle Setup
t = turtle.Turtle()
t.speed(0)
t.pensize(3)
t.color("black")

# Move to starting position
t.penup()
t.goto(0, -220)
t.pendown()

# Face Outline
t.begin_fill()
t.fillcolor("#FFD8A8")

t.left(90)
t.circle(180, 40)
t.circle(80, 60)
t.circle(60, 40)
t.circle(100, 60)
t.circle(60, 50)
t.circle(180, 40)

t.right(180)

t.circle(-180, 40)
t.circle(-60, 50)
t.circle(-100, 60)
t.circle(-60, 40)
t.circle(-80, 60)
t.circle(-180, 40)

t.end_fill()

# Left Ear
t.penup()
t.goto(-160, 20)
t.pendown()

t.begin_fill()
t.circle(35)
t.end_fill()

# Right Ear
t.penup()
t.goto(125, 20)
t.pendown()

t.begin_fill()
t.circle(35)
t.end_fill()

# ==========================
# PART 2 : Eyes, Nose, Mouth & Tilak
# ==========================

# Left Eye
t.penup()
t.goto(-45, 60)
t.setheading(0)
t.pendown()
t.color("black")

t.begin_fill()
t.circle(8)
t.end_fill()

# Right Eye
t.penup()
t.goto(45, 60)
t.pendown()

t.begin_fill()
t.circle(8)
t.end_fill()

# Eyebrows
t.pensize(3)

t.penup()
t.goto(-70, 90)
t.setheading(20)
t.pendown()
t.forward(40)

t.penup()
t.goto(30, 105)
t.setheading(-20)
t.pendown()
t.forward(40)

# Nose
t.penup()
t.goto(0, 45)
t.setheading(-90)
t.pendown()

t.forward(40)

# Nose Curve
t.right(30)
t.circle(15, 120)

# Mouth
t.penup()
t.goto(-35, -25)
t.setheading(-15)
t.pendown()

t.circle(35, 70)

# Smile
t.penup()
t.goto(-20, -40)
t.setheading(-10)
t.pendown()

t.circle(22, 60)

# Tilak
t.penup()
t.goto(0, 120)
t.setheading(-90)
t.pendown()

t.pensize(5)
t.color("red")
t.forward(55)

# Tilak Dot
t.penup()
t.goto(0, 55)
t.dot(10, "red")

# Reset Pen
t.color("black")
t.pensize(3)

# ==========================
# PART 3 : Crown (Mukut)
# ==========================

# Crown Base
t.penup()
t.goto(-90, 170)
t.setheading(0)
t.pendown()

t.color("gold")
t.pensize(3)

t.begin_fill()
t.forward(180)
t.left(90)
t.forward(25)
t.left(90)
t.forward(180)
t.left(90)
t.forward(25)
t.end_fill()

# Crown Spikes
x = -80

for i in range(7):
    t.penup()
    t.goto(x, 195)
    t.setheading(90)
    t.pendown()

    t.begin_fill()
    t.left(30)
    t.forward(35)
    t.right(60)
    t.forward(35)
    t.right(150)
    t.forward(30)
    t.end_fill()

    x += 27

# Crown Jewels
colors = ["red", "blue", "green", "purple", "red", "blue", "green"]

x = -75

for i in range(7):
    t.penup()
    t.goto(x, 178)
    t.dot(12, colors[i])
    x += 25

# Center Jewel
t.penup()
t.goto(0, 210)
t.dot(20, "red")

# Decorative Lines
t.color("black")
t.pensize(2)

for y in [176, 183, 190]:
    t.penup()
    t.goto(-90, y)
    t.setheading(0)
    t.pendown()
    t.forward(180)

# Left Decoration
t.penup()
t.goto(-130, 120)
t.setheading(120)
t.pendown()

for i in range(18):
    t.forward(4)
    t.left(10)

# Right Decoration
t.penup()
t.goto(130, 120)
t.setheading(60)
t.pendown()

for i in range(18):
    t.forward(4)
    t.right(10)

# Reset
t.color("black")
t.pensize(3)

# ==========================
# PART 4 : Gada, Neck & Shoulders
# ==========================

# Neck
t.color("black")
t.pensize(3)

t.penup()
t.goto(-25, -120)
t.setheading(-90)
t.pendown()
t.forward(40)

t.penup()
t.goto(25, -120)
t.setheading(-90)
t.pendown()
t.forward(40)

# Shoulders
t.penup()
t.goto(-25, -160)
t.setheading(210)
t.pendown()
t.circle(150, 40)

t.penup()
t.goto(25, -160)
t.setheading(-30)
t.pendown()
t.circle(-150, 40)

# Chest Ornament
t.penup()
t.goto(0, -170)
t.color("gold")
t.begin_fill()
t.circle(18)
t.end_fill()

t.penup()
t.goto(0, -170)
t.dot(8, "red")

# --------------------------
# Gada Handle
# --------------------------

t.color("brown")
t.pensize(8)

t.penup()
t.goto(170, -80)
t.setheading(-90)
t.pendown()
t.forward(180)

# Gada Head
t.penup()
t.goto(170, 80)
t.color("gold")
t.pensize(2)
t.pendown()

t.begin_fill()
t.circle(35)
t.end_fill()

# Decorative Rings
for r in [25, 15]:
    t.penup()
    t.goto(170, 80-r)
    t.pendown()
    t.circle(r)

# Top Dot
t.penup()
t.goto(170, 150)
t.dot(18, "red")

# Bottom Ring
t.penup()
t.goto(170, -260)
t.color("gold")
t.dot(20)

# Decorative Chain
t.color("gold")
t.pensize(2)

t.penup()
t.goto(0, -188)
t.setheading(-90)
t.pendown()

for i in range(6):
    t.circle(6)
    t.forward(8)

# Reset
t.color("black")
t.pensize(3)

# ==========================
# PART 5 : Halo, Flag & Final Decoration
# ==========================

# Halo (Prabhamandal)
t.penup()
t.goto(0, -40)
t.pendown()

t.color("gold")
t.pensize(5)
t.circle(180)

# Inner Halo
t.penup()
t.goto(0, -20)
t.pendown()

t.pensize(2)
t.circle(160)

# --------------------------
# Flag Pole
# --------------------------

t.penup()
t.goto(-220, -180)
t.setheading(90)
t.pendown()

t.color("brown")
t.pensize(6)
t.forward(260)

# Flag
t.color("orange")
t.begin_fill()

t.right(90)
t.forward(90)
t.right(135)
t.forward(60)
t.right(90)
t.forward(60)

t.end_fill()

# Jai Shree Ram Text
t.penup()
t.goto(-205, 70)
t.color("red")
t.write("JAI SHREE RAM",
        align="left",
        font=("Arial", 14, "bold"))

# --------------------------
# Decorative Flowers
# --------------------------

flower_colors = ["red", "yellow", "pink", "blue"]

positions = [
    (-250, 250),
    (250, 250),
    (-250, -250),
    (250, -250)
]

for x, y in positions:
    t.penup()
    t.goto(x, y)
    t.pendown()

    for i in range(12):
        t.color(flower_colors[i % len(flower_colors)])
        t.circle(15)
        t.left(30)

# --------------------------
# Om Symbol
# --------------------------

t.penup()
t.goto(190, 230)
t.color("darkred")
t.write("ॐ",
        align="center",
        font=("Arial", 28, "bold"))

# --------------------------
# Final Message
# --------------------------

t.penup()
t.goto(0, -330)
t.color("blue")

t.write("|| JAI BAJRANGBALI ||",
        align="center",
        font=("Arial", 18, "bold"))

# Hide Turtle
t.hideturtle()

# Keep Window Open
turtle.done()

t.hideturtle()
turtle.done()"""




"""
import turtle

# Create Screen
screen = turtle.Screen()
screen.title("Hanuman Ji Art - Part 1")
screen.setup(800, 800)
screen.bgcolor("white")

# Create Turtle
t = turtle.Turtle()
t.speed(0)
t.pensize(3)
t.color("black")

# Move to starting position
t.penup()
t.goto(0, -220)
t.pendown()

# Face Outline
t.begin_fill()
t.fillcolor("#FFD8A8")

t.left(90)
t.circle(180, 40)
t.circle(80, 60)
t.circle(60, 40)
t.circle(100, 60)
t.circle(60, 50)
t.circle(180, 40)

t.right(180)

t.circle(-180, 40)
t.circle(-60, 50)
t.circle(-100, 60)
t.circle(-60, 40)
t.circle(-80, 60)
t.circle(-180, 40)

t.end_fill()

# Left Ear
t.penup()
t.goto(-160, 20)
t.pendown()
t.begin_fill()
t.circle(35)
t.end_fill()

# Right Ear
t.penup()
t.goto(125, 20)
t.pendown()
t.begin_fill()
t.circle(35)
t.end_fill()

# Hide Turtle
t.hideturtle()

# Keep Window Open
turtle.done()"""