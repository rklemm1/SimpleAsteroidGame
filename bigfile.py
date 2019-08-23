from tkinter import *
import time
import math
import random


class Menu:
    def __init__(self, master):  # Main menu, has instruction text and button to start the game
        self.master = master
        self.menutext = "Welcome to Simple Asteroids \n \n Controls: " \
                        "\n \n Left/Right Arrow Keys: Rotate \n Space: Shoot                                  \n"

        self.labelframe = Frame(self.master, width=600, height=450)
        self.labelframe.pack_propagate(0)
        self.label = Label(self.labelframe, width=600, height=500, text=self.menutext, bg='black', fg='white', font='Times 16 bold')
        self.label.pack()
        self.labelframe.place(x=0, y=0)
        self.scaleframe = Frame(self.master, width=200, height=150)
        self.scaleframe.pack_propagate(0)
        self.difficulty = IntVar()
        self.scale = Scale(self.scaleframe, width=200, bg='black', fg='white', from_=1, to=10, length=100, variable=self.difficulty)
        self.scale.set(5)
        self.scale.pack()
        self.scaleframe.place(x=0, y=450)
        self.buttonframe = Frame(self.master, width=400, height=150)
        self.buttonframe.pack_propagate(0)
        self.startbutton = Button(self.buttonframe, width=400, height=100, bg='black', fg='white',
                                  text='Start Game', font='Times 20 bold', command=self.new_window)
        self.startbutton.pack()
        self.buttonframe.place(x=200, y=450)
        self.labelframe2 = Frame(self.master, width=200, height=50)
        self.labelframe2.pack_propagate(0)
        self.label2 = Label(self.labelframe2, width=200, height=50, text='Difficulty', bg='black', fg='white', font='Times 16')
        self.label2.pack()
        self.labelframe2.place(x=0, y=550)

    def new_window(self):  # Open up a window on top of current window, start the Game class inside of it
        new_window = Toplevel(self.master)
        new_window.geometry('600x600')
        Game(new_window, self.difficulty)


class Game:
    def __init__(self, master, difficulty):
        self.difficulty = difficulty
        self.master = master
        self.master.focus_set()  # auto-focuses to the new window
        self.canvas = Canvas(self.master, height=600, width=600, bg='black')  # creates blank black canvas in the window
        self.canvas.pack()
        self.ship = Ship(self.canvas, self.difficulty)  # Puts instance of ship in canvas
        self.master.bind('<Left>', self.ship.rotate)  # binds keys to methods of the ship
        self.master.bind('<Right>', self.ship.rotate)
        self.master.bind('<space>', self.ship.shoot)
        self.asteroid = Asteroid(self.canvas, self.ship, self.difficulty)  # Puts the first asteroid on the screen
        self.score = 0
        self.delay = .03
        self.scoretext = self.canvas.create_text(300, 580, fill='white', text=('Score: ' + str(self.score)), font='Times 10')
        while self.ship.isAlive:  # The main loop, keeps game running until ship dies, then displays game over message
            if self.asteroid.isAlive:
                time.sleep(self.delay)  # Delay for calculation and so the game doesn't run too fast
                for rocket in self.ship.rocketarray:  # Rocket movement in for loop to make sure it moves all of them
                    rocket.move()
                bbox = self.asteroid.canvas.bbox(self.asteroid.id)  # finds the rectangle that holds the asteroid
                overlap = self.canvas.find_overlapping(bbox[0], bbox[1], bbox[2], bbox[3])
                # returns what on the canvas overlaps the asteroid
                if len(overlap) > 1:  # if the asteroid overlaps more than just itself
                    if overlap[0] == 1:  # checks if the asteroid overlaps the ship, if true it kills the ship
                        self.ship.kill()
                    else:  # if the asteroid is overlapping anything that is not the ship, destroy the asteroid
                        self.asteroid.kill()
                self.asteroid.move()  # moves asteroid if it is still on the screen
                self.master.update()  # updates everything on the canvas
            else:  # if the asteroid is dead when the loop restarts, increment score and make a new one
                self.score += 1
                self.canvas.delete(self.scoretext)
                self.scoretext = self.canvas.create_text(300, 580, fill='white', text=('Score: ' + str(self.score)), font='Times 10')
                self.asteroid.__init__(self.canvas, self.ship, self.difficulty)
                self.master.update()
                time.sleep(self.delay)
        self.endgame()
        # self.master.destroy()

    def endgame(self):  # Displays Game over message
        self.canvas.delete(self.scoretext)
        scorestring = 'Your score: ' + str(self.score)
        self.canvas.create_text(300, 200, fill='white', text='Game Over', font='Times 30')
        self.canvas.create_text(300, 400, fill='white', text=scorestring, font='Times 20')
        self.canvas.create_text(300, 500, fill='white', text='Please close this window before starting a new game', font='Times 16')


class Ship:

    def __init__(self, canvas, difficulty):  # Create the triangle on the canvas
        self.difficulty = difficulty
        self.rocketarray = []
        self.control_dict = {'Left': 1, 'Right': -1}  # dictionary that maps key events to turn directions
        self.turnspeed = 2 * self.difficulty.get()
        self.canvas = canvas
        self.heading = math.pi/2
        self.xtop = 300
        self.ytop = 275
        self.xleft = 290
        self.yleft = 300
        self.xright = 310
        self.yright = 300
        self.id = self.canvas.create_polygon((self.xleft, self.yleft, self.xright, self.yright,
                                             self.xtop, self.ytop), fill='white')
        self.isAlive = True
        self.xcenter, self.ycenter = self.centroid()

# The following centroid() and rotate() methods are modified versions of those found at:
# https://stackoverflow.com/questions/3408779/how-do-i-rotate-a-polygon-in-python-on-a-tkinter-canvas

    def centroid(self):   # return the center of the triangle to rotate around
        return 1 / 3 * (self.xleft + self.xright + self.xtop), 1 / 3 * (self.yleft + self.yright + self.ytop)

    def rotate(self, event=None):
        turn = self.control_dict[event.keysym] * self.turnspeed * math.pi/180
        self.heading += turn
        # ^figures out which direction to turn and how many degrees at a time to turn

        def _rot(x, y):  # rotates all the triangle points around the center, using trig magic
            x -= self.xcenter
            y -= self.ycenter
            _x = x * math.cos(turn) + y * math.sin(turn)
            _y = -x * math.sin(turn) + y * math.cos(turn)
            return _x + self.xcenter, _y + self.ycenter

        self.xleft, self.yleft = _rot(self.xleft, self.yleft)
        self.xright, self.yright = _rot(self.xright, self.yright)
        self.xtop, self.ytop = _rot(self.xtop, self.ytop)
        self.xcenter, self.ycenter = self.centroid()
        self.draw()  # update triangle with new rotated coordinates

    def draw(self):
        self.canvas.coords(self.id, self.xleft, self.yleft, self.xright, self.yright, self.xtop, self.ytop)
        for rocket in self.rocketarray:
            if not rocket.isAlive:
                self.rocketarray.remove(rocket)

    def shoot(self, event=None):
        if len(self.rocketarray) < 10:
            self.rocketarray += [Rocket(self.canvas, self.xtop, self.ytop, self.heading)]

    def kill(self):  # destroy the triangle, will cause game window to close
        self.isAlive = False


class CanvasCircle:
    def __init__(self, canvas, speed, radius):
        self.canvas = canvas
        self.isAlive = True
        self.speed = speed
        self.radius = radius

    def placecircle(self, x, y):
        return self.canvas.create_oval((x - self.radius, y - self.radius, x + self.radius, y + self.radius),
                                       fill='white')

    def move(self):
        self.x -= self.speed * self.xstep
        self.y -= self.speed * self.ystep
        self.draw()

    def draw(self):
        self.canvas.coords(self.id, (self.x - self.radius, self.y - self.radius,
                                     self.x + self.radius, self.y + self.radius))
        if self.x > 600 or self.x < 0 or self.y > 600 or self.y < 0:
            self.isAlive = False
            self.canvas.delete(self.id)


class Asteroid(CanvasCircle):
    def __init__(self, canvas, ship, difficulty):  # draw the circle and set variables
        super().__init__(canvas, (.3 * difficulty.get()), 15)
        self.difficulty = difficulty
        self.ship = ship

        self.x, self.y = self.create_coords(self.radius)
        self.id = super().placecircle(self.x, self.y)
        self.xship, self.yship = self.ship.centroid()
        self.xdist = self.x - self.xship
        self.ydist = self.y - self.yship
        self.xstep = self.xdist / 100
        self.ystep = self.ydist / 100

    def create_coords(self, size):  # long algorithm that will spawn asteroid on the edge of the screen
        a = random.randint(0, 1)
        if a == 0:  # left or right start
            b = random.randint(0, 1)
            if b == 0:  # left
                x = 0
                c = random.randint(0, 1)
                if c == 0:
                    y = random.randint(0, 200)
                else:
                    y = random.randint(400, (600 - size))
            else:  # right
                x = 600 - size
                c = random.randint(0, 1)
                if c == 0:
                    y = random.randint(0, 200)
                else:
                    y = random.randint(400, (600 - size))
        else:  # top or bottom start
            b = random.randint(0, 1)
            if b == 0:  # top
                y = 0
                c = random.randint(0, 1)
                if c == 0:
                    x = random.randint(0, 200)
                else:
                    x = random.randint(400, (600 - size))
            else:  # bottom
                y = 600 - size
                c = random.randint(0, 1)
                if c == 0:
                    x = random.randint(0, 200)
                else:
                    x = random.randint(400, (600 - size))
        return x, y

    def kill(self):  # destroys current circle, Game class will then create a new one
        self.canvas.delete(self.id)
        self.isAlive = False


class Rocket(CanvasCircle):  # Rocket comes from tip of triangle and moves in one direction
    def __init__(self, canvas, x, y, heading):
        super().__init__(canvas, 7, 4)
        self.x = x
        self.y = y
        self.heading = heading
        self.xstep = -math.cos(heading)
        self.ystep = math.sin(heading)
        self.id = super().placecircle(self.x, self.y)


def main():  # main method, starts the Menu and mainloop()
    root = Tk()
    root.geometry('600x600')
    Menu(root)
    root.mainloop()


if __name__ == '__main__':
    main()
